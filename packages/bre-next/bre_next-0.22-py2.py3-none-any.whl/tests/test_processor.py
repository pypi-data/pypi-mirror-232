import io
import os
from decimal import Decimal
from functools import partial
from shutil import copytree

from lxml import etree

from bre.actions import action_registry
from bre.core import ALL, ActionWithValue, Condition, Rule, Rules
from bre.operators import operator_registry
from bre.processor import Processor

from .fields import field_registry
from .utils import fixture


def test_processor(tmpdir, caplog):
    broken_xml = fixture("integration/broken.xml")
    rule_active_xml = fixture("integration/rule_active.xml")
    rule_inactive_xml = fixture("integration/rule_inactive.xml")

    action = action_registry.get("set_str")
    field = field_registry.get("currency_code")
    action_with_value = ActionWithValue(action, field, "GBP")
    operator = operator_registry.get("str_equals")
    field = field_registry.get("vendor_number")
    condition = Condition(field, operator, "100004")

    rule1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule1])

    processor = Processor(rules)
    broken_xml_output = processor.perform(broken_xml, "broken.xml")
    rule_active_xml_output = processor.perform(rule_active_xml, "rule_active.xml")
    rule_inactive_xml_output = processor.perform(rule_inactive_xml, "rule_inactive.xml")

    currency_code = field_registry.get("currency_code").get(etree.parse(rule_active_xml_output))
    assert currency_code == "GBP"

    assert broken_xml_output is None
    rule_inactive_xml = fixture("integration/rule_inactive.xml")
    assert rule_inactive_xml.read() == rule_inactive_xml_output.getvalue()

    assert "Error processing broken.xml" in caplog.text


def test_processor_with_header_and_line_rule(tmpdir, caplog):
    input_xml = fixture("technische_unie_smaller_than.xml")

    action = action_registry.get("absolute_decimal")
    field = field_registry.get("line_quantity")
    action_with_value = ActionWithValue(action, field, None)

    operator = operator_registry.get("str_equals")
    field = field_registry.get("scan_source")
    condition_1 = Condition(field, operator, "EDI")

    operator = operator_registry.get("decimal_smaller_then")
    field = field_registry.get("line_quantity")
    condition_2 = Condition(field, operator, "0.00000000")

    rule1 = Rule("Rule1", "Rule1", [condition_1, condition_2], ALL, [action_with_value], [], None)
    rules = Rules([rule1])

    processor = Processor(rules)
    output_xml = processor.perform(input_xml, "output.xml")

    line_quantity = field_registry.get("line_quantity").get(etree.parse(output_xml))
    assert line_quantity == Decimal("1")
