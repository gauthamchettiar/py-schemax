#!/usr/bin/en# Set log level
export SCHEMAX_LOG_LEVEL="DEBUG"

# Set custom log file path (automatically enables file logging)
export SCHEMAX_LOG_FILE_PATH="schemax-debug.log"

# Example usage after sourcing this file:
# schemax validate schema.json  # Uses the environment defaults above

echo "py-schemax environment variables configured:"
echo "  SCHEMAX_VALIDATE_OUTPUT_FORMAT=$SCHEMAX_VALIDATE_OUTPUT_FORMAT"
echo "  SCHEMAX_VALIDATE_OUTPUT_LEVEL=$SCHEMAX_VALIDATE_OUTPUT_LEVEL"
echo "  SCHEMAX_VALIDATE_FAIL_MODE=$SCHEMAX_VALIDATE_FAIL_MODE"
echo "  SCHEMAX_LOG_LEVEL=$SCHEMAX_LOG_LEVEL"
echo "  SCHEMAX_LOG_FILE_PATH=$SCHEMAX_LOG_FILE_PATH"ironment variable configuration for py-schemax
# Source this file or add these exports to your shell profile

# Set default output format to JSON
export SCHEMAX_VALIDATE_OUTPUT_FORMAT="json"

# Set default verbosity to verbose (shows both OK and ERROR results)
export SCHEMAX_VALIDATE_OUTPUT_LEVEL="verbose"

# Set failure mode to never fail (useful for CI/CD logging)
export SCHEMAX_VALIDATE_FAIL_MODE="never"

# Set logging level to DEBUG for detailed information
export SCHEMAX_LOG_LEVEL="DEBUG"

# Set custom log file path (automatically enables file logging)
export SCHEMAX_LOG_FILE_PATH="schemax-debug.log"

# Example usage after sourcing this file:
# schemax validate schema.json  # Uses the environment defaults above

echo "py-schemax environment variables configured:"
echo "  SCHEMAX_VALIDATE_OUTPUT_FORMAT=$SCHEMAX_VALIDATE_OUTPUT_FORMAT"
echo "  SCHEMAX_VALIDATE_OUTPUT_LEVEL=$SCHEMAX_VALIDATE_OUTPUT_LEVEL"
echo "  SCHEMAX_VALIDATE_FAIL_MODE=$SCHEMAX_VALIDATE_FAIL_MODE"
echo "  SCHEMAX_LOG_LEVEL=$SCHEMAX_LOG_LEVEL"
echo "  SCHEMAX_LOG_FILE_PATH=$SCHEMAX_LOG_FILE_PATH"
