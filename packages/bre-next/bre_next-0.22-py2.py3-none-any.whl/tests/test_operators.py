from datetime import date
from decimal import Decimal

from bre.operators import operator_registry


def test_str_equals():
    str_equals = operator_registry.get("str_equals")
    assert str_equals.evaluate("AA", "AA")
    assert not str_equals.evaluate("AA", "aa")


def test_str_equals_insensitive():
    str_equals_insensitive = operator_registry.get("str_equals_insensitive")
    assert str_equals_insensitive.evaluate("AA", "AA")
    assert str_equals_insensitive.evaluate("AA", "aa")
    assert not str_equals_insensitive.evaluate("AA", "BB")
    assert not str_equals_insensitive.evaluate("AA", "bb")


def test_str_not_equals():
    str_not_equals = operator_registry.get("str_not_equals")
    assert not str_not_equals.evaluate("AA", "AA")
    assert str_not_equals.evaluate("AA", "aa")


def test_str_not_equals_insensitive():
    str_not_equals_insensitive = operator_registry.get("str_not_equals_insensitive")
    assert not str_not_equals_insensitive.evaluate("AA", "AA")
    assert not str_not_equals_insensitive.evaluate("AA", "aa")
    assert str_not_equals_insensitive.evaluate("AA", "BB")
    assert str_not_equals_insensitive.evaluate("AA", "bb")


def test_str_empty():
    str_empty = operator_registry.get("str_empty")
    assert str_empty.evaluate("", None)
    assert not str_empty.evaluate("AA", None)


def test_str_is_not_empty():
    str_is_not_empty = operator_registry.get("str_is_not_empty")
    assert not str_is_not_empty.evaluate("", None)
    assert str_is_not_empty.evaluate("AA", None)


def test_str_starts_with():
    str_starts_with = operator_registry.get("str_starts_with")
    assert str_starts_with.evaluate("AA", "A")
    assert not str_starts_with.evaluate("AA", "a")


def test_str_starts_with_insensitive():
    str_starts_with_insensitive = operator_registry.get("str_starts_with_insensitive")
    assert str_starts_with_insensitive.evaluate("AA", "A")
    assert str_starts_with_insensitive.evaluate("AA", "a")
    assert not str_starts_with_insensitive.evaluate("AA", "B")
    assert not str_starts_with_insensitive.evaluate("AA", "b")


def test_str_starts_not_with():
    str_starts_not_with = operator_registry.get("str_starts_not_with")
    assert not str_starts_not_with.evaluate("AA", "A")
    assert str_starts_not_with.evaluate("AA", "a")


def test_str_starts_not_with_insensitive():
    str_starts_not_with_insensitive = operator_registry.get("str_starts_not_with_insensitive")
    assert not str_starts_not_with_insensitive.evaluate("AA", "A")
    assert not str_starts_not_with_insensitive.evaluate("AA", "a")
    assert str_starts_not_with_insensitive.evaluate("AA", "B")
    assert str_starts_not_with_insensitive.evaluate("AA", "b")


def test_str_ends_with():
    str_ends_with = operator_registry.get("str_ends_with")
    assert str_ends_with.evaluate("AA", "A")
    assert not str_ends_with.evaluate("AA", "a")


def test_str_ends_with_insensitive():
    str_ends_with_insensitive = operator_registry.get("str_ends_with_insensitive")
    assert str_ends_with_insensitive.evaluate("AA", "A")
    assert str_ends_with_insensitive.evaluate("AA", "a")


def test_str_ends_not_with():
    str_ends_not_with = operator_registry.get("str_ends_not_with")
    assert not str_ends_not_with.evaluate("AA", "A")
    assert str_ends_not_with.evaluate("AA", "a")


def test_str_ends_not_with_insensitive():
    str_ends_not_with_insensitive = operator_registry.get("str_ends_not_with_insensitive")
    assert not str_ends_not_with_insensitive.evaluate("AA", "A")
    assert not str_ends_not_with_insensitive.evaluate("AA", "a")
    assert str_ends_not_with_insensitive.evaluate("AA", "B")
    assert str_ends_not_with_insensitive.evaluate("AA", "b")


