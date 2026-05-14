"""Comprehensive test suite for nldate.parse.

Organized into nine sections covering each documented natural-language form.
TODAY is fixed at Wednesday, June 4, 2025, so weekday rules are unambiguous
and month/year arithmetic avoids 31-day and Feb-29 overflow edge cases.
"""

from datetime import date

import pytest

from nldate import parse


TODAY = date(2025, 6, 4)  # Wednesday


# --- Section 1: Basic reference words ---


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("today", date(2025, 6, 4)),
        ("Today", date(2025, 6, 4)),
        ("TODAY", date(2025, 6, 4)),
        ("  today  ", date(2025, 6, 4)),
        ("tomorrow", date(2025, 6, 5)),
        ("Tomorrow", date(2025, 6, 5)),
        ("TOMORROW", date(2025, 6, 5)),
        ("  tomorrow  ", date(2025, 6, 5)),
        ("yesterday", date(2025, 6, 3)),
        ("Yesterday", date(2025, 6, 3)),
        ("YESTERDAY", date(2025, 6, 3)),
        ("  yesterday  ", date(2025, 6, 3)),
        ("now", date(2025, 6, 4)),
        ("Now", date(2025, 6, 4)),
    ],
)
def test_reference_words(inp: str, expected: date) -> None:
    assert parse(inp, today=TODAY) == expected


# --- Section 2: Numeric relative offsets ---


@pytest.mark.parametrize(
    "inp,expected",
    [
        # in N units
        ("in 1 day", date(2025, 6, 5)),
        ("in 2 days", date(2025, 6, 6)),
        ("in 3 days", date(2025, 6, 7)),
        ("in 1 week", date(2025, 6, 11)),
        ("in 2 weeks", date(2025, 6, 18)),
        ("in 1 month", date(2025, 7, 4)),
        ("in 2 months", date(2025, 8, 4)),
        ("in 1 year", date(2026, 6, 4)),
        ("in 2 years", date(2027, 6, 4)),
        # N units ago
        ("1 day ago", date(2025, 6, 3)),
        ("2 days ago", date(2025, 6, 2)),
        ("3 days ago", date(2025, 6, 1)),
        ("1 week ago", date(2025, 5, 28)),
        ("2 weeks ago", date(2025, 5, 21)),
        ("1 month ago", date(2025, 5, 4)),
        ("2 months ago", date(2025, 4, 4)),
        ("1 year ago", date(2024, 6, 4)),
        ("2 years ago", date(2023, 6, 4)),
    ],
)
def test_numeric_offsets(inp: str, expected: date) -> None:
    assert parse(inp, today=TODAY) == expected


# --- Section 3: English number-word relative offsets ---


