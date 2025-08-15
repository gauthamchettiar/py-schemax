"""Utility functions for py-schemax."""

import sys
from typing import List

from xxhash import xxh3_64

from py_schemax.schema.validation import ValidationOutputSchema


def accept_file_paths_as_stdin(file_paths: List[str]) -> List[str]:
    """Accept file paths from standard input."""
    if not file_paths and not sys.stdin.isatty():
        try:
            file_paths = [
                line.strip() for line in sys.stdin.read().split("\n") if line.strip()
            ]
        except (EOFError, KeyboardInterrupt):  # pragma: no cover
            file_paths = []
    return file_paths


def merge_validation_outputs(
    *outputs: ValidationOutputSchema,
) -> ValidationOutputSchema:
    """Merge multiple validation outputs into one."""
    file_path = ""
    valid = True
    error_count = 0
    errors = []

    for output in outputs:
        file_path = file_path if file_path != "" else output["file_path"]
        valid = valid and output["valid"]
        error_count += output["error_count"]
        errors.extend(output["errors"])

    return {
        "file_path": file_path,
        "valid": valid,
        "error_count": error_count,
        "errors": errors,
    }
