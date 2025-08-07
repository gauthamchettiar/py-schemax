"""Utility functions for py-schemax."""

import sys
from typing import List

from xxhash import xxh3_64


def accept_file_paths_as_stdin(file_paths: List[str]) -> List[str]:
    """Accept file paths from standard input."""
    if not file_paths and not sys.stdin.isatty():
        try:
            file_paths = [line.strip() for line in sys.stdin if line.strip()]
        except (EOFError, KeyboardInterrupt):
            # Handle cases where stdin is not available or interrupted
            file_paths = []
    return file_paths


def get_hash_of_file(file_path: str) -> str:
    """Get a hash of the file content."""
    hasher = xxh3_64()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()
