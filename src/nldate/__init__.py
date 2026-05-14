"""Natural-language date parser."""

import calendar
import re
from datetime import date, timedelta

__all__ = ["parse"]


WEEKDAYS: dict[str, int] = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

MONTHS: dict[str, int] = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

WORD_NUMBERS: dict[str, int] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

UNIT_TO_FIELD: dict[str, str] = {
    "day": "days",
    "days": "days",
    "week": "weeks",
    "weeks": "weeks",
    "month": "months",
    "months": "months",
    "year": "years",
    "years": "years",
}

_ISO_RE = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")
_ISO_SLASH_RE = re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2})$")
_US_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_MONTH_NAME_RE = re.compile(r"^([a-z]+)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})$")
_NEXT_WD_RE = re.compile(r"^next\s+([a-z]+)$")
_LAST_WD_RE = re.compile(r"^last\s+([a-z]+)$")
_IN_RE = re.compile(r"^in\s+(.+)$")
_AGO_RE = re.compile(r"^(.+)\s+ago$")
_BEFORE_RE = re.compile(r"^(.+?)\s+before\s+(.+)$")
_AFTER_RE = re.compile(r"^(.+?)\s+after\s+(.+)$")
_FROM_RE = re.compile(r"^(.+?)\s+from\s+(.+)$")
_OFFSET_CHUNK_RE = re.compile(rf"^(\d+|an?|{'|'.join(WORD_NUMBERS)})\s+([a-z]+)$")


def _add_months(d: date, n: int) -> date:
    total = d.month - 1 + n
    new_year = d.year + total // 12
    new_month = total % 12 + 1
    last_day = calendar.monthrange(new_year, new_month)[1]
    return date(new_year, new_month, min(d.day, last_day))


def _add_years(d: date, n: int) -> date:
    new_year = d.year + n
    last_day = calendar.monthrange(new_year, d.month)[1]
    return date(new_year, d.month, min(d.day, last_day))


def _apply_offset(d: date, offset: dict[str, int], sign: int) -> date:
    result = d
    if offset.get("years"):
        result = _add_years(result, sign * offset["years"])
    if offset.get("months"):
        result = _add_months(result, sign * offset["months"])
    day_total = offset.get("weeks", 0) * 7 + offset.get("days", 0)
    if day_total:
        result = result + timedelta(days=sign * day_total)
    return result


def _parse_offset(text: str) -> dict[str, int]:
    parts = re.split(r"\s+and\s+|\s*,\s*", text.strip())
    if not parts or parts == [""]:
        raise ValueError(f"Could not parse offset: {text!r}")
    result: dict[str, int] = {"days": 0, "weeks": 0, "months": 0, "years": 0}
    for part in parts:
        m = _OFFSET_CHUNK_RE.match(part.strip())
        if not m:
            raise ValueError(f"Could not parse offset chunk: {part!r}")
        n_str = m.group(1)
        if n_str in ("a", "an"):
            n = 1
        elif n_str in WORD_NUMBERS:
            n = WORD_NUMBERS[n_str]
        else:
            n = int(n_str)
        unit = m.group(2)
        if unit not in UNIT_TO_FIELD:
            raise ValueError(f"Unknown unit: {unit!r}")
        result[UNIT_TO_FIELD[unit]] += n
    return result


def _parse_absolute(text: str) -> date | None:
    m = _ISO_RE.match(text)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = _ISO_SLASH_RE.match(text)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = _US_RE.match(text)
    if m:
        return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
    m = _MONTH_NAME_RE.match(text)
    if m:
        token = m.group(1)
        if token not in MONTHS:
            return None
        return date(int(m.group(3)), MONTHS[token], int(m.group(2)))
    return None


def _parse_anchor(text: str, today: date) -> date | None:
    text = text.strip()
    if text in ("today", "now"):
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    if text == "yesterday":
        return today - timedelta(days=1)
    return _parse_absolute(text)


def _weekday_in_adjacent_week(today: date, weekday: int, shift_weeks: int) -> date:
    this_monday = today - timedelta(days=today.weekday())
    target_monday = this_monday + timedelta(weeks=shift_weeks)
    return target_monday + timedelta(days=weekday)


def parse(s: str, today: date | None = None) -> date:
    if not isinstance(s, str):
        raise ValueError(f"Expected str, got {type(s).__name__}")
    normalized = s.strip().lower()
    if not normalized:
        raise ValueError("Empty input")
    if today is None:
        today = date.today()

    if normalized in ("today", "now"):
        return today
    if normalized == "tomorrow":
        return today + timedelta(days=1)
    if normalized == "yesterday":
        return today - timedelta(days=1)

    abs_date = _parse_absolute(normalized)
    if abs_date is not None:
        return abs_date

    m = _NEXT_WD_RE.match(normalized)
    if m:
        wd = m.group(1)
        if wd not in WEEKDAYS:
            raise ValueError(f"Unknown weekday: {wd!r}")
        return _weekday_in_adjacent_week(today, WEEKDAYS[wd], shift_weeks=1)

    m = _LAST_WD_RE.match(normalized)
    if m:
        wd = m.group(1)
        if wd not in WEEKDAYS:
            raise ValueError(f"Unknown weekday: {wd!r}")
        return _weekday_in_adjacent_week(today, WEEKDAYS[wd], shift_weeks=-1)

    for pattern, sign in ((_BEFORE_RE, -1), (_AFTER_RE, 1), (_FROM_RE, 1)):
        m = pattern.match(normalized)
        if not m:
            continue
        anchor = _parse_anchor(m.group(2), today)
        if anchor is None:
            continue
        offset = _parse_offset(m.group(1))
        return _apply_offset(anchor, offset, sign)

    m = _IN_RE.match(normalized)
    if m:
        return _apply_offset(today, _parse_offset(m.group(1)), 1)

    m = _AGO_RE.match(normalized)
    if m:
        return _apply_offset(today, _parse_offset(m.group(1)), -1)

    raise ValueError(f"Could not parse date: {s!r}")
