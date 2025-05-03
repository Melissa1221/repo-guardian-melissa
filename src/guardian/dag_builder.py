"""DAG builder module.

This module provides functionality to build a directed acyclic graph from Git objects.
"""

from collections import deque
from typing import Dict, Iterable, List, Optional

from networkx import DiGraph

from guardian.object_scanner import GitObject


def _parse_commit_parents(commit_content: bytes) -> List[str]:
    """Parse parent commit hashes from commit content.

    Args:
        commit_content: Binary content of a commit object

    Returns:
        List of parent commit hashes
    """
    parents = []
    lines = commit_content.split(b'\n')

    for line in lines:
        if line.startswith(b'parent '):
            parent_hash = line[7:].decode('utf-8').strip()
            parents.append(parent_hash)
        elif (not line.startswith(b'tree ') and
              not line.startswith(b'author ') and
              not line.startswith(b'committer ')):
            # We've reached the commit message (after headers)
            break

    return parents


def build_graph(objects: Iterable[GitObject]) -> DiGraph:
    """Build a directed graph of commits from Git objects.

    Args:
        objects: Iterable of GitObject instances, expected to be commits

    Returns:
        DiGraph: A directed graph where:
            - Nodes are commit hashes
            - Edges connect commits to their parents
            - Node attributes include 'object' (original GitObject)

    Notes:
        In Git, the relationship direction is from child to parent,
        so edges in the graph point from a commit to its parent(s).
    """
    G = DiGraph()

    # Filter out non-commit objects
    commits = [obj for obj in objects if obj.type == 'commit']

    # Add all commits as nodes
    for commit in commits:
        G.add_node(commit.hash, object=commit)

    # Process each commit to find parents and add edges
    for commit in commits:
        parents = _parse_commit_parents(commit.content)
        for parent in parents:
            # Only add edge if parent exists in the graph
            if parent in G:
                G.add_edge(commit.hash, parent)

    return G


def calculate_generation_numbers(graph: DiGraph) -> Dict[str, int]:
    """Calculate generation numbers for all commits in the graph.

    The generation number (GN) of a commit is defined as:
    - GN = 0 for commits with no parents (root commits)
    - GN = max(GN of all parents) + 1 for all other commits

    Args:
        graph: DiGraph of commits

    Returns:
        Dict mapping commit hash to its generation number
    """
    # Find roots (commits with no parents)
    roots = find_roots(graph)

    # Initialize generation numbers
    gen_numbers = {}

    # Initialize with roots (GN = 0)
    for root in roots:
        gen_numbers[root] = 0

    # BFS traversal to process commits in topological order
    visited = set(roots)
    queue = deque(roots)

    while queue:
        current = queue.popleft()

        # Find children (commits that have current as parent)
        children = [child for child in graph if current in graph.successors(child)]

        for child in children:
            # Check if all parents of child have been processed
            parents = list(graph.successors(child))
            if all(parent in gen_numbers for parent in parents):
                # Calculate generation number as max of parents + 1
                child_gen = max(gen_numbers[parent] for parent in parents) + 1
                gen_numbers[child] = child_gen

                if child not in visited:
                    visited.add(child)
                    queue.append(child)

    return gen_numbers


def find_roots(graph: DiGraph) -> List[str]:
    """Find root commits in the graph (commits with no parents).

    Args:
        graph: DiGraph of commits

    Returns:
        List of commit hashes that are roots
    """
    roots = []
    for node in graph.nodes():
        # A root has no successors (parents in Git's model)
        if len(list(graph.successors(node))) == 0:
            roots.append(node)

    return roots


def find_heads(graph: DiGraph) -> List[str]:
    """Find head commits in the graph (commits with no children).

    Args:
        graph: DiGraph of commits

    Returns:
        List of commit hashes that are heads (tips of branches)
    """
    heads = []
    for node in graph.nodes():
        # A head has no predecessors (children in Git's model)
        if len(list(graph.predecessors(node))) == 0:
            heads.append(node)

    return heads


def get_commit_path(graph: DiGraph, commit_hash: str) -> List[str]:
    """Get the path from a commit to the root.

    Args:
        graph: DiGraph of commits
        commit_hash: Starting commit hash

    Returns:
        List of commit hashes from the given commit to a root
        If multiple paths exist, returns the shortest one
    """
    if commit_hash not in graph:
        return []

    # Use BFS to find shortest path to a root
    visited = {commit_hash}
    queue = deque([(commit_hash, [commit_hash])])

    while queue:
        current, path = queue.popleft()

        # Check if current is a root (no parents)
        parents = list(graph.successors(current))
        if not parents:
            return path

        # Add all parents to the queue
        for parent in parents:
            if parent not in visited:
                visited.add(parent)
                queue.append((parent, path + [parent]))

    return []  # Should not reach here if graph is valid


def get_common_ancestor(graph: DiGraph, commit1: str, commit2: str) -> Optional[str]:
    """Find the nearest common ancestor of two commits.

    Args:
        graph: DiGraph of commits
        commit1: First commit hash
        commit2: Second commit hash

    Returns:
        Hash of the nearest common ancestor, or None if no common ancestor found
    """
    if commit1 not in graph or commit2 not in graph:
        return None

    # Get all ancestors of commit1
    ancestors1 = set()
    queue = deque([commit1])
    while queue:
        current = queue.popleft()
        ancestors1.add(current)
        for parent in graph.successors(current):
            if parent not in ancestors1:
                queue.append(parent)

    # BFS from commit2 until we find a common ancestor
    visited = set()
    queue = deque([(commit2, 0)])  # (commit, distance)

    common_ancestors = []
    min_distance = float('inf')

    while queue:
        current, distance = queue.popleft()

        if distance > min_distance and common_ancestors:
            # We've already found closer common ancestors
            break

        if current in ancestors1:
            common_ancestors.append((current, distance))
            min_distance = distance
            # Don't break here - continue to find all at this distance

        visited.add(current)
        for parent in graph.successors(current):
            if parent not in visited:
                queue.append((parent, distance + 1))

    if not common_ancestors:
        return None

    # Return the common ancestor with minimum distance
    common_ancestors.sort(key=lambda x: x[1])  # Sort by distance
    return common_ancestors[0][0]
