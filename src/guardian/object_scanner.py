"""Git object scanner module.

This module provides functionality to scan, read, and validate Git objects.
"""

import hashlib
import os
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple


@dataclass
class GitObject:
    """Representation of a Git object."""

    type: str
    size: int
    content: bytes
    hash: str


class GitObjectError(Exception):
    """Exception raised for errors in Git object operations."""

    pass


def read_loose(path: Path) -> GitObject:
    """Read a loose Git object from the given path.

    Args:
        path: Path to the Git object file

    Returns:
        GitObject instance with parsed data

    Raises:
        GitObjectError: If the object is invalid or corrupted
    """
    if not path.exists():
        raise GitObjectError(f"Object file not found: {path}")

    # Extract expected hash from path
    expected_hash = path.parent.name + path.name

    # Read binary content
    try:
        raw_data = path.read_bytes()
    except (IOError, PermissionError) as e:
        raise GitObjectError(f"Failed to read object file: {e}")

    # Decompress with zlib
    try:
        decompressed = zlib.decompress(raw_data)
    except zlib.error:
        raise GitObjectError(
            "Failed to decompress object data: CRC error or corrupted data"
        )

    # Parse header "type size\0"
    header_end = decompressed.find(b"\0")
    if header_end == -1:
        raise GitObjectError("Invalid object format: null byte separator not found")

    header = decompressed[:header_end].decode("utf-8", errors="replace")
    content = decompressed[header_end + 1 :]

    # Split header into type and size
    try:
        obj_type, size_str = header.split(" ", 1)
    except ValueError:
        raise GitObjectError(f"Invalid header format: {header}")

    # Validate object type
    valid_types = ["blob", "tree", "commit", "tag"]
    if obj_type not in valid_types:
        raise GitObjectError(f"Unknown object type: {obj_type}")

    # Parse size
    try:
        size = int(size_str)
    except ValueError:
        raise GitObjectError(f"Invalid size in header: {size_str}")

    # Verify size matches actual content size
    if len(content) != size:
        raise GitObjectError(
            f"Size mismatch: header says {size}, actual is {len(content)}"
        )

    # Verify hash matches path
    hasher = hashlib.sha1()
    hasher.update(obj_type.encode() + b" " + str(size).encode() + b"\0" + content)
    actual_hash = hasher.hexdigest()

    if actual_hash != expected_hash:
        raise GitObjectError(
            f"Hash mismatch: expected {expected_hash}, got {actual_hash}"
        )

    return GitObject(type=obj_type, size=size, content=content, hash=actual_hash)


# Git object types in packfiles are encoded as integers
PACK_OBJECT_TYPES = {
    1: "commit",
    2: "tree",
    3: "blob",
    4: "tag",
    6: "ofs-delta",
    7: "ref-delta",
}


@dataclass
class PackHeader:
    """Packfile header information."""

    signature: bytes
    version: int
    object_count: int


@dataclass
class PackEntry:
    """Information about an entry in a packfile."""

    offset: int
    type: str
    size: int
    data_offset: int
    base_hash: Optional[str] = None  # For ref-delta
    base_offset: Optional[int] = None  # For ofs-delta


def read_pack_header(pack_path: Path) -> PackHeader:
    """Read and validate a packfile header.

    Args:
        pack_path: Path to the packfile

    Returns:
        PackHeader with signature, version, and object count

    Raises:
        GitObjectError: If the packfile header is invalid
    """
    if not pack_path.exists():
        raise GitObjectError(f"Packfile not found: {pack_path}")

    try:
        with open(pack_path, "rb") as f:
            # Read 12-byte header: 4-byte signature, 4-byte version, 4-byte count
            header_data = f.read(12)
            if len(header_data) < 12:
                raise GitObjectError("Packfile header is truncated")

            signature = header_data[:4]
            if signature != b"PACK":
                raise GitObjectError(f"Invalid packfile signature: {signature}")

            version, object_count = struct.unpack(">II", header_data[4:12])
            if version != 2:
                raise GitObjectError(f"Unsupported packfile version: {version}")

            return PackHeader(
                signature=signature, version=version, object_count=object_count
            )
    except (IOError, PermissionError) as e:
        raise GitObjectError(f"Failed to read packfile: {e}")


def read_varint(data: bytes, offset: int) -> Tuple[int, int]:
    """Read a variable-length integer from packfile data.

    Args:
        data: Bytes containing the variable-length integer
        offset: Starting offset in the data

    Returns:
        Tuple of (value, new_offset)

    Raises:
        GitObjectError: If the varint is invalid or truncated
    """
    value = 0
    shift = 0
    current_offset = offset

    while True:
        if current_offset >= len(data):
            raise GitObjectError("Truncated varint in packfile")

        byte = data[current_offset]
        current_offset += 1

        value |= (byte & 0x7F) << shift
        shift += 7

        if not (byte & 0x80):
            break

    return value, current_offset


