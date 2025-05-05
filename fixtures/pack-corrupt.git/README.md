# Corrupted Packfile Fixture

This is a minimal Git repository with a corrupted packfile for testing purposes.

## Contents

- `.git/objects/pack/pack-corrupt.pack`: A packfile with corrupted CRC
- `.git/objects/pack/pack-corrupt.idx`: The corresponding index file

## Corruption Details

The packfile has been intentionally corrupted with a CRC error at a specific offset.
This fixture is used for testing the error detection and reporting capabilities of
the Repo-Guardian tool.

## Usage

This fixture is used in BDD tests to verify the behavior of the Repo-Guardian tool
when encountered with a corrupted packfile.
