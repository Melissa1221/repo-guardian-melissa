"""Additional unit tests for the object scanner module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from guardian.object_scanner import (
    GitObjectError,
    extract_object_from_packfile,
    find_object_in_packfiles,
    iter_objects,
    read_idx_file,
)


class TestObjectScannerAdditional:
    """Additional tests for the object scanner module."""

    def test_read_idx_file(self, tmp_path):
        """Test reading a valid idx file."""
        # Create a minimal fake idx file
        idx_path = tmp_path / "test.idx"

        with open(idx_path, "wb") as f:
            # Header: signature + version 2
            f.write(b"\xff\x74\x4f\x63" + (2).to_bytes(4, byteorder="big"))

            # Fanout table: 255 zeros followed by 1
            fanout = bytes([0] * 4 * 255) + (1).to_bytes(4, byteorder="big")
            f.write(fanout)

            # Object entries: one SHA-1 hash
            test_hash = b"a" * 20
            f.write(test_hash)

            # CRC32: one entry
            f.write((0).to_bytes(4, byteorder="big"))

            # Offsets: one entry
            test_offset = 12345
            f.write(test_offset.to_bytes(4, byteorder="big"))

        # When reading the idx file
        hash_to_offset = read_idx_file(idx_path)

        # Then it should parse the entries correctly
        assert len(hash_to_offset) == 1
        assert "61" * 20 in hash_to_offset  # "a" in hex is 61
        assert hash_to_offset["61" * 20] == 12345

    def test_read_idx_file_nonexistent(self):
        """Test reading a nonexistent idx file."""
        # Given a path that doesn't exist
        nonexistent_path = Path("/nonexistent/path.idx")

        # When trying to read the idx file, it should raise an error
        with pytest.raises(GitObjectError, match="Index file not found"):
            read_idx_file(nonexistent_path)

    def test_read_idx_file_corrupted(self, tmp_path):
        """Test reading a corrupted idx file."""
        # Create a corrupted idx file
        idx_path = tmp_path / "corrupted.idx"

        with open(idx_path, "wb") as f:
            f.write(b"This is not a valid idx file")

        # When trying to read the idx file, it should raise an error
        with pytest.raises(GitObjectError):
            read_idx_file(idx_path)

    @patch("guardian.object_scanner.read_pack_entry")
    @patch("guardian.object_scanner.zlib.decompress")
    def test_extract_object_from_packfile(
        self, mock_decompress, mock_read_entry, tmp_path
    ):
        """Test extracting an object from a packfile."""
        # Create a fake packfile
        pack_path = tmp_path / "test.pack"
        with open(pack_path, "wb") as f:
            f.write(b"Fake packfile content")

        # Mock read_pack_entry to return a blob entry
        mock_entry = MagicMock()
        mock_entry.type = "blob"
        mock_entry.size = 12
        mock_entry.offset = 0
        mock_read_entry.return_value = (mock_entry, 100)

        # Mock zlib.decompress to return fake content
        mock_decompress.return_value = b"blob content"

        # When extracting the object
        obj = extract_object_from_packfile(pack_path, 42)

        # Then it should return a GitObject
        assert obj.type == "blob"
        assert obj.size == 12
        assert obj.content == b"blob content"

    def test_extract_object_from_packfile_nonexistent(self):
        """Test extracting an object from a nonexistent packfile."""
        # Given a path that doesn't exist
        nonexistent_path = Path("/nonexistent/path.pack")

        # When trying to extract the object, it should raise an error
        with pytest.raises(GitObjectError, match="Packfile not found"):
            extract_object_from_packfile(nonexistent_path, 0)

    @patch("guardian.object_scanner.read_idx_file")
    @patch("guardian.object_scanner.extract_object_from_packfile")
    def test_find_object_in_packfiles(self, mock_extract, mock_read_idx, tmp_path):
        """Test finding an object in packfiles."""
        # Create a fake repo with a packfile
        repo_path = tmp_path
        pack_dir = repo_path / "objects" / "pack"
        pack_dir.mkdir(parents=True)
        pack_path = pack_dir / "test.pack"
        with open(pack_path, "wb") as f:
            f.write(b"dummy")

        idx_path = pack_dir / "test.idx"
        with open(idx_path, "wb") as f:
            f.write(b"dummy")

        # Mock read_idx_file to return a hash -> offset mapping
        test_hash = "abcd" * 10
        mock_read_idx.return_value = {test_hash: 12}

        # Mock extract_object_from_packfile to return a GitObject
        mock_obj = MagicMock()
        mock_obj.hash = test_hash
        mock_extract.return_value = mock_obj

        # When finding the object
        obj = find_object_in_packfiles(repo_path, test_hash)

        # Then it should return the GitObject
        assert obj == mock_obj
        mock_read_idx.assert_called_once()
        mock_extract.assert_called_once_with(pack_path, 12)

    def test_find_object_in_packfiles_not_found(self, tmp_path):
        """Test finding a nonexistent object in packfiles."""
        # Create a fake repo with no packfiles
        repo_path = tmp_path
        pack_dir = repo_path / "objects" / "pack"
        pack_dir.mkdir(parents=True)

        # When finding a nonexistent object
        obj = find_object_in_packfiles(repo_path, "nonexistent")

        # Then it should return None
        assert obj is None

    @patch("guardian.object_scanner.read_loose")
    def test_iter_objects(self, mock_read_loose, tmp_path):
        """Test iterating over objects in a repository."""
        # Create a fake repo with some loose objects
        repo_path = tmp_path
        objects_dir = repo_path / "objects"
        objects_dir.mkdir()

        # Create a prefix directory
        prefix_dir = objects_dir / "ab"
        prefix_dir.mkdir()

        # Create some fake object files
        obj_file1 = prefix_dir / "cdef1234567890abcdef1234567890abcdef12"
        obj_file2 = prefix_dir / "0123456789abcdef0123456789abcdef01234"

        with open(obj_file1, "wb") as f:
            f.write(b"dummy1")

        with open(obj_file2, "wb") as f:
            f.write(b"dummy2")

        # Mock read_loose to return GitObjects
        mock_obj1 = MagicMock()
        mock_obj2 = MagicMock()
        mock_read_loose.side_effect = [mock_obj1, mock_obj2]

        # When iterating over objects
        objects = list(iter_objects(repo_path))

        # Then it should yield all objects
        assert len(objects) == 2
        assert mock_obj1 in objects
        assert mock_obj2 in objects

    def test_iter_objects_nonexistent_repo(self):
        """Test iterating over objects in a nonexistent repository."""
        # Given a path that doesn't exist
        nonexistent_path = Path("/nonexistent/repo")

        # When trying to iterate over objects, it should raise an error
        with pytest.raises(GitObjectError, match="Invalid repository path"):
            list(iter_objects(nonexistent_path))
