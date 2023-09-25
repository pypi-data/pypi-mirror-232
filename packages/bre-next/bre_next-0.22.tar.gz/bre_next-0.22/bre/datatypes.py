from datetime import datetime
from decimal import Decimal as RealDecimal


class ParseError(Exception):
    pass


class Datatype(object):
    id = None

    @staticmethod
    def parse(s):
        raise NotImplementedError()

    @staticmethod
    def serialize(value):
        raise NotImplementedError()


class Null(object):
    id = None

    @staticmethod
    def parse(s):
        if s is not None:
            raise ParseError("Cannot convert to None")
        return s

    @staticmethod
    def serialize(value):
        return None


class String(Datatype):
    id = "string"

    @staticmethod
    def parse(s):
        return s

    @staticmethod
    def serialize(value):
        return value


class Integer(Datatype):
    id = "integer"

    @staticmethod
    def parse(s):
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            raise ParseError("Cannot convert to int")

    @staticmethod
    def serialize(value):
        if value is None:
            return ""
        return str(value)


class Decimal(Datatype):
    id = "decimal"

    @staticmethod
    def parse(s):
        if not isinstance(s, (RealDecimal, int, float, str)):
            return None
        if isinstance(s, str):
            # string can be a digit - what we expect - but there is a chance it is a random string
            # in that case we do not want to present it to the RealDecimal as it will raise an error
            # The other types (Decimal, int, float) are parseable.
            if len(s) == 0:
                return None
            try:
                float(s)
            except ValueError:
                raise ParseError("Could not convert")
        return RealDecimal(s)

    @staticmethod
    def serialize(value):
        if value is None:
            return ""

        if isinstance(value, str):
            # already a string, no need to format
            return value

        return str(normalize_fraction(value))


class Date(Datatype):
    id = "date"

    @staticmethod
    def parse(s):
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            raise ParseError("Cannot convert to date")

    @staticmethod
    def serialize(value):
        if not value:
            return ""
        return value.strftime("%Y-%m-%d")


def normalize_fraction(input_decimal):
    # https://stackoverflow.com/a/11227743
    normalized = input_decimal.normalize()
    __, __, exponent = normalized.as_tuple()
    return normalized if exponent <= 0 else normalized.quantize(1)