def read_pack_entry(pack_data: bytes, offset: int) -> Tuple[PackEntry, int]:
    """Read a single entry from packfile data.

    Args:
        pack_data: The full packfile data
        offset: Offset to start reading from

    Returns:
        Tuple of (PackEntry, new_offset)

    Raises:
        GitObjectError: If the entry is invalid or corrupted
    """
    if offset >= len(pack_data):
        raise GitObjectError(f"Invalid offset in packfile: {offset}")

    # Read the type and size from the first byte(s)
    try:
        byte = pack_data[offset]
        object_type = (byte >> 4) & 0x7
        size_part = byte & 0xF
        size = size_part
        shift = 4
        offset += 1

        # Read more bytes if the MSB is set (varint encoding)
        while byte & 0x80:
            if offset >= len(pack_data):
                raise GitObjectError("Truncated varint in packfile")

            byte = pack_data[offset]
            offset += 1
            size |= (byte & 0x7F) << shift
            shift += 7

            if not (byte & 0x80):
                break

        # Validate object type
        if object_type not in PACK_OBJECT_TYPES:
            raise GitObjectError(f"Unknown object type in packfile: {object_type}")

        type_name = PACK_OBJECT_TYPES[object_type]
        entry = PackEntry(
            offset=offset - 1,  # Original offset before reading
            type=type_name,
            size=size,
            data_offset=offset,
        )

        # Handle deltas
        if type_name == "ref-delta":
            # Next 20 bytes are the base object hash
            if offset + 20 > len(pack_data):
                raise GitObjectError("Truncated ref-delta in packfile")

            entry.base_hash = pack_data[offset : offset + 20].hex()
            offset += 20
            entry.data_offset = offset
        elif type_name == "ofs-delta":
            # Read a variable-length negative offset
            neg_offset, new_offset = read_varint(pack_data, offset)
            entry.base_offset = entry.offset - neg_offset
            offset = new_offset
            entry.data_offset = offset

        return entry, offset

    except (IndexError, struct.error) as e:
        raise GitObjectError(f"Failed to parse packfile entry: {e}")


def read_idx_file(idx_path: Path) -> Dict[str, int]:
    """Read a packfile index (.idx) file.

    Args:
        idx_path: Path to the .idx file

    Returns:
        Dictionary mapping object hashes to their offsets in the packfile

    Raises:
        GitObjectError: If the idx file is invalid or corrupted
    """
    if not idx_path.exists():
        raise GitObjectError(f"Index file not found: {idx_path}")

    try:
        with open(idx_path, "rb") as f:
            # Read and validate header
            header = f.read(8)
            if len(header) < 8:
                raise GitObjectError("Truncated idx file")

            signature, version = struct.unpack(">4sI", header)
            if signature != b"\xfftOc":
                raise GitObjectError(f"Invalid idx signature: {signature}")

            if version != 2:
                raise GitObjectError(f"Unsupported idx version: {version}")

            # Read fanout table (256 * 4 bytes)
            fanout = list(struct.unpack(">256I", f.read(256 * 4)))
            object_count = fanout[255]

            # Read object hashes (20 bytes each)
            hashes = []
            for _ in range(object_count):
                obj_hash = f.read(20).hex()
                hashes.append(obj_hash)

            # Skip CRCs (4 bytes each)
            f.seek(object_count * 4, os.SEEK_CUR)

            # Read offsets (4 bytes each)
            offsets = list(struct.unpack(f">{object_count}I", f.read(object_count * 4)))

            # Create hash -> offset mapping
            hash_to_offset = {}
            for i in range(object_count):
                hash_to_offset[hashes[i]] = offsets[i]

            return hash_to_offset

    except (IOError, PermissionError, struct.error) as e:
        raise GitObjectError(f"Failed to read idx file: {e}")


def extract_object_from_packfile(pack_path: Path, offset: int) -> GitObject:
    """Extract a Git object from a packfile at the given offset.

    Args:
        pack_path: Path to the packfile
        offset: Offset of the object in the packfile

    Returns:
        GitObject instance

    Raises:
        GitObjectError: If extraction fails
    """
    if not pack_path.exists():
        raise GitObjectError(f"Packfile not found: {pack_path}")

    try:
        with open(pack_path, "rb") as f:
            f.seek(offset)
            pack_data = f.read()

            # Read the pack entry
            entry, data_offset = read_pack_entry(pack_data, 0)

            # Read the compressed data
            compressed_data = pack_data[data_offset:]

            # Decompress the data
            try:
                decompressed = zlib.decompress(compressed_data)
            except zlib.error:
                raise GitObjectError(
                    f"Failed to decompress object data at offset {offset}: "
                    "CRC error or corrupted data"
                )

            # Handle delta objects
            if entry.type in ("ref-delta", "ofs-delta"):
                # Delta handling requires base object resolution
                # This implementation is simplified for clarity
                raise GitObjectError("Delta objects are not fully implemented yet")

            # Calculate the hash
            hasher = hashlib.sha1()
            header = f"{entry.type} {entry.size}\0".encode()
            hasher.update(header + decompressed)
            obj_hash = hasher.hexdigest()

            return GitObject(
                type=entry.type, size=entry.size, content=decompressed, hash=obj_hash
            )

    except (IOError, PermissionError) as e:
        raise GitObjectError(f"Failed to read packfile: {e}")


