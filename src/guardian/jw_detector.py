"""Jaro-Winkler detector module.

This module provides functionality to detect rewritten Git history using
Jaro-Winkler distance.
"""

from typing import List, Tuple

import textdistance
from networkx import DiGraph

from guardian.dag_builder import get_commit_path


def calculate_path_fingerprint(graph: DiGraph, commit_sha: str) -> List[str]:
    """Calculate a fingerprint for the path from commit to root.

    Args:
        graph: DiGraph of commits
        commit_sha: Starting commit hash

    Returns:
        List of commit hashes from commit to root
    """
    return get_commit_path(graph, commit_sha)


def path_similarity(path_a: List[str], path_b: List[str]) -> float:
    """Calculate similarity between two commit paths using Jaro-Winkler.

    Args:
        path_a: First commit path
        path_b: Second commit path

    Returns:
        Similarity score between 0.0 and 1.0
    """
    # Convert paths to strings for comparison
    str_a = ''.join(path_a)
    str_b = ''.join(path_b)

    # Calculate Jaro-Winkler similarity
    return textdistance.jaro_winkler.normalized_similarity(str_a, str_b)


def is_rewrite(path_a: List[str], path_b: List[str], threshold: float = 0.92) -> bool:
    """Determine if two paths are potentially rewrites using Jaro-Winkler distance.

    Args:
        path_a: First commit path
        path_b: Second commit path
        threshold: Similarity threshold (default 0.92)

    Returns:
        True if similarity is at or above threshold, False otherwise
    """
    if not path_a or not path_b:
        return False

    similarity = path_similarity(path_a, path_b)
    return similarity >= threshold


def find_potential_rewrites(
    graph: DiGraph, threshold: float = 0.92
) -> List[Tuple[str, str, float]]:
    """Find potential history rewrites in the graph.

    Compares all head commits to find pairs with similar paths to root
    that could indicate rewritten history.

    Args:
        graph: DiGraph of commits
        threshold: Similarity threshold (default 0.92)

    Returns:
        List of tuples (commit1, commit2, similarity) for potential rewrites
    """
    from guardian.dag_builder import find_heads

    heads = find_heads(graph)
    results = []

    # Compare all pairs of heads
    for i, head1 in enumerate(heads):
        path1 = calculate_path_fingerprint(graph, head1)

        for head2 in heads[i+1:]:
            path2 = calculate_path_fingerprint(graph, head2)

            # Skip comparison if paths are identical (same branch)
            if path1 == path2:
                continue

            # Calculate similarity
            similarity = path_similarity(path1, path2)

            # Check if similarity is above threshold
            if similarity >= threshold:
                results.append((head1, head2, similarity))

    # Sort by similarity (highest first)
    results.sort(key=lambda x: x[2], reverse=True)
    return results
