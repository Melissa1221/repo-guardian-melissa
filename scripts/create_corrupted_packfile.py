#!/usr/bin/env python3
"""Script to generate a corrupted packfile fixture for testing purposes."""
import os
import struct
import sys
from pathlib import Path

def create_corrupted_packfile(output_dir: Path):
    """Create a corrupted packfile and corresponding idx file.
    
    Args:
        output_dir: Directory to write the files to
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create the packfile with a valid header but corrupted content
    pack_path = output_dir / "pack-corrupt.pack"
    
    with open(pack_path, "wb") as f:
        # Write PACK signature
        f.write(b"PACK")
        
        # Write version (2) and object count (1)
        f.write(struct.pack(">II", 2, 1))
        
        # Write a fake blob entry header (type 3, size 12)
        # 0x30 = 0011 0000 (type 3 in high nibble, size 0 in low nibble)
        # 0x0C = 0000 1100 (size 12 with MSB unset)
        f.write(bytes([0x30, 0x0C]))
        
        # Start of valid zlib header but corrupted data
        # This will cause a more reliable CRC error
        f.write(b"\x78\x9c\x00\x00\x00\xFF\xFF")
        
        # Write a fake trailer (20 bytes SHA1)
        f.write(b"\x00" * 20)
    
    # Create a minimal idx file
    idx_path = output_dir / "pack-corrupt.idx"
    
    with open(idx_path, "wb") as f:
        # Write idx signature (\377tOc)
        f.write(b"\xff\x74\x4f\x63")
        
        # Write idx version (2)
        f.write(struct.pack(">I", 2))
        
        # Write a fake fanout table (256 entries, all zeros except last)
        fanout = [0] * 255 + [1]  # 1 object
        f.write(struct.pack(f">{'I' * 256}", *fanout))
        
        # Write a fake object hash (20 bytes)
        f.write(b"a" * 20)
        
        # Write a fake CRC (4 bytes)
        f.write(struct.pack(">I", 0))
        
        # Write a fake offset (4 bytes, pointing to position 12 in the packfile)
        f.write(struct.pack(">I", 12))
        
        # No large offsets in this simple example

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <output_directory>")
        sys.exit(1)
    
    output_dir = Path(sys.argv[1])
    create_corrupted_packfile(output_dir)
    print(f"Created corrupted packfile in {output_dir}")

if __name__ == "__main__":
    main() 