@pytest.mark.parametrize(
    "inp,expected",
    [
        # zero
        ("zero days ago", date(2025, 6, 4)),
        ("in zero days", date(2025, 6, 4)),
        # one through twelve (ago, with days)
        ("one day ago", date(2025, 6, 3)),
        ("two days ago", date(2025, 6, 2)),
        ("three days ago", date(2025, 6, 1)),
        ("four days ago", date(2025, 5, 31)),
        ("five days ago", date(2025, 5, 30)),
        ("six days ago", date(2025, 5, 29)),
        ("seven days ago", date(2025, 5, 28)),
        ("eight days ago", date(2025, 5, 27)),
        ("nine days ago", date(2025, 5, 26)),
        ("ten days ago", date(2025, 5, 25)),
        ("eleven days ago", date(2025, 5, 24)),
        ("twelve days ago", date(2025, 5, 23)),
        # weeks ago
        ("one week ago", date(2025, 5, 28)),
        ("two weeks ago", date(2025, 5, 21)),
        ("three weeks ago", date(2025, 5, 14)),
        # months ago
        ("one month ago", date(2025, 5, 4)),
        ("six months ago", date(2024, 12, 4)),
        # years ago
        ("one year ago", date(2024, 6, 4)),
        ("two years ago", date(2023, 6, 4)),
        # in <word> <unit>
        ("in one day", date(2025, 6, 5)),
        ("in two days", date(2025, 6, 6)),
        ("in three days", date(2025, 6, 7)),
        ("in five days", date(2025, 6, 9)),
        ("in ten days", date(2025, 6, 14)),
        ("in twelve days", date(2025, 6, 16)),
        ("in two weeks", date(2025, 6, 18)),
        ("in three months", date(2025, 9, 4)),
        ("in ten years", date(2035, 6, 4)),
        # from <anchor>
        ("two weeks from today", date(2025, 6, 18)),
        ("three days from tomorrow", date(2025, 6, 8)),
        ("2 weeks from now", date(2025, 6, 18)),
        # "a" / "an" as quantity 1
        ("a day ago", date(2025, 6, 3)),
        ("a week ago", date(2025, 5, 28)),
        ("a month ago", date(2025, 5, 4)),
        ("a year ago", date(2024, 6, 4)),
        ("in a day", date(2025, 6, 5)),
        ("in a week", date(2025, 6, 11)),
        ("in a month", date(2025, 7, 4)),
        ("in a year", date(2026, 6, 4)),
        ("a year from today", date(2026, 6, 4)),
    ],
)
def test_word_number_offsets(inp: str, expected: date) -> None:
    assert parse(inp, today=TODAY) == expected


# --- Section 4: Compound offsets (mixed units, "and") ---


@pytest.mark.parametrize(
    "inp,expected",
    [
        # yesterday=2025-06-03; +1yr -> 2026-06-03; +2mo -> 2026-08-03
        ("1 year and 2 months after yesterday", date(2026, 8, 3)),
        ("one year and two months after yesterday", date(2026, 8, 3)),
        # today=2025-06-04; +2w+3d = +17 days
        ("2 weeks and 3 days from today", date(2025, 6, 21)),
        ("two weeks and three days from today", date(2025, 6, 21)),
        # today=2025-06-04; +1mo -> 2025-07-04; +5d -> 2025-07-09
        ("1 month and 5 days after today", date(2025, 7, 9)),
        # tomorrow=2025-06-05; +1mo -> 2025-07-05; +5d -> 2025-07-10
        ("one month and five days after tomorrow", date(2025, 7, 10)),
    ],
)
def test_compound_offsets(inp: str, expected: date) -> None:
    assert parse(inp, today=TODAY) == expected


# --- Section 5: Weekday expressions (next-upcoming / most-recent rule) ---


@pytest.mark.parametrize(
    "inp,expected",
    [
        # From Wed 2025-06-04, "next X" = upcoming X strictly after today
        ("next Thursday", date(2025, 6, 5)),
        ("next Friday", date(2025, 6, 6)),
        ("next Saturday", date(2025, 6, 7)),
        ("next Sunday", date(2025, 6, 8)),
        ("next Monday", date(2025, 6, 9)),
        ("next Tuesday", date(2025, 6, 10)),
        ("next Wednesday", date(2025, 6, 11)),  # exactly 7 days (never today)
        # From Wed 2025-06-04, "last X" = most recent X strictly before today
        ("last Tuesday", date(2025, 6, 3)),
        ("last Monday", date(2025, 6, 2)),
        ("last Sunday", date(2025, 6, 1)),
        ("last Saturday", date(2025, 5, 31)),
        ("last Friday", date(2025, 5, 30)),
        ("last Thursday", date(2025, 5, 29)),
        ("last Wednesday", date(2025, 5, 28)),  # exactly 7 days back (never today)
        # Case-insensitive
        ("Next Friday", date(2025, 6, 6)),
        ("LAST monday", date(2025, 6, 2)),
        ("next FRIDAY", date(2025, 6, 6)),
        ("NEXT THURSDAY", date(2025, 6, 5)),
    ],
)
def test_weekday_expressions(inp: str, expected: date) -> None:
    assert parse(inp, today=TODAY) == expected


