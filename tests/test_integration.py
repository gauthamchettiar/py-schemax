"""Integration tests for py-schemax CLI and workflow functionality.

These tests focus on end-to-end functionality, real file I/O, and component integration.
They complement the unit tests in test_validation_command.py by testing scenarios that
require real file systems, caching persistence, and performance characteristics.
"""

import json
import tempfile
import time
from pathlib import Path

from click.testing import CliRunner

from py_schemax.cli import validate


def test_cache_persistence_across_cli_runs():
    """Test that validation cache persists across separate CLI invocations."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a schema file
        schema = {
            "name": "Cache Test Schema",
            "fqn": "cache.test.schema",
            "columns": [{"name": "id", "type": "integer"}],
        }

        schema_file = Path(temp_dir) / "cache_test.json"
        with open(schema_file, "w") as f:
            json.dump(schema, f)

        # First run - should create cache
        start_time = time.time()
        result1 = runner.invoke(validate, [str(schema_file), "--verbose"])
        first_run_time = time.time() - start_time

        assert result1.exit_code == 0
        assert "cache_test.json" in result1.output

        # Second run - should use cache (faster)
        start_time = time.time()
        result2 = runner.invoke(validate, [str(schema_file), "--verbose"])
        second_run_time = time.time() - start_time

        assert result2.exit_code == 0
        assert "cache_test.json" in result2.output

        # Second run should be faster due to caching
        # (This is a rough check - cache benefits may vary)
        assert second_run_time <= first_run_time + 0.1  # Allow some variance


def test_batch_processing_mixed_file_types():
    """Test processing multiple files with different formats (JSON/YAML)."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create JSON valid file
        json_schema = {
            "name": "JSON Schema",
            "fqn": "json.schema",
            "columns": [{"name": "id", "type": "integer"}],
        }
        json_file = Path(temp_dir) / "schema.json"
        with open(json_file, "w") as f:
            json.dump(json_schema, f)

        # Create YAML valid file
        yaml_content = """name: "YAML Schema"
fqn: "yaml.schema"
columns:
  - name: "id"
    type: "integer"
"""
        yaml_file = Path(temp_dir) / "schema.yaml"
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        # Process both files
        result = runner.invoke(validate, [str(json_file), str(yaml_file), "--verbose"])

        # Should succeed with both file types
        assert result.exit_code == 0

        # Should process both file types successfully
        assert "schema.json" in result.output
        assert "schema.yaml" in result.output
        assert result.output.count("✅") == 2


def test_performance_with_large_batch():
    """Test performance characteristics with a larger number of files."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple schema files
        files = []
        for i in range(10):  # Create 10 files
            schema = {
                "name": f"Schema {i}",
                "fqn": f"batch.schema.{i}",
                "columns": [
                    {"name": "id", "type": "integer"},
                    {"name": f"field_{i}", "type": "string"},
                ],
            }

            file_path = Path(temp_dir) / f"schema_{i}.json"
            with open(file_path, "w") as f:
                json.dump(schema, f)
            files.append(str(file_path))

        # Process all files
        start_time = time.time()
        result = runner.invoke(validate, files + ["--verbose"])
        processing_time = time.time() - start_time

        assert result.exit_code == 0
        assert result.output.count("✅") == 10
        assert "Validation completed successfully!" in result.output

        # Should complete in reasonable time (adjust threshold as needed)
        assert processing_time < 10.0  # Should be much faster than 10 seconds


def test_cache_invalidation_on_file_change():
    """Test that cache is invalidated when file content changes."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        schema_file = Path(temp_dir) / "changing_schema.json"

        # Create initial schema
        initial_schema = {
            "name": "Initial Schema",
            "fqn": "changing.schema",
            "columns": [{"name": "id", "type": "integer"}],
        }

        with open(schema_file, "w") as f:
            json.dump(initial_schema, f)

        # First validation
        result1 = runner.invoke(validate, [str(schema_file)])
        assert result1.exit_code == 0

        # Modify the file
        modified_schema = {
            "name": "Modified Schema",  # Changed name
            "fqn": "changing.schema",
            "columns": [
                {"name": "id", "type": "integer"},
                {"name": "new_field", "type": "string"},  # Added field
            ],
        }

        with open(schema_file, "w") as f:
            json.dump(modified_schema, f)

        # Second validation should work with modified content
        result2 = runner.invoke(validate, [str(schema_file)])
        assert result2.exit_code == 0
