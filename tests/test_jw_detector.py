"""Tests for the jw_detector module."""

from unittest.mock import patch

import networkx as nx
from guardian.jw_detector import (
    calculate_path_fingerprint,
    find_potential_rewrites,
    is_rewrite,
    path_similarity,
)


def test_path_similarity():
    """Test calculation of path similarity."""
    # Test identical paths
    path_a = ["abc123", "def456", "ghi789"]
    path_b = ["abc123", "def456", "ghi789"]
    assert path_similarity(path_a, path_b) == 1.0

    # Test completely different paths
    path_c = ["aaa111", "bbb222", "ccc333"]
    similarity = path_similarity(path_a, path_c)
    assert 0.0 <= similarity < 0.5  # Very low similarity

    # Test similar but not identical paths
    path_d = ["abc123", "def456", "xyz789"]  # Only last element differs
    similarity = path_similarity(path_a, path_d)
    assert 0.8 <= similarity < 1.0  # High similarity


def test_is_rewrite():
    """Test detection of rewritten history."""
    # Test identical paths (not rewrite)
    path_a = ["abc123", "def456", "ghi789"]
    path_b = ["abc123", "def456", "ghi789"]
    assert is_rewrite(path_a, path_b) is True  # 100% similarity

    # Test completely different paths (not rewrite)
    path_c = ["aaa111", "bbb222", "ccc333"]
    assert is_rewrite(path_a, path_c) is False  # Low similarity

    # Test similar paths with different threshold
    path_d = ["abc123", "def456", "xyz789"]

    # Should be a rewrite with lower threshold
    assert is_rewrite(path_a, path_d, threshold=0.8) is True

    # May not be a rewrite with higher threshold
    result_high_threshold = is_rewrite(path_a, path_d, threshold=0.99)
    assert result_high_threshold is False

    # Test empty paths
    assert is_rewrite([], path_a) is False
    assert is_rewrite(path_a, []) is False
    assert is_rewrite([], []) is False


@patch("guardian.jw_detector.get_commit_path")
def test_calculate_path_fingerprint(mock_get_path):
    """Test calculation of path fingerprint."""
    # Setup mock
    mock_get_path.return_value = ["abc123", "def456", "ghi789"]

    # Create test graph
    graph = nx.DiGraph()
    graph.add_node("abc123")

    # Call function
    fingerprint = calculate_path_fingerprint(graph, "abc123")

    # Verify result
    assert fingerprint == ["abc123", "def456", "ghi789"]
    mock_get_path.assert_called_once_with(graph, "abc123")


@patch("guardian.jw_detector.calculate_path_fingerprint")
@patch("guardian.dag_builder.find_heads")
def test_find_potential_rewrites(mock_find_heads, mock_calc_fingerprint):
    """Test finding potential history rewrites."""
    # Setup mocks
    mock_find_heads.return_value = ["head1", "head2", "head3"]

    # Mock different path fingerprints
    def mock_fingerprint(graph, commit):
        if commit == "head1":
            return ["head1", "middle1", "root"]
        elif commit == "head2":
            return ["head2", "middle2", "root"]
        elif commit == "head3":
            # Similar to head1 (potential rewrite)
            return ["head3", "middle1", "root"]
        return []

    mock_calc_fingerprint.side_effect = mock_fingerprint

    # Create test graph
    graph = nx.DiGraph()
    for node in ["head1", "head2", "head3", "middle1", "middle2", "root"]:
        graph.add_node(node)

    # Call function
    results = find_potential_rewrites(graph)

    # Verify results
    assert len(results) > 0

    # Check that we have a result with head1 and head3
    found = False
    for h1, h3, sim in results:
        if {h1, h3} == {"head1", "head3"}:
            found = True
            assert sim > 0.92
            break

    assert found, "Expected to find a match between head1 and head3"
