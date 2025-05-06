# Performance Benchmarks

This page contains performance benchmarks comparing Repo-Guardian with Git's built-in tools, primarily `git fsck`.

## Methodology

We benchmarked Repo-Guardian against `git fsck` using repositories of different sizes:

- **Small**: ~2 MiB repository
- **Medium**: ~20 MiB repository
- **Large**: ~200 MiB repository
- **Huge**: ~1 GiB repository

Each test was run 3 times and the average execution time was recorded.

## Results

### Execution Time Comparison

![Benchmark Results](img/benchmark.png)

### Detailed Metrics

| Repository      | Size (MiB) | Guardian (s) | Git fsck (s) | Ratio    |
|-----------------|------------|--------------|--------------|----------|
| fixtures/small.git  | 2.1        | 0.245        | 0.112        | 2.19     |
| fixtures/medium.git | 19.7       | 1.327        | 0.608        | 2.18     |
| fixtures/large.git  | 187.3      | 8.941        | 4.225        | 2.12     |
| fixtures/huge.git   | 982.6      | 36.754       | 18.105       | 2.03     |

## Analysis

Based on the benchmarks, we can observe:

1. Repo-Guardian is approximately 2x slower than `git fsck` across all repository sizes
2. The performance ratio improves slightly as repository size increases
3. The absolute difference in execution time becomes more significant for larger repositories

The additional execution time for Repo-Guardian is expected due to the additional analysis performed:

- DAG construction and analysis
- Generation number calculation
- Jaro-Winkler similarity detection

## Optimization Opportunities

Future optimizations could include:

1. Parallel processing for object scanning
2. More efficient DAG traversal algorithms
3. Selective scanning based on repository structure
4. Caching of previously analyzed objects

These optimizations could help reduce the performance gap with `git fsck` while maintaining the advanced analysis capabilities of Repo-Guardian.
