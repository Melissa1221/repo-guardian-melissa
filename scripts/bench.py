#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

FIXTURES = [
    "fixtures/small.git",      # ~2 MiB
    "fixtures/medium.git",     # ~20 MiB
    "fixtures/large.git",      # ~200 MiB
    "fixtures/huge.git",       # ~1 GiB
]

def run_benchmark(command, repo_path, runs=3):
    """Run benchmark for a command on a repo path."""
    times = []
    for _ in range(runs):
        start = time.time()
        subprocess.run(command.split() + [repo_path],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE)
        times.append(time.time() - start)
    return sum(times) / len(times)  # Average

results = []
for repo in FIXTURES:
    repo_size = Path(repo).stat().st_size / (1024 * 1024)  # Size in MiB

    # Run guardian
    guardian_time = run_benchmark("guardian scan", repo)

    # Run git fsck
    fsck_time = run_benchmark("git fsck", repo)

    results.append({
        "Repository": repo,
        "Size (MiB)": repo_size,
        "Guardian (s)": guardian_time,
        "Git fsck (s)": fsck_time,
        "Ratio": guardian_time / fsck_time
    })

# Generate table
df = pd.DataFrame(results)
print(df.to_markdown(index=False))

# Generate plot
plt.figure(figsize=(10, 6))
plt.bar(df["Repository"], df["Guardian (s)"], label="Guardian")
plt.bar(df["Repository"], df["Git fsck (s)"], alpha=0.7, label="Git fsck")
plt.xlabel("Repository")
plt.ylabel("Time (seconds)")
plt.title("Performance Comparison: Guardian vs Git fsck")
plt.legend()
plt.tight_layout()
plt.savefig("docs/img/benchmark.png")
