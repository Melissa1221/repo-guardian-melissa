#!/usr/bin/env python3
"""Script to create corrupted Git objects for testing."""

import zlib
from pathlib import Path


def create_corrupt_blob():
    """Create a corrupted blob object."""
    # Create base directories
    base_dir = Path("fixtures/corrupt-blob.git/objects")
    base_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create corrupted zlib data
    (base_dir / "ab").mkdir(exist_ok=True)
    corrupt_path = base_dir / "ab" / "cdef1234567890abcdef1234567890abcdef12"

    content = b"This is a corrupted blob object"
    header = b"blob " + str(len(content)).encode() + b"\0"
    full_data = header + content

    # Compress the data
    compressed = zlib.compress(full_data)
    # Corrupt the last few bytes to cause CRC errors
    corrupted = compressed[:-5] + b"XXXXX"

    with open(corrupt_path, "wb") as f:
        f.write(corrupted)

    # 2. Create invalid header object
    (base_dir / "cd").mkdir(exist_ok=True)
    invalid_header_path = base_dir / "cd" / "ef1234567890abcdef1234567890abcdef1234"

    # Missing the size part in header
    invalid_header = b"blob\0This is missing the size in header"
    invalid_compressed = zlib.compress(invalid_header)

    with open(invalid_header_path, "wb") as f:
        f.write(invalid_compressed)

    # 3. Create size mismatch object
    (base_dir / "ef").mkdir(exist_ok=True)
    size_mismatch_path = base_dir / "ef" / "0123456789abcdef0123456789abcdef012345"

    # Size is too large
    content = b"This content is smaller than declared"
    wrong_size = len(content) + 100  # Declare a size 100 bytes larger
    size_mismatch_header = b"blob " + str(wrong_size).encode() + b"\0"
    size_mismatch_data = size_mismatch_header + content
    size_mismatch_compressed = zlib.compress(size_mismatch_data)

    with open(size_mismatch_path, "wb") as f:
        f.write(size_mismatch_compressed)

    print("Created corrupted Git objects in fixtures/corrupt-blob.git/objects/")


if __name__ == "__main__":
    create_corrupt_blob()
