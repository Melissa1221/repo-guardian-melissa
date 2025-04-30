"""Git object scanner module.

This module provides functionality to scan, read, and validate Git objects.
"""

from pathlib import Path
from dataclasses import dataclass
import zlib
import hashlib
from typing import Optional, Tuple


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
        raise GitObjectError("Failed to decompress object data: CRC error or corrupted data")
    
    # Parse header "type size\0"
    header_end = decompressed.find(b'\0')
    if header_end == -1:
        raise GitObjectError("Invalid object format: null byte separator not found")
    
    header = decompressed[:header_end].decode('utf-8', errors='replace')
    content = decompressed[header_end + 1:]
    
    # Split header into type and size
    try:
        obj_type, size_str = header.split(' ', 1)
    except ValueError:
        raise GitObjectError(f"Invalid header format: {header}")
    
    # Validate object type
    valid_types = ['blob', 'tree', 'commit', 'tag']
    if obj_type not in valid_types:
        raise GitObjectError(f"Unknown object type: {obj_type}")
    
    # Parse size
    try:
        size = int(size_str)
    except ValueError:
        raise GitObjectError(f"Invalid size in header: {size_str}")
    
    # Verify size matches actual content size
    if len(content) != size:
        raise GitObjectError(f"Size mismatch: header says {size}, actual is {len(content)}")
    
    # Verify hash matches path
    hasher = hashlib.sha1()
    hasher.update(obj_type.encode() + b' ' + str(size).encode() + b'\0' + content)
    actual_hash = hasher.hexdigest()
    
    if actual_hash != expected_hash:
        raise GitObjectError(f"Hash mismatch: expected {expected_hash}, got {actual_hash}")
    
    return GitObject(type=obj_type, size=size, content=content, hash=actual_hash) 