def test_str_contains():
    str_contains = operator_registry.get("str_contains")
    assert str_contains.evaluate("AA", "A")
    assert not str_contains.evaluate("AA", "a")


def test_str_contains_insensitive():
    str_contains_insensitive = operator_registry.get("str_contains_insensitive")
    assert str_contains_insensitive.evaluate("AA", "A")
    assert str_contains_insensitive.evaluate("AA", "a")


def test_str_not_contains():
    str_not_contains = operator_registry.get("str_not_contains")
    assert not str_not_contains.evaluate("AA", "A")
    assert str_not_contains.evaluate("AA", "a")


def test_str_not_contains_insensitive():
    str_not_contains_insensitive = operator_registry.get("str_not_contains_insensitive")
    assert not str_not_contains_insensitive.evaluate("AA", "A")
    assert not str_not_contains_insensitive.evaluate("AA", "a")
    assert str_not_contains_insensitive.evaluate("AA", "B")
    assert str_not_contains_insensitive.evaluate("AA", "b")


def test_str_match_regex():
    str_match_regex = operator_registry.get("str_match_regex")
    assert str_match_regex.evaluate("AA", "^([A-Z]+)")
    assert not str_match_regex.evaluate("aa", "^([A-Z]+)")


def test_str_not_match_regex():
    str_not_match_regex = operator_registry.get("str_not_match_regex")
    assert not str_not_match_regex.evaluate("AA", "^([A-Z]+)")
    assert str_not_match_regex.evaluate("aa", "^([A-Z]+)")


def test_decimal_equals():
    decimal_equals = operator_registry.get("decimal_equals")
    assert decimal_equals.evaluate(Decimal("1.0"), Decimal("1.0"))
    assert not decimal_equals.evaluate(Decimal("2.0"), Decimal("3.0"))


def test_decimal_not_equals():
    decimal_not_equals = operator_registry.get("decimal_not_equals")
    assert not decimal_not_equals.evaluate(Decimal("1.0"), Decimal("1.0"))
    assert decimal_not_equals.evaluate(Decimal("2.0"), Decimal("3.0"))


def test_decimal_greater_then():
    decimal_greater_then = operator_registry.get("decimal_greater_then")
    assert decimal_greater_then.evaluate(Decimal("2.0"), Decimal("1.0"))
    assert not decimal_greater_then.evaluate(Decimal("2.0"), Decimal("2.0"))


def test_decimal_smaller_then():
    decimal_smaller_then = operator_registry.get("decimal_smaller_then")
    assert decimal_smaller_then.evaluate(Decimal("1.0"), Decimal("2.0"))
    assert not decimal_smaller_then.evaluate(Decimal("2.0"), Decimal("2.0"))


def test_date_equals():
    date_equals = operator_registry.get("date_equals")
    date1 = date(2017, 6, 1)
    date2 = date(2017, 6, 1)
    date3 = date(2018, 6, 1)
    assert date_equals.evaluate(date1, date2)
    assert not date_equals.evaluate(date1, date3)


def test_date_not_equals():
    date_not_equals = operator_registry.get("date_not_equals")
    date1 = date(2017, 6, 1)
    date2 = date(2017, 6, 1)
    date3 = date(2018, 6, 1)
    assert not date_not_equals.evaluate(date1, date2)
    assert date_not_equals.evaluate(date1, date3)


def test_date_greater_then():
    date_greater_then = operator_registry.get("date_greater_then")
    date1 = date(2017, 6, 1)
    date2 = date(2017, 6, 1)
    date3 = date(2018, 6, 1)
    assert date_greater_then.evaluate(date3, date1)
    assert not date_greater_then.evaluate(date1, date2)


def test_date_smaller_then():
    date_smaller_then = operator_registry.get("date_smaller_then")
    date1 = date(2017, 6, 1)
    date2 = date(2017, 6, 1)
    date3 = date(2018, 6, 1)
    assert date_smaller_then.evaluate(date1, date3)
    assert not date_smaller_then.evaluate(date1, date2)