def find_object_in_packfiles(repo_path: Path, obj_hash: str) -> Optional[GitObject]:
    """Find a Git object in packfiles by its hash.

    Args:
        repo_path: Path to the Git repository
        obj_hash: Hash of the object to find

    Returns:
        GitObject if found, None otherwise

    Raises:
        GitObjectError: If there's an error reading packfiles
    """
    pack_dir = repo_path / "objects" / "pack"
    if not pack_dir.exists() or not pack_dir.is_dir():
        return None

    # Find all .idx files
    idx_files = list(pack_dir.glob("*.idx"))

    for idx_path in idx_files:
        try:
            # Read the index file
            hash_to_offset = read_idx_file(idx_path)

            # Check if our object is in this packfile
            if obj_hash in hash_to_offset:
                # Find corresponding packfile
                pack_path = idx_path.with_suffix(".pack")
                if not pack_path.exists():
                    continue

                # Extract the object
                offset = hash_to_offset[obj_hash]
                return extract_object_from_packfile(pack_path, offset)

        except GitObjectError:
            # Try the next packfile
            continue

    return None


def scan_packfile(pack_path: Path) -> List[PackEntry]:
    """Scan a packfile and return information about all entries.

    Args:
        pack_path: Path to the packfile

    Returns:
        List of PackEntry objects

    Raises:
        GitObjectError: If the packfile is corrupted
    """
    try:
        # Read packfile header
        header = read_pack_header(pack_path)

        # Read the entire packfile
        with open(pack_path, "rb") as f:
            # Skip the header (12 bytes)
            f.seek(12)
            pack_data = f.read()

        entries = []
        offset = 0

        # Read all entries
        for i in range(header.object_count):
            try:
                entry, next_offset = read_pack_entry(pack_data, offset)

                # Attempt to decompress the object data to validate it
                try:
                    # Extract the compressed data for this entry
                    compressed_data = pack_data[entry.data_offset : next_offset]
                    zlib.decompress(compressed_data)
                except zlib.error:
                    # Record the error and raise it immediately
                    raise GitObjectError(f"Invalid CRC at offset {offset + 12}")

                # Adjust offset to account for the 12-byte header
                entry.offset += 12
                entry.data_offset += 12
                if entry.base_offset is not None:
                    entry.base_offset += 12

                entries.append(entry)
                offset = next_offset
            except GitObjectError as e:
                # Immediately propagate the error
                raise GitObjectError(f"Invalid CRC at offset {offset + 12}: " f"{e}")

        return entries

    except (IOError, PermissionError) as e:
        raise GitObjectError(f"Failed to scan packfile: {e}")


def iter_objects(repo_path: Path) -> Iterator[GitObject]:
    """Iterate over all Git objects in a repository.

    Args:
        repo_path: Path to the Git repository

    Yields:
        GitObject instances

    Raises:
        GitObjectError: If the repository is invalid
    """
    if not repo_path.exists() or not repo_path.is_dir():
        raise GitObjectError(f"Invalid repository path: {repo_path}")

    objects_dir = repo_path / "objects"
    if not objects_dir.exists() or not objects_dir.is_dir():
        raise GitObjectError(f"Objects directory not found: {objects_dir}")

    # Scan loose objects
    for prefix_dir in objects_dir.iterdir():
        # Skip non-directories and special directories
        if not prefix_dir.is_dir() or prefix_dir.name in ("info", "pack"):
            continue

        # Check if this is a valid hex prefix
        is_valid_hex = all(c in "0123456789abcdef" for c in prefix_dir.name)
        if len(prefix_dir.name) != 2 or not is_valid_hex:
            continue

        # Scan objects in this prefix directory
        for obj_file in prefix_dir.iterdir():
            try:
                yield read_loose(obj_file)
            except GitObjectError:
                # Skip invalid objects
                continue

    # Scan packfiles
    pack_dir = objects_dir / "pack"
    if pack_dir.exists() and pack_dir.is_dir():
        for pack_file in pack_dir.glob("*.pack"):
            try:
                idx_file = pack_file.with_suffix(".idx")
                if not idx_file.exists():
                    continue

                hash_to_offset = read_idx_file(idx_file)

                for obj_hash, offset in hash_to_offset.items():
                    try:
                        yield extract_object_from_packfile(pack_file, offset)
                    except GitObjectError:
                        # Skip invalid objects
                        continue
            except GitObjectError:
                # Skip invalid packfiles
                continue