# --- Section 6: Absolute month-name dates ---


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("December 1, 2025", date(2025, 12, 1)),
        ("Dec 1, 2025", date(2025, 12, 1)),
        ("Dec. 1, 2025", date(2025, 12, 1)),
        ("Dec 1 2025", date(2025, 12, 1)),
        ("Dec. 1 2025", date(2025, 12, 1)),
        ("January 5th, 2026", date(2026, 1, 5)),
        ("Jan. 5, 2026", date(2026, 1, 5)),
        ("September 9, 2025", date(2025, 9, 9)),
        ("Sep. 9, 2025", date(2025, 9, 9)),
        ("Sept. 9, 2025", date(2025, 9, 9)),
        # Case-insensitivity
        ("DECEMBER 1, 2025", date(2025, 12, 1)),
        ("december 1, 2025", date(2025, 12, 1)),
        # Ordinal suffixes
        ("November 22nd, 2024", date(2024, 11, 22)),
        ("July 3rd, 2025", date(2025, 7, 3)),
        ("February 1st, 2025", date(2025, 2, 1)),
        ("March 4th, 2025", date(2025, 3, 4)),
    ],
)
def test_absolute_month_name(inp: str, expected: date) -> None:
    assert parse(inp) == expected


# --- Section 7: Numeric date formats ---


@pytest.mark.parametrize(
    "inp,expected",
    [
        # ISO YYYY-MM-DD
        ("2025-12-04", date(2025, 12, 4)),
        ("2025-12-01", date(2025, 12, 1)),
        ("2026-01-05", date(2026, 1, 5)),
        # ISO-style YYYY/MM/DD
        ("2025/12/04", date(2025, 12, 4)),
        ("2026/01/05", date(2026, 1, 5)),
        # US MM/DD/YYYY
        ("12/04/2025", date(2025, 12, 4)),
        ("01/05/2026", date(2026, 1, 5)),
        ("12/01/2025", date(2025, 12, 1)),
    ],
)
def test_numeric_dates(inp: str, expected: date) -> None:
    assert parse(inp) == expected


# --- Section 8: Before / after anchored expressions ---


@pytest.mark.parametrize(
    "inp,expected",
    [
        # Anchored to absolute date
        ("1 day before December 1, 2025", date(2025, 11, 30)),
        ("one day before December 1, 2025", date(2025, 11, 30)),
        ("5 days before December 1, 2025", date(2025, 11, 26)),
        ("2 weeks after January 1, 2026", date(2026, 1, 15)),
        ("two weeks after January 1, 2026", date(2026, 1, 15)),
        ("1 day before Dec. 1, 2025", date(2025, 11, 30)),
        ("2 weeks after Dec. 1, 2025", date(2025, 12, 15)),
        # Anchored to relative reference words
        ("3 days after yesterday", date(2025, 6, 6)),
        ("three days after yesterday", date(2025, 6, 6)),
        ("5 days before tomorrow", date(2025, 5, 31)),
        ("five days before tomorrow", date(2025, 5, 31)),
        # from-anchor with various forms
        ("a week from today", date(2025, 6, 11)),
        ("2 weeks from now", date(2025, 6, 18)),
        ("3 days before now", date(2025, 6, 1)),
    ],
)
def test_anchored_before_after(inp: str, expected: date) -> None:
    assert parse(inp, today=TODAY) == expected


# --- Section 9: Invalid inputs raise ValueError ---


@pytest.mark.parametrize(
    "inp",
    [
        "",
        "   ",
        "banana",
        "purple monkey dishwasher",
        "not a date",
        "February 30, 2025",
        "April 31, 2025",
        "2025/99/99",
        "13/45/2025",
        "two centuries ago",
        "in seventeen blorps",
        "next blursday",
        "last fakeday",
    ],
)
def test_invalid_inputs(inp: str) -> None:
    with pytest.raises(ValueError):
        parse(inp, today=TODAY)
