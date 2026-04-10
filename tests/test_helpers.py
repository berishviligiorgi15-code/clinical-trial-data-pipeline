from src.utils.helpers import (
    generate_study_business_key,
    normalize_category,
    normalize_placeholder,
    normalize_whitespace,
    parse_start_date,
    split_multi_value_field,
)


def test_normalize_whitespace():
    assert normalize_whitespace("  hello   world  ") == "hello world"


def test_normalize_placeholder_unknown():
    assert normalize_placeholder("Unknown") is None


def test_normalize_placeholder_valid_value():
    assert normalize_placeholder(" Completed ") == "Completed"


def test_normalize_category():
    assert normalize_category("not yet recruiting") == "NOT_YET_RECRUITING"


def test_parse_start_date_day_precision():
    parsed_date, precision = parse_start_date("10/18/21")
    assert parsed_date == "2021-10-18"
    assert precision == "day"


def test_parse_start_date_month_precision():
    parsed_date, precision = parse_start_date("2024-03")
    assert parsed_date == "2024-03-01"
    assert precision == "month"


def test_parse_start_date_unknown():
    parsed_date, precision = parse_start_date("Unknown")
    assert parsed_date is None
    assert precision is None


def test_split_multi_value_field():
    result = split_multi_value_field("Cancer, Diabetes, Cancer")
    assert result == ["Cancer", "Diabetes"]


def test_generate_study_business_key_is_stable():
    key1 = generate_study_business_key(
        "Trial A",
        "Org A",
        "2024-03"
    )
    key2 = generate_study_business_key(
        "Trial A",
        "Org A",
        "2024-03"
    )
    assert key1 == key2