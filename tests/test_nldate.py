from datetime import date

import pytest

from nldate import parse


TODAY = date(2025, 6, 4)


# --- Simple relative ---


def test_today():
    assert parse("today", today=TODAY) == date(2025, 6, 4)


def test_tomorrow():
    assert parse("tomorrow", today=TODAY) == date(2025, 6, 5)


def test_yesterday():
    assert parse("yesterday", today=TODAY) == date(2025, 6, 3)


# --- Relative offsets (plural) ---


def test_in_3_days():
    assert parse("in 3 days", today=TODAY) == date(2025, 6, 7)


def test_3_days_ago():
    assert parse("3 days ago", today=TODAY) == date(2025, 6, 1)


def test_in_2_weeks():
    assert parse("in 2 weeks", today=TODAY) == date(2025, 6, 18)


def test_2_weeks_ago():
    assert parse("2 weeks ago", today=TODAY) == date(2025, 5, 21)


# --- Singular vs plural units ---


def test_in_1_day_singular():
    assert parse("in 1 day", today=TODAY) == date(2025, 6, 5)


def test_in_1_week_singular():
    assert parse("in 1 week", today=TODAY) == date(2025, 6, 11)


def test_in_1_month_singular():
    assert parse("in 1 month", today=TODAY) == date(2025, 7, 4)


def test_in_2_months_plural():
    assert parse("in 2 months", today=TODAY) == date(2025, 8, 4)


def test_in_1_year_singular():
    assert parse("in 1 year", today=TODAY) == date(2026, 6, 4)


def test_1_year_ago():
    assert parse("1 year ago", today=TODAY) == date(2024, 6, 4)


def test_in_2_years_plural():
    assert parse("in 2 years", today=TODAY) == date(2027, 6, 4)


# --- Weekday expressions (next/last = the named weekday in the adjacent calendar week) ---


def test_next_monday():
    assert parse("next Monday", today=TODAY) == date(2025, 6, 9)


def test_next_friday():
    assert parse("next Friday", today=TODAY) == date(2025, 6, 13)


def test_last_friday():
    assert parse("last Friday", today=TODAY) == date(2025, 5, 30)


def test_last_monday():
    assert parse("last Monday", today=TODAY) == date(2025, 5, 26)


# --- Absolute dates with month name ---


def test_absolute_full_month_name():
    assert parse("December 1, 2025") == date(2025, 12, 1)


def test_absolute_short_month_name():
    assert parse("Dec 1, 2025") == date(2025, 12, 1)


def test_absolute_ordinal_suffix():
    assert parse("January 5th, 2026") == date(2026, 1, 5)


# --- Numeric date formats ---


def test_numeric_us_slash():
    # US convention: MM/DD/YYYY
    assert parse("12/01/2025") == date(2025, 12, 1)


def test_numeric_iso_dash():
    assert parse("2025-12-01") == date(2025, 12, 1)


def test_numeric_iso_slash():
    assert parse("2025/12/04") == date(2025, 12, 4)


# --- Before / after anchored to an absolute date ---


def test_days_before_absolute_date():
    assert parse("5 days before December 1, 2025") == date(2025, 11, 26)


def test_weeks_after_absolute_date():
    assert parse("2 weeks after January 1, 2026") == date(2026, 1, 15)


# --- Compound expressions ---


def test_compound_year_and_months_after_yesterday():
    # yesterday = 2025-06-03; +1 year -> 2026-06-03; +2 months -> 2026-08-03
    assert parse("1 year and 2 months after yesterday", today=TODAY) == date(2026, 8, 3)


def test_compound_weeks_and_days_from_today():
    # +14 days + 3 days = +17 days from 2025-06-04
    assert parse("2 weeks and 3 days from today", today=TODAY) == date(2025, 6, 21)


# --- Capitalization and whitespace ---


def test_capitalization_and_whitespace_relative():
    assert parse("  TOMORROW  ", today=TODAY) == date(2025, 6, 5)


def test_capitalization_absolute():
    assert parse("DECEMBER 1, 2025") == date(2025, 12, 1)


# --- Month-name punctuation variants (period after abbreviation, no comma) ---


def test_abbrev_with_period_comma():
    assert parse("Dec. 1, 2025") == date(2025, 12, 1)


def test_abbrev_with_period_no_comma():
    assert parse("Dec. 1 2025") == date(2025, 12, 1)


def test_abbrev_no_comma():
    assert parse("Dec 1 2025") == date(2025, 12, 1)


def test_jan_with_period():
    assert parse("Jan. 5, 2026") == date(2026, 1, 5)


def test_sept_four_letter_abbrev_with_period():
    assert parse("Sept. 9, 2025") == date(2025, 9, 9)


def test_sep_three_letter_abbrev_with_period():
    assert parse("Sep. 9, 2025") == date(2025, 9, 9)


# --- Additional numeric variants ---


def test_numeric_iso_dash_dec_4():
    assert parse("2025-12-04") == date(2025, 12, 4)


def test_numeric_us_slash_dec_4():
    assert parse("12/04/2025") == date(2025, 12, 4)


# --- Anchored offsets against periodised month abbreviation ---


def test_day_before_abbrev_with_period():
    assert parse("1 day before Dec. 1, 2025") == date(2025, 11, 30)


def test_weeks_after_abbrev_with_period():
    assert parse("2 weeks after Dec. 1, 2025") == date(2025, 12, 15)


# --- Invalid input ---


def test_invalid_gibberish_raises():
    with pytest.raises(ValueError):
        parse("not a date", today=TODAY)


def test_invalid_empty_string_raises():
    with pytest.raises(ValueError):
        parse("", today=TODAY)


def test_invalid_calendar_date_raises():
    # February 30 does not exist on any year.
    with pytest.raises(ValueError):
        parse("February 30, 2025")
