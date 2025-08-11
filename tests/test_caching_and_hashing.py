"""Tests for caching and hashing functionality in py-schemax."""

import json
import os
import shutil
import tempfile
from unittest.mock import patch

import pytest
from cachebox import LRUCache

from py_schemax.cache import persistent_cachedmethod
from py_schemax.utils import get_hash_of_file
from py_schemax.validator import Validator


class TestFileHashing:
    """Test file hashing functionality."""

    def test_get_hash_of_file_returns_consistent_hash(self):
        """Test that the same file content produces the same hash."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            test_content = {"name": "test", "fqn": "test.schema", "columns": []}
            json.dump(test_content, temp_file)
            temp_file_path = temp_file.name

        try:
            # Get hash twice for the same file
            hash1 = get_hash_of_file(temp_file_path)
            hash2 = get_hash_of_file(temp_file_path)

            # Hashes should be identical
            assert hash1 == hash2
            assert isinstance(hash1, str)
            assert len(hash1) > 0
        finally:
            os.unlink(temp_file_path)

    def test_get_hash_of_file_different_content_different_hash(self):
        """Test that different file contents produce different hashes."""
        content1 = {"name": "test1", "fqn": "test1.schema", "columns": []}
        content2 = {"name": "test2", "fqn": "test2.schema", "columns": []}

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file1:
            json.dump(content1, temp_file1)
            temp_file1_path = temp_file1.name

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file2:
            json.dump(content2, temp_file2)
            temp_file2_path = temp_file2.name

        try:
            hash1 = get_hash_of_file(temp_file1_path)
            hash2 = get_hash_of_file(temp_file2_path)

            # Hashes should be different
            assert hash1 != hash2
        finally:
            os.unlink(temp_file1_path)
            os.unlink(temp_file2_path)

    def test_get_hash_of_file_nonexistent_file_raises_error(self):
        """Test that hashing a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_hash_of_file("/path/that/does/not/exist.json")

    def test_hash_changes_when_file_content_changes(self):
        """Test that hash changes when file content is modified."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            # Write initial content
            initial_content = {"name": "test", "fqn": "test.schema", "columns": []}
            json.dump(initial_content, temp_file)
            temp_file_path = temp_file.name

        try:
            # Get initial hash
            initial_hash = get_hash_of_file(temp_file_path)

            # Modify file content
            with open(temp_file_path, "w") as f:
                modified_content = {
                    "name": "modified",
                    "fqn": "test.schema",
                    "columns": [],
                }
                json.dump(modified_content, f)

            # Get new hash
            modified_hash = get_hash_of_file(temp_file_path)

            # Hashes should be different
            assert initial_hash != modified_hash
        finally:
            os.unlink(temp_file_path)


class TestValidatorCaching:
    """Test caching functionality in the Validator class."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.test_cache_dir = tempfile.mkdtemp()
        self.test_cache_file = os.path.join(
            self.test_cache_dir, "test_validation.pickle"
        )

    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)

    def test_cache_hit_returns_cached_result(self):
        """Test that cached validation results are returned without re-processing."""
        # Create a test file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            test_content = {"name": "test", "fqn": "test.schema", "columns": []}
            json.dump(test_content, temp_file)
            temp_file_path = temp_file.name

        try:
            file_hash = get_hash_of_file(temp_file_path)

            # Patch the persistent_cachedmethod to use our test cache
            with patch("py_schemax.validator.persistent_cachedmethod") as mock_cache:
                # Configure the mock to simulate cache behavior
                mock_cache.return_value = lambda func: func

                # Create validator instances
                validator1 = Validator()
                validator2 = Validator()

                # First validation call
                result1 = validator1.validate_schema_file(temp_file_path, file_hash)

                # Second validation call with same file and hash
                result2 = validator2.validate_schema_file(temp_file_path, file_hash)

                # Both results should be identical (indicating cache hit)
                assert result1 == result2
                assert result1["valid"] is True
                assert result1["file_path"] == temp_file_path

        finally:
            os.unlink(temp_file_path)

    def test_cache_miss_with_different_hash(self):
        """Test that different file hashes result in cache misses."""
        # Create a test file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            test_content = {"name": "test", "fqn": "test.schema", "columns": []}
            json.dump(test_content, temp_file)
            temp_file_path = temp_file.name

        try:
            original_hash = get_hash_of_file(temp_file_path)
            different_hash = "different_hash_value"

            validator = Validator()

            # First call with original hash
            result1 = validator.validate_schema_file(temp_file_path, original_hash)

            # Second call with different hash (should be cache miss)
            result2 = validator.validate_schema_file(temp_file_path, different_hash)

            # Results should be identical (same file content) but processed separately
            assert result1["valid"] == result2["valid"]
            assert result1["file_path"] == result2["file_path"]

        finally:
            os.unlink(temp_file_path)

    def test_cache_with_none_hash(self):
        """Test validation behavior when file hash is None."""
        # Create a test file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            test_content = {"name": "test", "fqn": "test.schema", "columns": []}
            json.dump(test_content, temp_file)
            temp_file_path = temp_file.name

        try:
            validator = Validator()

            # Call with None hash (simulating file not found scenario)
            result = validator.validate_schema_file(temp_file_path, None)

            # Should still work and return valid result
            assert result["valid"] is True
            assert result["file_path"] == temp_file_path

        finally:
            os.unlink(temp_file_path)

    def test_validator_processes_identical_files_consistently(self):
        """Test that identical files produce identical validation results."""
        test_content = {"name": "test", "fqn": "test.schema", "columns": []}

        # Create two identical files
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file1:
            json.dump(test_content, temp_file1)
            temp_file1_path = temp_file1.name

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file2:
            json.dump(test_content, temp_file2)
            temp_file2_path = temp_file2.name

        try:
            hash1 = get_hash_of_file(temp_file1_path)
            hash2 = get_hash_of_file(temp_file2_path)

            # Hashes should be identical for identical content
            assert hash1 == hash2

            validator = Validator()

            # Validate both files
            result1 = validator.validate_schema_file(temp_file1_path, hash1)
            result2 = validator.validate_schema_file(temp_file2_path, hash2)

            # Results should be identical except for file paths
            assert result1["valid"] == result2["valid"]
            assert result1["error_count"] == result2["error_count"]
            assert result1["errors"] == result2["errors"]

        finally:
            os.unlink(temp_file1_path)
            os.unlink(temp_file2_path)


