"""Unit tests for the object scanner module."""

import hashlib
import zlib
from pathlib import Path

import pytest
from guardian.object_scanner import GitObjectError, read_loose


@pytest.fixture
def temp_git_object(tmp_path):
    """Create a valid Git object for testing."""
    # Create a simple blob object
    content = b"Hello, Git World!"
    obj_type = b"blob"
    size = len(content)

    # Format as Git object
    obj_data = obj_type + b" " + str(size).encode() + b"\0" + content

    # Calculate hash
    hasher = hashlib.sha1()
    hasher.update(obj_data)
    hash_val = hasher.hexdigest()

    # Create directory structure
    obj_dir = tmp_path / hash_val[:2]
    obj_dir.mkdir()
    obj_path = obj_dir / hash_val[2:]

    # Write compressed data
    compressed = zlib.compress(obj_data)
    obj_path.write_bytes(compressed)

    return {
        "path": obj_path,
        "hash": hash_val,
        "type": "blob",
        "size": size,
        "content": content
    }


class TestObjectScanner:
    """Test cases for the object scanner module."""

    def test_read_valid_object(self, temp_git_object):
        """Test reading a valid Git object."""
        # Given a valid Git object
        path = temp_git_object["path"]

        # When reading the object
        git_obj = read_loose(path)

        # Then the object should be correctly parsed
        assert git_obj.type == temp_git_object["type"]
        assert git_obj.size == temp_git_object["size"]
        assert git_obj.content == temp_git_object["content"]
        assert git_obj.hash == temp_git_object["hash"]

    def test_nonexistent_object(self):
        """Test reading a nonexistent object."""
        # Given a path that doesn't exist
        nonexistent_path = Path("/path/to/nonexistent/object")

        # When trying to read the object, it should raise an error
        with pytest.raises(GitObjectError, match="Object file not found"):
            read_loose(nonexistent_path)

    def test_corrupted_zlib_data(self, tmp_path):
        """Test reading a file with corrupted zlib data."""
        # Given a file with invalid zlib data
        obj_dir = tmp_path / "ab"
        obj_dir.mkdir()
        obj_path = obj_dir / "cdef1234567890abcdef1234567890abcdef12"
        obj_path.write_bytes(b"This is not valid zlib data")

        # When trying to read the object, it should raise an error
        with pytest.raises(GitObjectError, match="Failed to decompress object data"):
            read_loose(obj_path)

    def test_invalid_header_format(self, tmp_path):
        """Test reading an object with invalid header format."""
        # Given an object with invalid header format
        invalid_data = zlib.compress(b"invalid-header\0content")
        obj_dir = tmp_path / "ab"
        obj_dir.mkdir()
        obj_path = obj_dir / "cdef1234567890abcdef1234567890abcdef12"
        obj_path.write_bytes(invalid_data)

        # When trying to read the object, it should raise an error
        with pytest.raises(GitObjectError, match="Invalid header format"):
            read_loose(obj_path)

    def test_unknown_object_type(self, tmp_path):
        """Test reading an object with unknown type."""
        # Given an object with unknown type
        unknown_type_data = zlib.compress(b"unknown 12\0content")
        obj_dir = tmp_path / "ab"
        obj_dir.mkdir()
        obj_path = obj_dir / "cdef1234567890abcdef1234567890abcdef12"
        obj_path.write_bytes(unknown_type_data)

        # When trying to read the object, it should raise an error
        with pytest.raises(GitObjectError, match="Unknown object type"):
            read_loose(obj_path)

    def test_size_mismatch(self, tmp_path):
        """Test reading an object with size mismatch."""
        # Given an object with wrong size in header
        wrong_size_data = zlib.compress(b"blob 20\0too short content")
        obj_dir = tmp_path / "ab"
        obj_dir.mkdir()
        obj_path = obj_dir / "cdef1234567890abcdef1234567890abcdef12"
        obj_path.write_bytes(wrong_size_data)

        # When trying to read the object, it should raise an error
        with pytest.raises(GitObjectError, match="Size mismatch"):
            read_loose(obj_path)
