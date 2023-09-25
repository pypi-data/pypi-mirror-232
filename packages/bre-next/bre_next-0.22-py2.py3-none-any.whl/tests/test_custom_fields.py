from decimal import Decimal

from lxml import etree

from bre.actions import action_registry
from bre.core import ALL, ActionWithValue, Condition, Operator, Rule, Rules

from .fields import field_registry
from .utils import fixture


def test_actions():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)

    # test before action
    custom_str0 = field_registry.get("custom_str0").get(tree)
    assert custom_str0 == ""

    # execute action
    set_str = action_registry.get("set_str")
    field = field_registry.get("custom_str0")
    action = ActionWithValue(set_str, field, "Foo")
    action.perform(tree)

    # test after action
    custom_str0 = field_registry.get("custom_str0").get(tree)
    assert custom_str0 == "Foo"
