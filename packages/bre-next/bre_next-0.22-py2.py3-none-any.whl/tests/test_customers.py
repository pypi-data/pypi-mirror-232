from decimal import Decimal

from lxml import etree

from bre.actions import action_registry
from bre.core import ALL, ActionWithValue, Condition, Rule, Rules
from bre.operators import operator_registry

from .fields import field_registry
from .utils import fixture


def test_T210413_035_001():
    # if "vendor_name" "contains_insensitive" "Prodrive"
    # and "OrderLineNumber" is not empty
    header_source_field = field_registry.get("vendor_name")
    operator = operator_registry.get("str_contains_insensitive")
    condition_1 = Condition(header_source_field, operator, "Prodrive")
    line_source_field = field_registry.get("line_orderlinenumber")
    operator = operator_registry.get("str_is_not_empty")
    condition_2 = Condition(line_source_field, operator, "")

    # then set "line_orderlinenumber" to "changed"
    line_source_field = field_registry.get("line_orderlinenumber")
    action = action_registry.get("set_str")
    action = ActionWithValue(action, line_source_field, "changed")

    # create the rule
    rule = Rule(
        "T210413_035_001",
        "T210413_035_001",
        [condition_1, condition_2],
        ALL,
        [action],
        [],
        None,
    )
    rules = Rules([rule])

    with fixture("T210413_035_001.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # test header
    matches = output_tree.xpath("/Invoice/Header/Parties/VendorParty/Name")
    assert len(matches) == 1
    assert matches[0].text == "Prodrive"

    # test lines
    lines = output_tree.xpath("Line")
    assert len(lines) == 3
    assert lines[0].xpath("LineNumber")[0].text == "10000"
    assert lines[0].xpath("OrderNumber")[0].text == "101094786"
    assert lines[0].xpath("OrderLineNumber")[0].text == "changed"
    assert lines[1].xpath("LineNumber")[0].text == "20000"
    assert lines[1].xpath("OrderNumber")[0].text == "101094786"
    assert lines[1].xpath("OrderLineNumber")[0].text == "changed"
    assert lines[2].xpath("LineNumber")[0].text == "30000"
    assert lines[2].xpath("OrderNumber")[0].text == "101094786"
    assert lines[2].xpath("OrderLineNumber")[0].text is None

    # test used rule
    used_rules = output_tree.xpath("BusinessRules")[0].xpath("Rule")
    assert len(used_rules) == 1
    assert used_rules[0].xpath("Title")[0].text == "T210413_035_001"


def test_T210907_001_1():
    # if taxamount smaller then "0.00000001" then set taxpercentage to "0.00000000"
    condition = Condition(
        field_registry.get("tax_amount"),
        operator_registry.get("decimal_smaller_then"),
        Decimal("0.00000001"),
    )
    action = ActionWithValue(
        action_registry.get("set_decimal"),
        field_registry.get("tax_percent"),
        Decimal("0.00000000"),
    )

    # execute rule
    rules = Rules([Rule("T210907_001", "T210907_001", [condition], ALL, [action], [], None)])
    with fixture("T210907_001.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # test output (as string!)
    tax_amount = output_tree.xpath("/Invoice/Header/Tax/TotalTax")[0].text
    tax_percent = output_tree.xpath("/Invoice/Header/Tax/TotalTax/@percentquantity")[0]
    assert tax_amount == "0"
    assert tax_percent == "0"


def test_T210907_001_2():
    # if taxamount smaller then "0.00000000" then set taxpercentage to "0.00000000"
    condition = Condition(
        field_registry.get("tax_amount"),
        operator_registry.get("decimal_smaller_then"),
        Decimal("0.00000000"),
    )
    action = ActionWithValue(
        action_registry.get("set_decimal"),
        field_registry.get("tax_percent"),
        Decimal("0.00000000"),
    )

    # execute rule
    rules = Rules([Rule("T210907_001", "T210907_001", [condition], ALL, [action], [], None)])
    with fixture("T210907_001.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # test output (as string!)
    tax_amount = output_tree.xpath("/Invoice/Header/Tax/TotalTax")[0].text
    tax_percent = output_tree.xpath("/Invoice/Header/Tax/TotalTax/@percentquantity")[0]
    assert tax_amount == "0"
    assert tax_percent == ""  # Nothing executed


def test_T210907_001_3():
    # if taxamount equals "0.00000000" then set taxpercentage to "0.00000000"
    condition = Condition(
        field_registry.get("tax_amount"),
        operator_registry.get("decimal_equals"),
        Decimal("0.00000000"),
    )
    action = ActionWithValue(
        action_registry.get("set_decimal"),
        field_registry.get("tax_percent"),
        Decimal("0.00000000"),
    )

    # execute rule
    rules = Rules([Rule("T210907_001", "T210907_001", [condition], ALL, [action], [], None)])
    with fixture("T210907_001.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # test output (as string!)
    tax_amount = output_tree.xpath("/Invoice/Header/Tax/TotalTax")[0].text
    tax_percent = output_tree.xpath("/Invoice/Header/Tax/TotalTax/@percentquantity")[0]
    assert tax_amount == "0"
    assert tax_percent == "0"
