# -*- coding: utf-8 -*-
import logging

from . import datatypes
from .core import ActionRegistry
from .i18n import _

# global collection with Actions
action_registry = ActionRegistry()

logger = logging.getLogger(__name__)


@action_registry.register(_("set"), datatypes.String, datatypes.String, for_choices=True)
def set_str(manipulator, value):
    if manipulator.has_source_manipulator():
        value = manipulator.get()
    if manipulator.first:
        manipulator.set(value)
    else:
        manipulator.delete()


@action_registry.register(_("delete"), datatypes.String, datatypes.Null, for_choices=True)
def delete_str(manipulator, value):
    manipulator.delete()


@action_registry.register(_("strip"), datatypes.String, datatypes.Null)
def strip_str(manipulator, value):
    value = manipulator.get()
    value = "".join(value.split())
    manipulator.set(value)


@action_registry.register(_("string_left_string"), datatypes.String, datatypes.String)
def string_left_string(manipulator, value):
    original_value = manipulator.get()
    new_value = original_value.split(value)[0]
    manipulator.set(new_value)


@action_registry.register(_("string_left_integer"), datatypes.String, datatypes.Integer)
def string_left_integer(manipulator, value):
    original_value = manipulator.get()
    new_value = original_value[: (value - 1)]
    manipulator.set(new_value)


@action_registry.register(_("string_right_string"), datatypes.String, datatypes.String)
def string_right_string(manipulator, value):
    original_value = manipulator.get()
    try:
        dummy, new_value = original_value.split(value, 1)
    except ValueError:
        new_value = original_value
    manipulator.set(new_value)


@action_registry.register(_("string_right_integer"), datatypes.String, datatypes.Integer)
def string_right_integer(manipulator, value):
    original_value = manipulator.get()
    new_value = original_value[value:]
    manipulator.set(new_value)


@action_registry.register(_("string_leftback_string"), datatypes.String, datatypes.String)
def string_leftback_string(manipulator, value):
    original_value = manipulator.get()
    try:
        new_value, dummy = original_value.rsplit(value, 1)
    except ValueError:
        new_value = original_value
    manipulator.set(new_value)


@action_registry.register(_("string_leftback_integer"), datatypes.String, datatypes.Integer)
def string_leftback_integer(manipulator, value):
    original_value = manipulator.get()
    new_value = original_value[:-value]
    manipulator.set(new_value)


@action_registry.register(_("string_rightback_string"), datatypes.String, datatypes.String)
def string_rightback_string(manipulator, value):
    original_value = manipulator.get()
    new_value = original_value.split(value)[-1]
    manipulator.set(new_value)


@action_registry.register(_("string_rightback_integer"), datatypes.String, datatypes.Integer)
def string_rightback_integer(manipulator, value):
    original_value = manipulator.get()
    new_value = original_value[-(value - 1) :]
    manipulator.set(new_value)


@action_registry.register(_("prefix"), datatypes.String, datatypes.String)
def prefix_str(manipulator, value):
    original_value = manipulator.get()
    manipulator.set(value + original_value)


@action_registry.register(_("postfix"), datatypes.String, datatypes.String)
def postfix_str(manipulator, value):
    original_value = manipulator.get()
    manipulator.set(original_value + value)


@action_registry.register(_("set"), datatypes.Decimal, datatypes.Decimal, for_choices=True)
def set_decimal(manipulator, value):
    if manipulator.has_source_manipulator():
        value = manipulator.get()
    if manipulator.first:
        manipulator.set(value)
    else:
        manipulator.delete()


@action_registry.register(_("delete"), datatypes.Decimal, datatypes.Null, for_choices=True)
def delete_decimal(manipulator, value):
    manipulator.delete()


@action_registry.register(_("absolute"), datatypes.Decimal, datatypes.Null, for_choices=True)
def absolute_decimal(manipulator, value):
    value = manipulator.get()
    value = abs(value)
    manipulator.set(value)


@action_registry.register(_("negative"), datatypes.Decimal, datatypes.Null, for_choices=True)
def negative_decimal(manipulator, value):
    value = manipulator.get()
    value = -value
    manipulator.set(value)


@action_registry.register(_("set"), datatypes.Integer, datatypes.Integer, for_choices=True)
def set_int(manipulator, value):
    if manipulator.has_source_manipulator():
        value = manipulator.get()
    if manipulator.first:
        manipulator.set(value)
    else:
        manipulator.delete()


@action_registry.register(_("delete"), datatypes.Integer, datatypes.Null, for_choices=True)
def delete_int(manipulator, value):
    manipulator.delete()


@action_registry.register(_("absolute"), datatypes.Integer, datatypes.Null, for_choices=True)
def absolute_integer(manipulator, value):
    value = manipulator.get()
    value = abs(value)
    manipulator.set(value)


@action_registry.register(_("negative"), datatypes.Integer, datatypes.Null, for_choices=True)
def negative_integer(manipulator, value):
    value = manipulator.get()
    value = -value
    manipulator.set(value)


@action_registry.register(_("set"), datatypes.Date, datatypes.Date, for_choices=True)
def set_date(manipulator, value):
    if manipulator.has_source_manipulator():
        value = manipulator.get()
    if manipulator.first:
        manipulator.set(value)
    else:
        manipulator.delete()


@action_registry.register(_("delete"), datatypes.Date, datatypes.Null, for_choices=True)
def delete_date(manipulator, value):
    manipulator.delete()