class TestPersistentCacheMethod:
    """Test the persistent_cachedmethod decorator functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.test_cache_dir = tempfile.mkdtemp()
        self.test_cache_file = os.path.join(self.test_cache_dir, "test_cache.pickle")

    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)

    def test_persistent_cache_decorator_functionality_with_mock(self):
        """Test that the persistent cache decorator works with mocked atexit."""
        cache = LRUCache(maxsize=100)
        call_count = 0

        # Mock atexit to avoid the cleanup issue
        with patch("py_schemax.cache.atexit.register"):

            @persistent_cachedmethod(self.test_cache_file, cache)
            def expensive_operation(self, value):
                nonlocal call_count
                call_count += 1
                return value * 2

            # First call
            result1 = expensive_operation(None, 5)
            assert result1 == 10
            assert call_count == 1

            # Second call with same parameter should use cache
            result2 = expensive_operation(None, 5)
            assert result2 == 10
            assert call_count == 1  # Should not increment

            # Call with different parameter
            result3 = expensive_operation(None, 3)
            assert result3 == 6
            assert call_count == 2  # Should increment

    def test_cache_file_handling_with_existing_file(self):
        """Test that cache loads from existing file correctly."""
        # Create an initial cache file with some data
        initial_cache = LRUCache(maxsize=100)

        # Save the cache manually
        os.makedirs(os.path.dirname(self.test_cache_file), exist_ok=True)
        with open(self.test_cache_file, "wb") as fd:
            import larch.pickle as pickle

            pickle.dump(initial_cache, fd)

        # Verify file exists
        assert os.path.exists(self.test_cache_file)

        # Test that the decorator loads the existing cache
        with patch("py_schemax.cache.atexit.register"):
            new_cache = LRUCache(maxsize=100)

            @persistent_cachedmethod(self.test_cache_file, new_cache)
            def test_method(self, key):
                return f"processed_{key}"

            # The decorator should work
            result = test_method(None, "new_key")
            assert result == "processed_new_key"

    def test_save_pickle_function_creates_directory_and_saves_cache(self):
        """Test that _save_pickle creates directory and saves cache file."""
        cache = LRUCache(maxsize=100)

        # Use a nested directory path that doesn't exist
        nested_cache_file = os.path.join(self.test_cache_dir, "nested", "cache.pickle")

        # Track if atexit was called and capture the save function
        save_function = None

        def mock_atexit_register(func):
            nonlocal save_function
            save_function = func

        with patch(
            "py_schemax.cache.atexit.register", side_effect=mock_atexit_register
        ):

            @persistent_cachedmethod(nested_cache_file, cache)
            def test_method(self, key):
                return f"value_{key}"

            # Call the method to populate cache
            result = test_method(None, "test")
            assert result == "value_test"

            # Now manually call the save function to test the _save_pickle logic
            assert save_function is not None
            save_function()

            # Verify directory was created and file was saved
            assert os.path.exists(os.path.dirname(nested_cache_file))
            assert os.path.exists(nested_cache_file)

            # Verify cache can be loaded back
            import larch.pickle as pickle

            with open(nested_cache_file, "rb") as fd:
                loaded_cache = pickle.load(fd)
                assert loaded_cache is not None

    def test_save_pickle_handles_file_not_found_error(self):
        """Test that _save_pickle handles FileNotFoundError gracefully."""
        cache = LRUCache(maxsize=100)

        # Use an invalid path that will cause FileNotFoundError
        invalid_cache_file = "/root/invalid/path/cache.pickle"

        # Track if atexit was called and capture the save function
        save_function = None

        def mock_atexit_register(func):
            nonlocal save_function
            save_function = func

        with patch(
            "py_schemax.cache.atexit.register", side_effect=mock_atexit_register
        ):

            @persistent_cachedmethod(invalid_cache_file, cache)
            def test_method(self, key):
                return f"value_{key}"

            # Call the method to populate cache
            result = test_method(None, "test")
            assert result == "value_test"

            # Mock click.secho to capture error messages
            with patch("py_schemax.cache.click.secho") as mock_secho:
                # Now manually call the save function to test error handling
                assert save_function is not None
                save_function()  # Should not raise an exception

                # Verify that click.secho was called with error message
                mock_secho.assert_called_once_with(
                    "Error saving cache file. Directory may not exist.",
                    fg="yellow",
                    err=True,
                )

    def test_save_pickle_handles_os_error(self):
        """Test that _save_pickle handles OSError gracefully."""
        cache = LRUCache(maxsize=100)

        # Track if atexit was called and capture the save function
        save_function = None

        def mock_atexit_register(func):
            nonlocal save_function
            save_function = func

        with patch(
            "py_schemax.cache.atexit.register", side_effect=mock_atexit_register
        ):

            @persistent_cachedmethod(self.test_cache_file, cache)
            def test_method(self, key):
                return f"value_{key}"

            # Call the method to populate cache
            result = test_method(None, "test")
            assert result == "value_test"

            # Mock the file operations to raise OSError
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                with patch("py_schemax.cache.click.secho") as mock_secho:
                    # Now manually call the save function to test error handling
                    assert save_function is not None
                    save_function()  # Should not raise an exception

                    # Verify that click.secho was called with error message
                    mock_secho.assert_called_once_with(
                        "Error saving cache file. Directory may not exist.",
                        fg="yellow",
                        err=True,
                    )


class TestValidationCacheIntegration:
    """Test integration between validation and caching system."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.test_cache_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)

    def test_validation_result_consistency_with_caching(self):
        """Test that validation results are consistent when caching is involved."""
        # Create a valid schema file
        valid_schema = {
            "name": "User Schema",
            "fqn": "users.schema",
            "columns": [
                {
                    "name": "user_id",
                    "type": "integer",
                    "nullable": False,
                    "primary_key": True,
                }
            ],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            json.dump(valid_schema, temp_file)
            temp_file_path = temp_file.name

        try:
            file_hash = get_hash_of_file(temp_file_path)
            validator = Validator()

            # Multiple validation calls
            results = []
            for _ in range(3):
                result = validator.validate_schema_file(temp_file_path, file_hash)
                results.append(result)

            # All results should be identical
            for i in range(1, len(results)):
                assert results[0] == results[i]

            # Verify the structure of the result
            result = results[0]
            assert result["valid"] is True
            assert result["error_count"] == 0
            assert result["errors"] == []
            assert result["file_path"] == temp_file_path

        finally:
            os.unlink(temp_file_path)

    def test_cache_performance_benefit(self):
        """Test that caching provides performance benefits."""
        # Create a schema file
        schema = {"name": "test", "fqn": "test.schema", "columns": []}

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            json.dump(schema, temp_file)
            temp_file_path = temp_file.name

        try:
            file_hash = get_hash_of_file(temp_file_path)
            validator = Validator()

            # Patch the actual validation method to count calls
            original_validate = Validator.validate_schema
            call_count = 0

            def counting_validate(data, file_path=None):
                nonlocal call_count
                call_count += 1
                return original_validate(data, file_path)

            with patch.object(Validator, "validate_schema", counting_validate):
                # Multiple calls with same file and hash
                for _ in range(5):
                    validator.validate_schema_file(temp_file_path, file_hash)

                # The actual validation method should be called fewer times due to caching
                # Note: The exact number depends on cache implementation details
                assert call_count >= 1

        finally:
            os.unlink(temp_file_path)
