import hashlib
import re
from datetime import datetime
from typing import List, Optional, Tuple


NULL_LIKE_VALUES = {"", "unknown", "na", "n/a", "none", "null"}


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_placeholder(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    cleaned = normalize_whitespace(str(value))

    if cleaned.lower() in NULL_LIKE_VALUES:
        return None

    return cleaned


def normalize_category(value: Optional[str]) -> Optional[str]:
    cleaned = normalize_placeholder(value)
    if cleaned is None:
        return None
    return cleaned.upper().replace(" ", "_")


def parse_start_date(value: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    cleaned = normalize_placeholder(value)
    if cleaned is None:
        return None, None

    date_formats = [
        ("%m/%d/%y", "day"),
        ("%m/%d/%Y", "day"),
        ("%Y-%m-%d", "day"),
        ("%Y-%m", "month"),
        ("%Y", "year"),
    ]

    for fmt, precision in date_formats:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            if precision == "month":
                parsed = parsed.replace(day=1)
            elif precision == "year":
                parsed = parsed.replace(month=1, day=1)
            return parsed.date().isoformat(), precision
        except ValueError:
            continue

    return None, None


def split_multi_value_field(value: Optional[str]) -> List[str]:
    cleaned = normalize_placeholder(value)
    if cleaned is None:
        return []

    parts = [normalize_whitespace(part) for part in cleaned.split(",")]
    parts = [part for part in parts if part and part.lower() not in NULL_LIKE_VALUES]

    seen = set()
    result = []

    for part in parts:
        key = part.lower()
        if key not in seen:
            seen.add(key)
            result.append(part)

    return result


def generate_study_business_key(
    brief_title: Optional[str],
    organization_full_name: Optional[str],
    start_date_raw: Optional[str],
) -> str:
    title = normalize_placeholder(brief_title) or ""
    organization = normalize_placeholder(organization_full_name) or ""
    start_date = normalize_placeholder(start_date_raw) or ""

    raw_key = "||".join(
        [
            normalize_whitespace(title).lower(),
            normalize_whitespace(organization).lower(),
            normalize_whitespace(start_date).lower(),
        ]
    )

    return hashlib.md5(raw_key.encode("utf-8")).hexdigest()