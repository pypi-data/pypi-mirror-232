from datetime import date
from decimal import Decimal as RealDecimal

import pytest

from bre.core import Action, Operator
from bre.datatypes import Date, Decimal, Integer, ParseError, String


def test_parse_string():
    assert String.parse("Foo") == "Foo"


def test_parse_empty_string():
    assert String.parse("") == ""


def test_serialize_string():
    assert String.serialize("foo") == "foo"


def test_serialize_empty_string():
    assert String.serialize("") == ""


def test_parse_integer():
    assert Integer.parse("1") == 1


def test_parse_wrong_integer():
    with pytest.raises(ParseError):
        Integer.parse("foo")


def test_parse_empty_integer():
    assert Integer.parse("") is None


def test_serialize_integer():
    assert Integer.serialize(1) == "1"


def test_serialize_empty_integer():
    assert Integer.serialize(None) == ""


def test_parse_decimal():
    assert Decimal.parse("3.14") == RealDecimal("3.14")


def test_parse_wrong_decimal():
    with pytest.raises(ParseError):
        Decimal.parse("blah")


def test_parse_empty_decimal():
    assert Decimal.parse("") is None


def test_serialize_decimal():
    assert Decimal.serialize(RealDecimal("3.14")) == "3.14"


def test_serialize_empty_decimal():
    assert Decimal.serialize(None) == ""


def test_parse_date():
    assert Date.parse("2017-02-01") == date(2017, 2, 1)


def test_parse_wrong_date():
    with pytest.raises(ParseError):
        Date.parse("blah")


def test_parse_empty_date():
    assert Date.parse("") is None


def test_serialize_date():
    assert Date.serialize(date(2017, 2, 1)) == "2017-02-01"


def test_serialize_empty_date():
    assert Date.serialize(None) == ""


def test_operator_parse():
    operator = Operator("foo", "Foo", lambda a, b: True, Integer, Integer)
    assert operator.convert(1) == 1


def test_action_parse():
    action = Action("foo", "Foo", String, Integer, lambda t, v: None)
    assert action.convert(1) == 1


def test_parse_zero_decimal():
    assert Decimal.parse(RealDecimal("0.00000000")) is not None
