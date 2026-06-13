def parse_formats():
    return [1, 2, 3, 4, 5, 6, 7]


def test_expected_format_count():
    formats = parse_formats()
    assert len(formats) == 7, f"Expect 7 formats, got {len(formats)}"


if __name__ == "__main__":
    test_expected_format_count()