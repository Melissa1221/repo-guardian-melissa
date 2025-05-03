"""Tests for the dag_builder module."""

from unittest.mock import Mock

import networkx as nx
from guardian.dag_builder import (
    build_graph,
    calculate_generation_numbers,
    find_heads,
    find_roots,
    get_commit_path,
    get_common_ancestor,
)
from guardian.object_scanner import GitObject


def test_build_graph_simple():
    """Test building a graph from a simple commit history."""
    # Mock commit objects
    commit1 = Mock(spec=GitObject, type='commit', hash='abc123')
    commit1.content = (
        b'tree treehash1\n'
        b'author Author <author@example.com> 1611111111 +0000\n'
        b'committer Committer <committer@example.com> 1611111111 +0000\n\n'
        b'Init commit'
    )

    commit2 = Mock(spec=GitObject, type='commit', hash='def456')
    commit2.content = (
        b'tree treehash2\n'
        b'parent abc123\n'
        b'author Author <author@example.com> 1622222222 +0000\n'
        b'committer Committer <committer@example.com> 1622222222 +0000\n\n'
        b'Second commit'
    )

    commit3 = Mock(spec=GitObject, type='commit', hash='ghi789')
    commit3.content = (
        b'tree treehash3\n'
        b'parent def456\n'
        b'author Author <author@example.com> 1633333333 +0000\n'
        b'committer Committer <committer@example.com> 1633333333 +0000\n\n'
        b'Third commit'
    )

    # Build graph
    graph = build_graph([commit1, commit2, commit3])

    # Assert graph structure
    assert isinstance(graph, nx.DiGraph)
    assert set(graph.nodes()) == {'abc123', 'def456', 'ghi789'}

    # Check edges (child -> parent)
    assert sorted(graph.edges()) == [('def456', 'abc123'), ('ghi789', 'def456')]

    # Check node attributes
    assert graph.nodes['abc123']['object'] == commit1
    assert graph.nodes['def456']['object'] == commit2
    assert graph.nodes['ghi789']['object'] == commit3


def test_build_graph_with_merge():
    """Test building a graph with a merge commit."""
    # Mock commit objects for main branch
    commit1 = Mock(spec=GitObject, type='commit', hash='abc123')
    commit1.content = (
        b'tree treehash1\n'
        b'author Author <author@example.com> 1611111111 +0000\n'
        b'committer Committer <committer@example.com> 1611111111 +0000\n\n'
        b'Init commit'
    )

    commit2 = Mock(spec=GitObject, type='commit', hash='def456')
    commit2.content = (
        b'tree treehash2\n'
        b'parent abc123\n'
        b'author Author <author@example.com> 1622222222 +0000\n'
        b'committer Committer <committer@example.com> 1622222222 +0000\n\n'
        b'Second commit'
    )

    # Mock commit objects for feature branch
    commit3 = Mock(spec=GitObject, type='commit', hash='jkl012')
    commit3.content = (
        b'tree treehash3\n'
        b'parent abc123\n'
        b'author Author <author@example.com> 1633333333 +0000\n'
        b'committer Committer <committer@example.com> 1633333333 +0000\n\n'
        b'Feature commit'
    )

    # Mock merge commit
    commit4 = Mock(spec=GitObject, type='commit', hash='mno345')
    commit4.content = (
        b'tree treehash4\n'
        b'parent def456\n'
        b'parent jkl012\n'
        b'author Author <author@example.com> 1644444444 +0000\n'
        b'committer Committer <committer@example.com> 1644444444 +0000\n\n'
        b'Merge feature'
    )

    # Build graph
    graph = build_graph([commit1, commit2, commit3, commit4])

    # Assert graph structure
    assert isinstance(graph, nx.DiGraph)
    assert set(graph.nodes()) == {'abc123', 'def456', 'jkl012', 'mno345'}

    # Check edges (child -> parent)
    expected_edges = [
        ('def456', 'abc123'),
        ('jkl012', 'abc123'),
        ('mno345', 'def456'),
        ('mno345', 'jkl012')
    ]
    assert sorted(graph.edges()) == sorted(expected_edges)

    # Check node attributes
    assert graph.nodes['abc123']['object'] == commit1
    assert graph.nodes['def456']['object'] == commit2
    assert graph.nodes['jkl012']['object'] == commit3
    assert graph.nodes['mno345']['object'] == commit4


def test_calculate_generation_numbers():
    """Test calculation of generation numbers."""
    # Create a simple graph structure
    # Root -> A -> B -> C
    #           \
    #            -> D -> E
    # Merge F -> C
    #         -> E
    graph = nx.DiGraph()

    # Add nodes
    graph.add_node('root')
    graph.add_node('A')
    graph.add_node('B')
    graph.add_node('C')
    graph.add_node('D')
    graph.add_node('E')
    graph.add_node('F')

    # Add edges (child -> parent)
    graph.add_edge('A', 'root')
    graph.add_edge('B', 'A')
    graph.add_edge('C', 'B')
    graph.add_edge('D', 'A')
    graph.add_edge('E', 'D')
    graph.add_edge('F', 'C')
    graph.add_edge('F', 'E')

    # Calculate generation numbers
    gen_numbers = calculate_generation_numbers(graph)

    # Assert expected generation numbers
    expected = {
        'root': 0,
        'A': 1,
        'B': 2,
        'D': 2,
        'C': 3,
        'E': 3,
        'F': 4
    }

    assert gen_numbers == expected


def test_find_roots():
    """Test finding root commits in the graph."""
    graph = nx.DiGraph()

    # Add nodes and edges
    graph.add_node('root1')
    graph.add_node('root2')  # Second disconnected root
    graph.add_node('A')
    graph.add_node('B')

    graph.add_edge('A', 'root1')
    graph.add_edge('B', 'A')

    # Find roots
    roots = find_roots(graph)

    # Assert results
    assert set(roots) == {'root1', 'root2'}


def test_find_heads():
    """Test finding head commits in the graph."""
    graph = nx.DiGraph()

    # Add nodes and edges
    graph.add_node('root')
    graph.add_node('A')
    graph.add_node('B')  # Head 1
    graph.add_node('C')  # Head 2

    graph.add_edge('A', 'root')
    graph.add_edge('B', 'A')
    graph.add_edge('C', 'A')

    # Find heads
    heads = find_heads(graph)

    # Assert results
    assert set(heads) == {'B', 'C'}


def test_get_commit_path():
    """Test getting path from commit to root."""
    graph = nx.DiGraph()

    # Create linear history
    graph.add_node('root')
    graph.add_node('A')
    graph.add_node('B')
    graph.add_node('C')

    graph.add_edge('A', 'root')
    graph.add_edge('B', 'A')
    graph.add_edge('C', 'B')

    # Get commit path
    path = get_commit_path(graph, 'C')

    # Assert results
    assert path == ['C', 'B', 'A', 'root']


def test_get_common_ancestor():
    """Test finding common ancestor of two commits."""
    graph = nx.DiGraph()

    # Create graph with common ancestor
    #       root
    #        |
    #        A
    #       / \
    #      B   C
    #     /     \
    #    D       E

    graph.add_node('root')
    graph.add_node('A')
    graph.add_node('B')
    graph.add_node('C')
    graph.add_node('D')
    graph.add_node('E')

    graph.add_edge('A', 'root')
    graph.add_edge('B', 'A')
    graph.add_edge('C', 'A')
    graph.add_edge('D', 'B')
    graph.add_edge('E', 'C')

    # Find common ancestor for D and E
    ancestor = get_common_ancestor(graph, 'D', 'E')

    # Assert results
    assert ancestor == 'A'
