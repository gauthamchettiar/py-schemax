from py_schemax.summary import Summary


def test_summary():
    summary = Summary()
    summary.add_record(True, "file1.json")
    summary.add_record(False, "file2.json")
    summary.add_record(True, "file3.json")

    assert summary.validated_file_count == 3
    assert summary.valid_file_count == 2
    assert summary.invalid_file_count == 1
    assert summary.error_files == ["file2.json"]


def test_summary_representations():
    summary = Summary()
    summary.add_record(True, "file1.json")
    summary.add_record(False, "file2.json")

    dict_repr = summary.to_dict()
    assert dict_repr == {
        "validated_file_count": 2,
        "valid_file_count": 1,
        "invalid_file_count": 1,
        "error_files": ["file2.json"],
    }
