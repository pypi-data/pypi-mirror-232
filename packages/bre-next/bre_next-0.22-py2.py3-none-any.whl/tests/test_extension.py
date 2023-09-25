from decimal import Decimal

from lxml import etree

from bre.actions import action_registry
from bre.core import ALL, ActionWithValue, Condition, Operator, Rule, Rules

from .fields import field_registry
from .utils import fixture


def test_extractors():
    with fixture("invoice_extension_000000.xml") as f:
        tree = etree.parse(f)
    amount = field_registry.get("extension_000000_amount").get(tree)
    description = field_registry.get("extension_000000_description").get(tree)
    assert amount == Decimal("123.45")
    assert description == "TEST"


def test_actions():
    with fixture("invoice_extension_000000.xml") as f:
        tree = etree.parse(f)

    # test before action
    description = field_registry.get("extension_000000_description").get(tree)
    assert description == "TEST"

    # execute action
    delete = action_registry.get("delete_str")
    field = field_registry.get("extension_000000_description")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)

    # test after action
    description = field_registry.get("extension_000000_description").get(tree)
    assert description == ""


def test_core():
    invoice_number = field_registry.get("extension_000000_description")
    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition = Condition(invoice_number, operator, "TEST")

    amount = field_registry.get("extension_000000_amount")
    action = action_registry.get("set_decimal")
    action_with_value = ActionWithValue(action, amount, "12.345")

    rule1 = Rule("Rule1", "Description", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule1])

    with fixture("invoice_extension_000000.xml") as f:
        input_tree = etree.parse(f)

    # test before execution
    assert amount.get(input_tree) == Decimal("123.45")

    # execute Rule
    output_tree = rules.perform(input_tree)

    # test after execution
    assert amount.get(output_tree) == Decimal("12.345")
