# -*- coding: utf-8 -*-
import logging
import re

from . import datatypes
from .core import OperatorRegistry
from .i18n import _

# global collection with Operators
operator_registry = OperatorRegistry()

logger = logging.getLogger(__name__)


@operator_registry.register(_("equals"), datatypes.String, datatypes.String, for_choices=True)
def str_equals(extracted_value, compare_value):
    logger.debug(
        "str_equals `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value == compare_value


@operator_registry.register(_("equals_insensitive"), datatypes.String, datatypes.String, for_choices=True)
def str_equals_insensitive(extracted_value, compare_value):
    logger.debug(
        "str_equals_insensitive `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value.lower() == compare_value.lower()


@operator_registry.register(_("not_equals"), datatypes.String, datatypes.String, for_choices=True)
def str_not_equals(extracted_value, compare_value):
    logger.debug(
        "str_not_equals `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value != compare_value


@operator_registry.register(_("not_equals_insensitive"), datatypes.String, datatypes.String, for_choices=True)
def str_not_equals_insensitive(extracted_value, compare_value):
    logger.debug(
        "str_not_equals_insensitive `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value.lower() != compare_value.lower()


@operator_registry.register(_("empty"), datatypes.String, datatypes.Null)
def str_empty(extracted_value, compare_value):
    logger.debug("str_empty `%s` (%s)", extracted_value, type(extracted_value))
    return extracted_value == ""


@operator_registry.register(_("is_not_empty"), datatypes.String, datatypes.Null)
def str_is_not_empty(extracted_value, compare_value):
    logger.debug("str_is_not_empty `%s` (%s)", extracted_value, type(extracted_value))
    return extracted_value != ""


@operator_registry.register(_("starts_with"), datatypes.String, datatypes.String)
def str_starts_with(extracted_value, compare_value):
    logger.debug(
        "str_starts_with `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value.startswith(compare_value)


@operator_registry.register(_("starts_with_insensitive"), datatypes.String, datatypes.String)
def str_starts_with_insensitive(extracted_value, compare_value):
    logger.debug(
        "str_starts_with_insensitive `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value.lower().startswith(compare_value.lower())


@operator_registry.register(_("starts_not_with"), datatypes.String, datatypes.String)
def str_starts_not_with(extracted_value, compare_value):
    logger.debug(
        "str_starts_not_with `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return not extracted_value.startswith(compare_value)


@operator_registry.register(_("starts_not_with_insensitive"), datatypes.String, datatypes.String)
def str_starts_not_with_insensitive(extracted_value, compare_value):
    logger.debug(
        "str_starts_not_with_insensitive `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return not extracted_value.lower().startswith(compare_value.lower())


@operator_registry.register(_("ends_with"), datatypes.String, datatypes.String)
def str_ends_with(extracted_value, compare_value):
    logger.debug(
        "str_ends_with `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value.endswith(compare_value)


@operator_registry.register(_("ends_with_insensitive"), datatypes.String, datatypes.String)
def str_ends_with_insensitive(extracted_value, compare_value):
    logger.debug(
        "str_ends_with_insensitive `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value.lower().endswith(compare_value.lower())


@operator_registry.register(_("ends_not_with"), datatypes.String, datatypes.String)
def str_ends_not_with(extracted_value, compare_value):
    logger.debug(
        "str_ends_not_with `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return not extracted_value.endswith(compare_value)


@operator_registry.register(_("ends_not_with_insensitive"), datatypes.String, datatypes.String)
def str_ends_not_with_insensitive(extracted_value, compare_value):
    logger.debug(
        "str_ends_not_with_insensitive `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return not extracted_value.lower().endswith(compare_value.lower())


@operator_registry.register(_("contains"), datatypes.String, datatypes.String)
def str_contains(extracted_value, compare_value):
    logger.debug(
        "str_contains `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return compare_value in extracted_value


@operator_registry.register(_("contains_insensitive"), datatypes.String, datatypes.String)
def str_contains_insensitive(extracted_value, compare_value):
    logger.debug(
        "str_contains_insensitive `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return compare_value.lower() in extracted_value.lower()


@operator_registry.register(_("not_contains"), datatypes.String, datatypes.String)
def str_not_contains(extracted_value, compare_value):
    logger.debug(
        "str_not_contains `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return compare_value not in extracted_value


@operator_registry.register(_("not_contains_insensitive"), datatypes.String, datatypes.String)
def str_not_contains_insensitive(extracted_value, compare_value):
    logger.debug(
        "str_not_contains_insensitive `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return compare_value.lower() not in extracted_value.lower()


@operator_registry.register(_("match_regex"), datatypes.String, datatypes.String)
def str_match_regex(extracted_value, regex):
    logger.debug(
        "str_match_regex `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        regex,
        type(regex),
    )
    pattern = re.compile(regex)
    return pattern.match(extracted_value)


@operator_registry.register(_("not_match_regex"), datatypes.String, datatypes.String)
def str_not_match_regex(extracted_value, regex):
    logger.debug(
        "str_not_match_regex `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        regex,
        type(regex),
    )
    pattern = re.compile(regex)
    return not pattern.match(extracted_value)


@operator_registry.register(_("equals"), datatypes.Decimal, datatypes.Decimal, for_choices=True)
def decimal_equals(extracted_value, compare_value):
    logger.debug(
        "decimal_equals `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value == compare_value


@operator_registry.register(_("not_equals"), datatypes.Decimal, datatypes.Decimal, for_choices=True)
def decimal_not_equals(extracted_value, compare_value):
    logger.debug(
        "decimal_not_equals `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value != compare_value


@operator_registry.register(_("greater_than"), datatypes.Decimal, datatypes.Decimal)
def decimal_greater_then(extracted_value, compare_value):
    logger.debug(
        "decimal_greater_then `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value > compare_value


@operator_registry.register(_("smaller_than"), datatypes.Decimal, datatypes.Decimal)
def decimal_smaller_then(extracted_value, compare_value):
    logger.debug(
        "decimal_smaller_then `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value < compare_value


@operator_registry.register(_("equals"), datatypes.Date, datatypes.Date, for_choices=True)
def date_equals(extracted_value, compare_value):
    logger.debug(
        "date_equals `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value == compare_value


@operator_registry.register(_("not_equals"), datatypes.Date, datatypes.Date, for_choices=True)
def date_not_equals(extracted_value, compare_value):
    logger.debug(
        "date_not_equals `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value != compare_value


@operator_registry.register(_("greater_than"), datatypes.Date, datatypes.Date)
def date_greater_then(extracted_value, compare_value):
    logger.debug(
        "date_greater_then `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value > compare_value


@operator_registry.register(_("smaller_than"), datatypes.Date, datatypes.Date)
def date_smaller_then(extracted_value, compare_value):
    logger.debug(
        "date_smaller_then `%s` (%s), with `%s` (%s)",
        extracted_value,
        type(extracted_value),
        compare_value,
        type(compare_value),
    )
    return extracted_value < compare_value
