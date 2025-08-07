from typing import Any, Dict, List


class Summary:
    def __init__(self) -> None:
        self.validated_file_count = 0
        self.valid_file_count = 0
        self.invalid_file_count = 0
        self.error_files: List[str] = []

    def add_record(self, valid: bool, file_path: str) -> None:
        self.validated_file_count += 1
        if valid:
            self.valid_file_count += 1
        else:
            self.invalid_file_count += 1
            self.error_files.append(file_path)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validated_file_count": self.validated_file_count,
            "valid_file_count": self.valid_file_count,
            "invalid_file_count": self.invalid_file_count,
            "error_files": self.error_files,
        }
