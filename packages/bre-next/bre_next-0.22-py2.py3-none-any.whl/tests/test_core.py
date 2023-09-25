# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal

import pytest
from lxml import etree

from bre import datatypes
from bre.actions import action_registry
from bre.core import (
    ALL,
    ANY,
    Action,
    ActionRegistry,
    ActionWithValue,
    Condition,
    Error,
    Field,
    FieldRegistry,
    Operator,
    OperatorRegistry,
    Rule,
    Rules,
)
from bre.operators import operator_registry

from .fields import field_registry
from .utils import fixture


class MockField:
    def __init__(self, id, label, datatype, value):
        self.id = id
        self.label = label
        self.datatype = datatype
        self.value = value
        self._type = "Dummy"

    def get(self, tree):
        return self.value

    def manipulators(self, tree, source_field):
        return [MockManipulator(self)]

    def is_allowed_choice(self, value):
        return True

    def is_header_field(self):
        return True

    def is_line_field(self):
        return False

    def is_linecoding_field(self):
        return False

    def is_order_field(self):
        return False


class MockManipulator:
    def __init__(self, field):
        self.field = field
        self.first = True

    def get(self):
        return self.field.value

    def set(self, value):
        self.field.value = value

    def get_element(self):
        return None


def test_core_simple():
    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    field = MockField("a", "A", datatypes.String, "A")
    condition = Condition(field, operator, "A")

    def action_func(manipulator, value, source_field=None):
        manipulator.set(value)

    field2 = MockField("b", "B", datatypes.String, "B")

    action = Action("a", "A", datatypes.String, None, action_func)
    action_with_value = ActionWithValue(action, field2, "C")
    rule1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rule2 = Rule("Rule2", "Description2", [condition], ANY, [action_with_value], [], None)
    rule3 = Rule("Rule3", "Description3", [condition], None, [action_with_value], [], None)

    empty_xml = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Invoice><Header></Header></Invoice>
    """
    tree = etree.fromstring(empty_xml)

    rule1.perform(None, tree)
    assert field2.value == "C"

    rule2.perform(None, tree)
    assert field2.value == "C"

    with pytest.raises(Error):
        rule3.perform(None, tree)


def test_field_get_str():
    field = Field("a", "A", datatypes.String, "/Invoice/Header/CompCodeFin")
    with fixture("invoice.xml") as f:
        input_tree = etree.parse(f)
    assert field.get(input_tree) == "998"


def test_field_get_str_default():
    field = Field("a", "A", datatypes.String, "/Invoice/Header/NotThere")
    with fixture("invoice.xml") as f:
        input_tree = etree.parse(f)
    assert field.get(input_tree) == ""


def test_field_get_date():
    field = Field("a", "A", datatypes.Date, "/Invoice/Header/InvoiceDate")
    with fixture("invoice.xml") as f:
        input_tree = etree.parse(f)
    assert field.get(input_tree) == date(2012, 6, 1)


def test_field_set_str():
    field = Field("a", "A", datatypes.String, "/Invoice/Header/CompCodeFin")
    with fixture("invoice.xml") as f:
        input_tree = etree.parse(f)
    field.manipulators(input_tree, None)[0].set("1000")
    assert field.get(input_tree) == "1000"


def test_field_set_date():
    field = Field("a", "A", datatypes.Date, "/Invoice/Header/InvoiceDate")
    with fixture("invoice.xml") as f:
        input_tree = etree.parse(f)
    field.manipulators(input_tree, None)[0].set(date(2017, 1, 1))
    assert field.get(input_tree) == date(2017, 1, 1)


def test_field_set_new_element():
    field = Field("a", "A", datatypes.String, "/tree/foo")
    tree = etree.fromstring("<tree></tree>")
    field.manipulators(tree, None)[0].set("value")
    assert field.get(tree) == "value"
    assert etree.tostring(tree) == b"<tree><foo>value</foo></tree>"


def test_field_get_attribute():
    field = Field("a", "A", datatypes.String, "/Invoice/Header/TotalAmount", "currency")
    with fixture("invoice.xml") as f:
        input_tree = etree.parse(f)
    assert field.get(input_tree) == "EUR"


def test_field_set_attribute():
    field = Field("a", "A", datatypes.String, "/Invoice/Header/TotalAmount", "currency")
    with fixture("invoice.xml") as f:
        input_tree = etree.parse(f)
    field.manipulators(input_tree, None)[0].set("GPB")
    assert field.get(input_tree) == "GPB"


def test_field_set_new_attribute():
    # create an element for an attribute field
    field = Field("a", "A", datatypes.String, "/tree/foo", "val")
    tree = etree.fromstring("<tree></tree>")
    field.manipulators(tree, None)[0].set("value")
    assert field.get(tree) == "value"
    assert etree.tostring(tree) == b'<tree><foo val="value"/></tree>'


def test_wrong_compare_value():
    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    field = MockField("a", "A", datatypes.String, "A")
    condition = Condition(field, operator, "B")

    def action_func(manipulator, value):
        assert False

    field2 = MockField("b", "B", datatypes.String, "B")
    action = Action("a", "A", datatypes.String, None, action_func)
    action_with_value = ActionWithValue(action, field2, "C")
    rule1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rule2 = Rule("Rule2", "Description2", [condition], ANY, [action_with_value], [], None)

    class Tree:
        value = None

    tree = Tree()

    rule1.perform(None, tree)
    assert tree.value is None

    rule2.perform(None, tree)
    assert tree.value is None


def test_field_limits_operators():
    field_a = Field("a", "A", datatypes.Decimal, "/foo")
    field_b = Field("b", "B", datatypes.String, "/foo")

    operator_registry = OperatorRegistry()

    @operator_registry.register("equals", datatypes.Decimal, datatypes.Decimal)
    def decimal_equals(extracted_value, compare_value):
        return extracted_value == compare_value

    @operator_registry.register("startwith", datatypes.String, datatypes.String)
    def start_with(extracted_value, compare_value):
        return extracted_value.startswith(compare_value)

    assert set(operator_registry.all()) == set(
        [operator_registry.get("decimal_equals"), operator_registry.get("start_with")]
    )

    operators_a = field_a.get_allowed_operators(operator_registry)
    operators_b = field_b.get_allowed_operators(operator_registry)
    assert len(operators_a) == 1
    assert len(operators_b) == 1
    assert list(operators_a)[0].id == "decimal_equals"
    assert list(operators_b)[0].id == "start_with"


def test_field_choices_limits_operators():
    field_a = Field("a", "A", datatypes.String, "/foo", choices=[("foo", "Foo")])
    field_b = Field("b", "B", datatypes.String, "/foo")

    operator_registry = OperatorRegistry()

    @operator_registry.register("x", datatypes.String, datatypes.String)
    def x(extracted_value, compare_value):
        return True

    @operator_registry.register("y", datatypes.String, datatypes.String, for_choices=True)
    def y(extracted_value, compare_value):
        return True

    assert set(operator_registry.all()) == set([operator_registry.get("x"), operator_registry.get("y")])

    assert field_a.get_allowed_operators(operator_registry) == set([operator_registry.get("y")])

    assert field_b.get_allowed_operators(operator_registry) == set(
        [operator_registry.get("x"), operator_registry.get("y")]
    )


def test_field_choices_limits_actions():
    field_a = Field("a", "A", datatypes.String, "/foo", choices=[("foo", "Foo")])
    field_b = Field("b", "B", datatypes.String, "/foo")

    action_registry = ActionRegistry()

    @action_registry.register("x", datatypes.String, datatypes.String)
    def x():
        pass

    @action_registry.register("y", datatypes.String, datatypes.String, for_choices=True)
    def y():
        pass

    assert set(action_registry.all()) == set([action_registry.get("x"), action_registry.get("y")])

    assert field_a.get_allowed_actions(action_registry) == set([action_registry.get("y")])

    assert field_b.get_allowed_actions(action_registry) == set([action_registry.get("x"), action_registry.get("y")])


def test_field_limits_actions():
    field_a = Field("a", "A", datatypes.Decimal, "/foo")
    field_b = Field("b", "B", datatypes.String, "/foo")

    action_registry = ActionRegistry()

    @action_registry.register("Set decimal", datatypes.Decimal, datatypes.Decimal, 0)
    def set_decimal(tree, field, value):
        pass

    @action_registry.register("Set str", datatypes.String, datatypes.String, 0)
    def set_str(tree, field, value):
        pass

    actions_a = field_a.get_allowed_actions(action_registry)
    actions_b = field_b.get_allowed_actions(action_registry)
    assert len(actions_a) == 1
    assert len(actions_b) == 1
    assert list(actions_a)[0].id == "set_decimal"
    assert list(actions_b)[0].id == "set_str"


def test_rule_with_zero_value():
    field = field_registry.get("invoice_amount")

    operator = operator_registry.get("decimal_smaller_then")
    condition = Condition(field, operator, Decimal("0.00000000"))

    rule1 = Rule("Rule1", "Description1", [condition], ALL, [], [], None)
    rules = Rules([rule1])
    with fixture("NEXTIN-4977.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)
    assert field.get(output_tree) < Decimal("0.00000000")


def test_rule_with_xml():
    def action_func(manipulator, value, source_field=None):
        value = manipulator.get()
        manipulator.set("X" + value)

    field = field_registry.get("vendor_invoice_number")
    action = Action("a", "A", datatypes.String, None, action_func)
    action_with_value = ActionWithValue(action, field, None)
    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition = Condition(field, operator, "2012 00696")
    rule1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule1])
    with fixture("invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)
    assert field.get(output_tree) == "X2012 00696"


def test_rule_with_xml_and_real_action():
    field = field_registry.get("vendor_invoice_number")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, field, "new value")
    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition = Condition(field, operator, "2012 00696")
    rule1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule1])
    with fixture("invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)
    assert field.get(output_tree) == "new value"


def test_conditions_empty_value():
    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    field = field_registry.get("vendor_invoice_date")
    condition = Condition(field, operator, "2012-06-01")
    rule1 = Rule("Rule1", "Description1", [condition], ALL, None, [], None)
    rules = Rules([rule1])

    empty_xml = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Invoice><Header></Header></Invoice>
    """
    input_tree = etree.fromstring(empty_xml)

    output_tree = rules.perform(input_tree)
    assert field.get(output_tree) is None


def test_actions_all():
    registry = ActionRegistry()
    assert registry.all() is not None


def test_fields_all():
    registry = FieldRegistry()
    assert registry.all() is not None


def test_field_action_set_choices():
    operator = Operator("equals", "Equals", lambda a, b: a == b, datatypes.String, datatypes.String)
    field = Field("a", "A", datatypes.String, "/Invoice/Header/A")
    condition = Condition(field, operator, "Value")

    field2 = Field(
        "b",
        "B",
        datatypes.String,
        "/Invoice/Header/B",
        choices=[("True", "true"), ("False", "false")],
    )

    action = action_registry.get("set_str")
    with pytest.raises(Error):
        ActionWithValue(action, field2, "nonsense")
    action_with_value = ActionWithValue(action, field2, "true")
    rule1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule1])
    empty_xml = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Invoice><Header><A>Value</A></Header></Invoice>
    """
    input_tree = etree.fromstring(empty_xml)
    output_tree = rules.perform(input_tree)
    assert field2.get(output_tree) == "true"


def test_linecoding_from_header():
    source_field_header = field_registry.get("vendor_invoice_number")
    source_field_line = field_registry.get("line_UserArea02")
    target_field = field_registry.get("linecoding_description")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "new value")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition_header = Condition(source_field_header, operator, "999999")
    condition_line = Condition(source_field_line, operator, "bar")
    rule1 = Rule(
        "Rule1",
        "Decritpion1",
        [condition_header, condition_line],
        ALL,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule1])

    with fixture("invoice_linecoding.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    output_matched_manipulators = source_field_header.manipulators(output_tree, None)
    assert len(output_matched_manipulators) == 1

    # since out test xml has one predefined LineCoding field, we need
    # the second instance for assertion
    assert (output_tree.xpath("LineCoding")[1].xpath("Description")[0].text) == "new value"
    assert (output_tree.xpath("LineCoding")[1].xpath("LineNumber")[0].text) == "2"


def test_no_linecoding_without_action():
    source_field_header = field_registry.get("vendor_invoice_number")
    source_field_line = field_registry.get("line_UserArea02")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition_header = Condition(source_field_header, operator, "999999")
    condition_line = Condition(source_field_line, operator, "bar")
    rule1 = Rule("Rule1", "Decritpion1", [condition_header, condition_line], ALL, [], [], None)
    rules = Rules([rule1])

    with fixture("invoice_linecoding.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    output_matched_manipulators = source_field_header.manipulators(output_tree, None)
    assert len(output_matched_manipulators) == 1

    # since out test xml has one predefined LineCoding field, we need
    # to make sure no extra linecodings were created
    assert len(output_tree.xpath("LineCoding")) == 1


def test_subrule_execution_with_matching_header():
    source_field_header = field_registry.get("vendor_invoice_number")
    source_field_line = field_registry.get("line_UserArea02")
    target_field = field_registry.get("linecoding_description")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "new value")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition_header = Condition(source_field_header, operator, "999999")
    condition_line = Condition(source_field_line, operator, "bar")

    subrule = Rule("Subrule", "Subrule test", [condition_line], ALL, [action_with_value], [], None)

    rule1 = Rule("Rule1", "Decritpion1", [condition_header], ALL, [], [subrule], None)

    rules = Rules([rule1])

    with fixture("invoice_linecoding.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    output_matched_manipulators = source_field_header.manipulators(output_tree, None)
    assert len(output_matched_manipulators) == 1

    # since out test xml has one predefined LineCoding field, we need
    # the second instance for assertion
    assert (output_tree.xpath("LineCoding")[1].xpath("Description")[0].text) == "new value"
    assert (output_tree.xpath("LineCoding")[1].xpath("LineNumber")[0].text) == "2"


def test_no_subrule_execution_without_main_rule_match():
    source_field_header = field_registry.get("vendor_invoice_number")
    source_field_line = field_registry.get("line_UserArea02")
    target_field = field_registry.get("linecoding_description")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "new value")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition_header = Condition(source_field_header, operator, "not_a_match")
    condition_line = Condition(source_field_line, operator, "bar")

    subrule = Rule("Subrule", "Subrule test", [condition_line], ALL, [action_with_value], [], None)

    rule1 = Rule("Rule1", "Decritpion1", [condition_header], ALL, [], [subrule], None)

    rules = Rules([rule1])

    with fixture("invoice_linecoding.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)
    assert len(output_tree.xpath("//LineCoding")) == 1


def test_linecoding_from_header_no_lines():
    source_field_header = field_registry.get("vendor_invoice_number")
    source_field_line = field_registry.get("line_UserArea02")
    target_field = field_registry.get("linecoding_description")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "new value")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition_header = Condition(source_field_header, operator, "999999")
    condition_line = Condition(source_field_line, operator, "bar")
    rule1 = Rule(
        "Rule1",
        "Decritpion1",
        [condition_header, condition_line],
        ALL,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule1])

    dummy_xml = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Invoice>
<Header><InvoiceNumber>999999</InvoiceNumber></Header>
</Invoice>
    """
    input_tree = etree.fromstring(dummy_xml).getroottree()
    output_tree = rules.perform(input_tree)
    assert len(output_tree.xpath("//LineCoding")) == 0
    # Here put a test that raises an exception since LineCoding cannot be
    # formed from a Header alone.


def test_linecoding_from_header_no_matching_lines():
    source_field_header = field_registry.get("vendor_invoice_number")
    source_field_line = field_registry.get("line_UserArea02")
    target_field = field_registry.get("linecoding_description")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "new value")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition_header = Condition(source_field_header, operator, "999999")
    condition_line = Condition(source_field_line, operator, "bar")
    rule1 = Rule(
        "Rule1",
        "Decritpion1",
        [condition_header, condition_line],
        ALL,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule1])

    dummy_xml = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Invoice>
<Header><InvoiceNumber>999999</InvoiceNumber></Header>
<Line><UserArea02>foo</UserArea02></Line>
</Invoice>
    """
    input_tree = etree.fromstring(dummy_xml).getroottree()
    output_tree = rules.perform(input_tree)
    assert len(output_tree.xpath("//LineCoding")) == 0
    # Here put a test that raises an exception since LineCoding cannot be
    # formed from a Header alone.


def test_linecoding_from_line():
    source_field = field_registry.get("line_UserArea02")
    target_field = field_registry.get("linecoding_description")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "new value")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition = Condition(source_field, operator, "bar")
    rule1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule1])

    with fixture("invoice_linecoding.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    output_matched_manipulators = source_field.manipulators(output_tree, None)

    # Make sure we have matches to verify
    assert len(output_matched_manipulators) == 1

    # Check if all source matches were changed
    for source_manipulator in output_matched_manipulators:
        assert target_field.get(source_manipulator.get_element().getparent()) == "new value"


def test_linecoding_from_header_and_2_lines():
    source_field_header = field_registry.get("vendor_invoice_number")
    source_field_line_1 = field_registry.get("line_UserArea01")
    source_field_line_2 = field_registry.get("line_UserArea02")
    target_field = field_registry.get("linecoding_description")

    action = action_registry.get("set_str")
    action_with_value1 = ActionWithValue(action, target_field, "", source_field_header)
    action_with_value2 = ActionWithValue(action, target_field, "", source_field_header)

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition1 = Condition(source_field_line_1, operator, "foo")
    condition2 = Condition(source_field_line_2, operator, "bar")

    rule1 = Rule("Rule1", "Description1", [condition1], ALL, [action_with_value1], [], None)
    rule2 = Rule("Rule2", "Description2", [condition2], ALL, [action_with_value2], [], None)
    rules = Rules([rule1, rule2])

    with fixture("invoice_linecoding.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    output_matched_manipulators1 = source_field_line_1.manipulators(output_tree, None)
    output_matched_manipulators2 = source_field_line_2.manipulators(output_tree, None)

    assert len(output_matched_manipulators1) == 2
    assert len(output_matched_manipulators2) == 1

    for source_manipulator in output_matched_manipulators1:
        assert target_field.get(source_manipulator.get_element().getparent()) == "999999"

    for source_manipulator in output_matched_manipulators2:
        assert target_field.get(source_manipulator.get_element().getparent()) == "999999"


def test_linecoding_with_linenumber_in_line():
    source_field1 = field_registry.get("line_UserArea03")
    source_field2 = field_registry.get("line_UserArea04")
    target_field = field_registry.get("linecoding_description")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "new_value")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition1 = Condition(source_field1, operator, "foobar")
    condition2 = Condition(source_field2, operator, "barfoo")

    rule = Rule(
        "Rule1",
        "Bre01_and_Bre02",
        [condition1, condition2],
        ALL,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule])

    with fixture("invoice_linecoding.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    output_matched_manipulators = source_field1.manipulators(output_tree, None)
    assert len(output_matched_manipulators) == 1

    for source_manipulator in output_matched_manipulators:
        assert target_field.get(source_manipulator.get_element().getparent()) == "new_value"

    output_matched_manipulators = source_field2.manipulators(output_tree, None)
    assert len(output_matched_manipulators) == 1

    for source_manipulator in output_matched_manipulators:
        assert target_field.get(source_manipulator.get_element().getparent()) == "new_value"
        # New lineCoding is created on top of the existing one.
        # The existing one has LineNumber 1, the new one LineNumber 50
        # assert that both exist (one old, one created)
        assert len(output_tree.xpath("LineCoding")) == 2
        linecoding_elements = output_tree.xpath("LineCoding")
        linecoding_numbers = ["1", "50"]
        for element in linecoding_elements:
            assert element.xpath("LineNumber")[0].text in linecoding_numbers
            linecoding_numbers.remove(element.xpath("LineNumber")[0].text)


def test_linecoding_something_of_everything():
    # This test will test a lot of basic funcionalities:
    # Copying of a line-element in the linecoding_elements
    # Setting of a line-coding element based on a header element
    # Making linecodes, one with a new LineNumber not in the line
    # and one with a linenumber already in the line
    # and one with a predefined linenumber which is updated.
    source_field_header = field_registry.get("vendor_invoice_number")
    source_field_line_1 = field_registry.get("line_UserArea01")
    source_field_line_5 = field_registry.get("line_UserArea05")
    target_field_description = field_registry.get("linecoding_description")
    target_field_taxcode = field_registry.get("linecoding_taxcode")

    action_set = action_registry.get("set_str")
    action_with_value = ActionWithValue(action_set, target_field_taxcode, "Ipsum")
    action_with_copy = ActionWithValue(action_set, target_field_description, "", source_field_header)
    operator = Operator("equals", "equals", lambda a, b: a == b, None, None)
    condition1 = Condition(source_field_line_1, operator, "foo")
    condition2 = Condition(source_field_line_5, operator, "Lorem")
    condition3 = Condition(source_field_header, operator, "999999")
    rule1 = Rule("Rule1", "Rule1", [condition1, condition3], ALL, [action_with_value], [], None)
    rule2 = Rule("Rule2", "Rule2", [condition2, condition3], ALL, [action_with_copy], [], None)
    rules = Rules([rule1, rule2])

    with fixture("invoice_linecoding.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)
    # The first tule to be performed is on two lines with UserArea01
    # and those line-codings need to contain TaxCode == "Ipsum"
    # The second tule will create a LineCoding with LineNumber 5
    # and in the Description an copy of the Invoice Number.
    assert (output_tree.xpath("LineCoding")[0].xpath("TaxCode")[0].text) == "Ipsum"
    assert (output_tree.xpath("LineCoding")[0].xpath("LineNumber")[0].text) == "1"
    assert (output_tree.xpath("LineCoding")[1].xpath("TaxCode")[0].text) == "Ipsum"
    assert (output_tree.xpath("LineCoding")[1].xpath("LineNumber")[0].text) == "2"
    assert (output_tree.xpath("LineCoding")[2].xpath("Description")[0].text) == source_field_header.get(output_tree)
    assert (output_tree.xpath("LineCoding")[2].xpath("LineNumber")[0].text) == "5"


def test_set_additionalfield_generic_1():
    invoice_number = field_registry.get("vendor_invoice_number")
    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition = Condition(invoice_number, operator, "201200696")

    generic_1 = field_registry.get("generic_1")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, generic_1, "new value")

    rule1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule1])

    with fixture("invoice2.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)
    assert generic_1.get(output_tree) == "new value"


def test_order_action_to_linecoding():
    source_field = field_registry.get("order_order_number")
    target_field = field_registry.get("linecoding_project")

    action = action_registry.get("set_str")
    action_with_value1 = ActionWithValue(action, target_field, "Project Foo")
    action_with_value2 = ActionWithValue(action, target_field, "Project Bar")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition1 = Condition(source_field, operator, "0011600006")
    condition2 = Condition(source_field, operator, "0011600007")

    rule1 = Rule("Rule1", "Description1", [condition1], ALL, [action_with_value1], [], None)
    rule2 = Rule("Rule2", "Description2", [condition2], ALL, [action_with_value2], [], None)
    rules = Rules([rule1, rule2])

    with fixture("multivalue.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # We expect that the OrderNumbers create LineCodings. In this linecodings, a Project
    # field is set and the OrderNumber it applies to is copied to the line as well
    coding_lines = output_tree.xpath("LineCoding")

    # sanity check to assert no Lines are created
    assert len(output_tree.xpath("Line")) == 0
    assert len(coding_lines) == 2
    assert coding_lines[0].xpath("OrderNumber")[0].text == "0011600006"
    assert coding_lines[0].xpath("Project")[0].text == "Project Foo"
    assert coding_lines[1].xpath("OrderNumber")[0].text == "0011600007"
    assert coding_lines[1].xpath("Project")[0].text == "Project Bar"

    rules = output_tree.xpath("BusinessRules")[0].xpath("Rule")
    assert len(rules) == 2
    assert rules[0].xpath("Title")[0].text == "Rule1"
    assert rules[1].xpath("Title")[0].text == "Rule2"


def test_order_action_to_linecoding_same_condition():
    source_field = field_registry.get("order_order_number")
    target_field = field_registry.get("linecoding_project")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "Project Foo")

    operator = Operator("not_equals", "Not equals", lambda a, b: a != b, None, None)
    condition = Condition(source_field, operator, "No project has this number")

    rule = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule])

    with fixture("multivalue.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # We expect that the OrderNumbers create LineCodings. In this linecodings, a Project
    # field is set and the OrderNumber it applies to is copied to the line as well
    coding_lines = output_tree.xpath("LineCoding")

    assert len(coding_lines) == 2
    assert coding_lines[0].xpath("OrderNumber")[0].text == "0011600006"
    assert coding_lines[0].xpath("Project")[0].text == "Project Foo"
    assert coding_lines[1].xpath("OrderNumber")[0].text == "0011600007"
    assert coding_lines[1].xpath("Project")[0].text == "Project Foo"

    rules = output_tree.xpath("BusinessRules")[0].xpath("Rule")
    assert len(rules) == 1
    assert rules[0].xpath("Title")[0].text == "Rule1"


def test_action_based_on_order_and_line_condition():
    order_source_field = field_registry.get("order_order_number")
    line_source_field = field_registry.get("line_UserArea01")
    target_field = field_registry.get("linecoding_description")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "bar")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition1 = Condition(order_source_field, operator, "0011600006")
    condition2 = Condition(line_source_field, operator, "foo")

    rule = Rule(
        "Rule1",
        "Description1",
        [condition1, condition2],
        ALL,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule])

    with fixture("multivalue_with_lines.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    coding_lines = output_tree.xpath("LineCoding")

    assert len(coding_lines) == 2
    assert coding_lines[0].xpath("LineNumber")[0].text == "1"
    assert coding_lines[0].xpath("Description")[0].text == "bar"
    assert coding_lines[1].xpath("OrderNumber")[0].text == "0011600006"
    assert coding_lines[1].xpath("Description")[0].text == "bar"

    rules = output_tree.xpath("BusinessRules")[0].xpath("Rule")
    assert len(rules) == 1
    assert rules[0].xpath("Title")[0].text == "Rule1"


def test_empty_conditions_dont_trigger_linecoding_actions():
    # ISP-4762 -- when having a condition on OrderNumber only, the Line conditions would be empty
    # and thus always trigger. Same happens vice versa. This should not happen.
    order_source_field = field_registry.get("order_order_number")
    target_field = field_registry.get("linecoding_description")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "bar")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition1 = Condition(order_source_field, operator, "0011600006")

    rule = Rule("Rule1", "Description1", [condition1], ALL, [action_with_value], [], None)
    rules = Rules([rule])

    with fixture("multivalue_with_lines.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    coding_lines = output_tree.xpath("LineCoding")

    assert len(coding_lines) == 1
    assert coding_lines[0].xpath("OrderNumber")[0].text == "0011600006"
    assert coding_lines[0].xpath("Description")[0].text == "bar"


def test_order_condition_targets_a_header_field():
    order_source_field = field_registry.get("order_order_number")
    target_field = field_registry.get("vendor_number")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "bar")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition = Condition(order_source_field, operator, "0011600006")

    rule = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule])

    with fixture("multivalue.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    coding_lines = output_tree.xpath("LineCoding")

    assert len(coding_lines) == 0
    assert target_field.get(output_tree) == "bar"


def test_order_type_targets_equivalent_in_header():
    order_source_field = field_registry.get("order_order_number")
    target_field = field_registry.get("order_number")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "Changed")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition = Condition(order_source_field, operator, "0011600006")

    rule = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule])

    with fixture("multivalue.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    coding_lines = output_tree.xpath("LineCoding")

    assert len(coding_lines) == 0
    assert target_field.get(output_tree) == "Changed"


def test_condition_on_order_field_not_added_to_executed_rules_if_not_executed():
    # To determine which rules are applied, we check the header_conditions. But
    # if a rule is based on ORDER fields, the header conditions would always match
    source_field = field_registry.get("order_order_number")
    target_field = field_registry.get("linecoding_project")

    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "Project Nonexistent")

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition = Condition(source_field, operator, "No Match")

    rule1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule1])

    with fixture("multivalue.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # We expect that the OrderNumbers create LineCodings. In this linecodings, a Project
    # field is set and the OrderNumber it applies to is copied to the line as well
    coding_lines = output_tree.xpath("LineCoding")

    # sanity check to assert no Lines are created
    assert len(output_tree.xpath("Line")) == 0
    assert len(coding_lines) == 0

    assert len(output_tree.xpath("BusinessRules")) == 0


def test_two_rules_header_condition_order_condition_no_matches():
    # Order rule
    source_field1 = field_registry.get("order_order_number")
    target_field1 = field_registry.get("linecoding_project")

    action1 = action_registry.get("set_str")
    action_with_value1 = ActionWithValue(action1, target_field1, "Project Nonexistent")

    operator1 = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition1 = Condition(source_field1, operator1, "No Match")

    rule1 = Rule("Rule1", "Description1", [condition1], ALL, [action_with_value1], [], None)

    # Header rule
    source_field2 = field_registry.get("debit_credit")
    target_field2 = field_registry.get("vendor_number")

    action2 = action_registry.get("set_str")
    action_with_value2 = ActionWithValue(action2, target_field2, "Neither credit nor debit")

    operator2 = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition2 = Condition(source_field2, operator2, "No Match")

    rule2 = Rule("Rule2", "Description2", [condition2], ALL, [action_with_value2], [], None)

    rules = Rules([rule1, rule2])

    with fixture("multivalue.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # We expect that the OrderNumbers create LineCodings. In this linecodings, a Project
    # field is set and the OrderNumber it applies to is copied to the line as well
    coding_lines = output_tree.xpath("LineCoding")

    # sanity check to assert no Lines are created
    assert len(output_tree.xpath("Line")) == 0
    assert len(coding_lines) == 0

    assert len(output_tree.xpath("BusinessRules")) == 0


def test_clean_ordernumber_in_first_line():
    source_field = field_registry.get("line_ordernumber")
    target_field = field_registry.get("line_ordernumber")

    action = action_registry.get("string_left_integer")
    action_with_value = ActionWithValue(action, source_field, 9)

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition = Condition(source_field, operator, "30095280/36.20.93")

    rule = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule])

    with fixture("logistic_invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    lines = output_tree.xpath("Line")

    assert len(lines) == 2
    assert lines[0].xpath("LineNumber")[0].text == "10"
    assert lines[1].xpath("LineNumber")[0].text == "20"
    assert lines[0].xpath("OrderNumber")[0].text == "30095280"
    assert lines[1].xpath("OrderNumber")[0].text == "30099471/99.90.07"

    rules = output_tree.xpath("BusinessRules")[0].xpath("Rule")
    assert len(rules) == 1
    assert rules[0].xpath("Title")[0].text == "Rule1"


def test_clean_ordernumber_in_second_line():
    source_field = field_registry.get("line_ordernumber")
    target_field = field_registry.get("line_ordernumber")

    action = action_registry.get("string_left_integer")
    action_with_value = ActionWithValue(action, source_field, 9)

    operator = Operator("equals", "Equals", lambda a, b: a == b, None, None)
    condition = Condition(source_field, operator, "30099471/99.90.07")

    rule = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)
    rules = Rules([rule])

    with fixture("logistic_invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    lines = output_tree.xpath("Line")

    assert len(lines) == 2
    assert lines[0].xpath("LineNumber")[0].text == "10"
    assert lines[1].xpath("LineNumber")[0].text == "20"
    assert lines[0].xpath("OrderNumber")[0].text == "30095280/36.20.93"
    assert lines[1].xpath("OrderNumber")[0].text == "30099471"

    rules = output_tree.xpath("BusinessRules")[0].xpath("Rule")
    assert len(rules) == 1
    assert rules[0].xpath("Title")[0].text == "Rule1"


def test_clear_ordernumber():
    # rule: if order_number is not empty, then string_left_integer "9" to keep the first 8 characters
    # this should not clean the ordernumber if the order has already 8 or less characters
    operator_registry = OperatorRegistry()

    @operator_registry.register("str_is_not_empty", datatypes.String, datatypes.Null)
    def str_is_not_empty(extracted_value, compare_value):
        return extracted_value != ""

    # rule: if order_number in header is not empty, then string_left_integer "9" to keep the first 8 characters
    header_source_field = field_registry.get("order_number")
    operator = operator_registry.get("str_is_not_empty")
    condition_1 = Condition(header_source_field, operator, "")
    action = action_registry.get("string_left_integer")
    action_1 = ActionWithValue(action, header_source_field, 9)

    # rule: if order_number in line is not empty, then string_left_integer "9" to keep the first 8 characters
    line_source_field = field_registry.get("line_ordernumber")
    operator = operator_registry.get("str_is_not_empty")
    condition_2 = Condition(line_source_field, operator, "")
    action = action_registry.get("string_left_integer")
    action_2 = ActionWithValue(action, line_source_field, 9)

    # create the rule
    rule = Rule(
        "Rule1",
        "Description1",
        [condition_1, condition_2],
        ALL,
        [action_1, action_2],
        [],
        None,
    )
    rules = Rules([rule])

    # order_number is too long, should be stripped to 8 characters
    with fixture("technische_unie_invalid_ordernumber.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # test header
    matches = output_tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert len(matches) == 1
    assert matches[0].text == "30100009"

    # test lines
    lines = output_tree.xpath("Line")
    assert len(lines) == 1
    assert lines[0].xpath("LineNumber")[0].text == "20"
    assert lines[0].xpath("OrderNumber")[0].text == "30100009"

    # test used rule
    used_rules = output_tree.xpath("BusinessRules")[0].xpath("Rule")
    assert len(used_rules) == 1
    assert used_rules[0].xpath("Title")[0].text == "Rule1"

    # second invoice: order_number is already valid, should not be stripped
    with fixture("technische_unie_valid_ordernumber.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # test header
    matches = output_tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert len(matches) == 1
    assert matches[0].text == "30102328"

    # test lines
    lines = output_tree.xpath("Line")
    assert len(lines) == 1
    assert lines[0].xpath("LineNumber")[0].text == "20"
    assert lines[0].xpath("OrderNumber")[0].text == "30102328"

    # test used rule
    used_rules = output_tree.xpath("BusinessRules")[0].xpath("Rule")
    assert len(used_rules) == 1
    assert used_rules[0].xpath("Title")[0].text == "Rule1"

    # third invoice: has no lines, lines should not be created
    with fixture("technische_unie_valid_ordernumber_no_lines.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # test header
    matches = output_tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert len(matches) == 1
    assert matches[0].text == "30102330"

    # test lines
    lines = output_tree.xpath("Line")
    assert len(lines) == 0

    # test used rule. Rule1 does not apply, because it has a line condition
    used_rules = output_tree.xpath("BusinessRules")
    assert len(used_rules) == 0


def test_multiple_rules_for_the_same_field():
    # invoice_empty_tags.xml

    # Example from customer Schagen/Salverda:
    # Rule 1: set CompCodeFin to `301` if CompCodeFin is empty
    # Rule 2: set CompCodeFin to `251` if CompCodeFin is not `301`
    # Previous result: value is always 251, which is incorrect

    operator_registry = OperatorRegistry()

    @operator_registry.register("str_empty", datatypes.String, datatypes.Null)
    def str_empty(extracted_value, compare_value):
        return extracted_value == ""

    @operator_registry.register("str_not_equals", datatypes.String, datatypes.String, for_choices=True)
    def str_not_equals(extracted_value, compare_value):
        return extracted_value != compare_value

    # Rule 1: set CompCodeFin to `301` if CompCodeFin is empty
    source_field = field_registry.get("company_code")
    operator = operator_registry.get("str_empty")
    condition = Condition(source_field, operator, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, source_field, "301")
    rule_1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)

    # Rule 2: set CompCodeFin to `251` if CompCodeFin is not `301`
    source_field = field_registry.get("company_code")
    operator = operator_registry.get("str_not_equals")
    condition = Condition(source_field, operator, "301")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, source_field, "251")
    rule_2 = Rule("Rule2", "Description2", [condition], ALL, [action_with_value], [], None)

    # create the rules
    rules = Rules([rule_1, rule_2])

    # perform the rules
    with fixture("invoice_empty_tags.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # test, should return 301, and not 251, rule "2" is not executed
    matches = output_tree.xpath("/Invoice/Header/CompCodeFin")
    assert len(matches) == 1
    assert matches[0].text == "301"


def test_multiple_rules_for_the_same_field_inversed():
    # invoice_empty_tags.xml

    # Example from customer Schagen/Salverda:
    # Rule 1: set CompCodeFin to `251` if CompCodeFin is not `301`
    # Rule 2: set CompCodeFin to `301` if CompCodeFin is empty
    # Previous result: value is always 301, which is incorrect

    operator_registry = OperatorRegistry()

    @operator_registry.register("str_empty", datatypes.String, datatypes.Null)
    def str_empty(extracted_value, compare_value):
        return extracted_value == ""

    @operator_registry.register("str_not_equals", datatypes.String, datatypes.String, for_choices=True)
    def str_not_equals(extracted_value, compare_value):
        return extracted_value != compare_value

    # Rule 1: set CompCodeFin to `301` if CompCodeFin is empty
    source_field = field_registry.get("company_code")
    operator = operator_registry.get("str_empty")
    condition = Condition(source_field, operator, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, source_field, "301")
    rule_1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)

    # Rule 2: set CompCodeFin to `251` if CompCodeFin is not `301`
    source_field = field_registry.get("company_code")
    operator = operator_registry.get("str_not_equals")
    condition = Condition(source_field, operator, "301")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, source_field, "251")
    rule_2 = Rule("Rule2", "Description2", [condition], ALL, [action_with_value], [], None)

    # create the rules, in reversed order
    rules = Rules([rule_2, rule_1])

    # perform the rules
    with fixture("invoice_empty_tags.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # test, should return 251, and not 301, rule "1" is not executed
    matches = output_tree.xpath("/Invoice/Header/CompCodeFin")
    assert len(matches) == 1
    assert matches[0].text == "251"


def test_multiple_rules_for_the_same_field_both_executed():
    # invoice_empty_tags.xml

    # Example;
    # Rule 1: set CompCodeFin to `301` if CompCodeFin is empty
    # Rule 2: set CompCodeFin to `251` if CompCodeFin is `301`
    # Previous result: value is always 301, which is incorrect, the second rule is not executed

    operator_registry = OperatorRegistry()

    @operator_registry.register("str_empty", datatypes.String, datatypes.Null)
    def str_empty(extracted_value, compare_value):
        return extracted_value == ""

    @operator_registry.register("str_equals", datatypes.String, datatypes.String, for_choices=True)
    def str_equals(extracted_value, compare_value):
        return extracted_value == compare_value

    # Rule 1: set CompCodeFin to `301` if CompCodeFin is empty
    source_field = field_registry.get("company_code")
    operator = operator_registry.get("str_empty")
    condition = Condition(source_field, operator, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, source_field, "301")
    rule_1 = Rule("Rule1", "Description1", [condition], ALL, [action_with_value], [], None)

    # Rule 2: set CompCodeFin to `251` if CompCodeFin is `301`
    source_field = field_registry.get("company_code")
    operator = operator_registry.get("str_equals")
    condition = Condition(source_field, operator, "301")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, source_field, "251")
    rule_2 = Rule("Rule2", "Description2", [condition], ALL, [action_with_value], [], None)

    # create the rules
    rules = Rules([rule_1, rule_2])

    # perform the rules
    with fixture("invoice_empty_tags.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # test, should return 251 because the second rule has a condition set by the first rule
    matches = output_tree.xpath("/Invoice/Header/CompCodeFin")
    assert len(matches) == 1
    assert matches[0].text == "251"


def test_condition_header_and_line_field_all():
    header_source_field = field_registry.get("order_number")  # header_order_number
    line_source_field = field_registry.get("line_ordernumber")  # line_order_number
    target_field = field_registry.get("scan_operator")

    operator_registry = OperatorRegistry()

    @operator_registry.register("str_is_not_empty", datatypes.String, datatypes.Null)
    def str_is_not_empty(extracted_value, compare_value):
        return extracted_value != ""

    operator_not_empty = operator_registry.get("str_is_not_empty")

    @operator_registry.register("str_is_empty", datatypes.String, datatypes.Null)
    def str_is_empty(extracted_value, compare_value):
        return extracted_value == ""

    operator_empty = operator_registry.get("str_is_empty")

    # Rule1: if header_order_number and line_order_number are both not empty, then set ScanOperator to BOTH
    condition_1 = Condition(header_source_field, operator_not_empty, "")
    condition_2 = Condition(line_source_field, operator_not_empty, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "BOTH")
    rule = Rule(
        "Rule1",
        "Description1",
        [condition_1, condition_2],
        ALL,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule])

    # Rule1: perform
    with fixture("logistic_invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # Rule1: test ScanOperator, should be set to BOTH because both conditions apply
    scan_operator = field_registry.get("scan_operator").get(output_tree)
    assert scan_operator == "BOTH"

    # Rule2: if header_order_number is empty and line_order_number is not empty, then set ScanOperator to LINE
    condition_1 = Condition(header_source_field, operator_empty, "")
    condition_2 = Condition(line_source_field, operator_not_empty, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "LINE")
    rule = Rule(
        "Rule2",
        "Description2",
        [condition_1, condition_2],
        ALL,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule])

    # Rule2: perform
    with fixture("logistic_invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # Rule2: test ScanOperator, should not be modified because condition_1 does not apply
    scan_operator = field_registry.get("scan_operator").get(output_tree)
    assert scan_operator == "ORIGINAL"

    # Rule3: if header_order_number is not empty and line_order_number is empty, then set ScanOperator to HEAD
    condition_1 = Condition(header_source_field, operator_not_empty, "")
    condition_2 = Condition(line_source_field, operator_empty, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "HEAD")
    rule = Rule(
        "Rule3",
        "Description3",
        [condition_1, condition_2],
        ALL,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule])

    # Rule3: perform
    with fixture("logistic_invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # Rule3: test ScanOperator, should not be modified because condition_2 does not apply
    scan_operator = field_registry.get("scan_operator").get(output_tree)
    assert scan_operator == "ORIGINAL"

    # Rule4: if header_order_number and line_order_number are empty, then set ScanOperator to EMPTY
    condition_1 = Condition(header_source_field, operator_empty, "")
    condition_2 = Condition(line_source_field, operator_empty, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "EMPTY")
    rule = Rule(
        "Rule4",
        "Description4",
        [condition_1, condition_2],
        ALL,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule])

    # Rule4: perform
    with fixture("logistic_invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # Rule4: test ScanOperator, should not be modified because both conditions does not apply
    scan_operator = field_registry.get("scan_operator").get(output_tree)
    assert scan_operator == "ORIGINAL"


def test_condition_header_and_line_field_any():
    header_source_field = field_registry.get("order_number")  # header_order_number
    line_source_field = field_registry.get("line_ordernumber")  # line_order_number
    target_field = field_registry.get("scan_operator")

    operator_registry = OperatorRegistry()

    @operator_registry.register("str_is_not_empty", datatypes.String, datatypes.Null)
    def str_is_not_empty(extracted_value, compare_value):
        return extracted_value != ""

    operator_not_empty = operator_registry.get("str_is_not_empty")

    @operator_registry.register("str_is_empty", datatypes.String, datatypes.Null)
    def str_is_empty(extracted_value, compare_value):
        return extracted_value == ""

    operator_empty = operator_registry.get("str_is_empty")

    # Rule1: if header_order_number and line_order_number are both not empty, then set ScanOperator to BOTH
    condition_1 = Condition(header_source_field, operator_not_empty, "")
    condition_2 = Condition(line_source_field, operator_not_empty, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "BOTH")
    rule = Rule(
        "Rule1",
        "Description1",
        [condition_1, condition_2],
        ANY,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule])

    # Rule1: perform
    with fixture("logistic_invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # Rule1: test ScanOperator, should be set to BOTH because both conditions apply
    scan_operator = field_registry.get("scan_operator").get(output_tree)
    assert scan_operator == "BOTH"

    # Rule2: if header_order_number is empty and line_order_number is not empty, then set ScanOperator to LINE
    condition_1 = Condition(header_source_field, operator_empty, "")
    condition_2 = Condition(line_source_field, operator_not_empty, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "LINE")
    rule = Rule(
        "Rule2",
        "Description2",
        [condition_1, condition_2],
        ANY,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule])

    # Rule2: perform
    with fixture("logistic_invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # Rule2: test ScanOperator, should be modified because condition_2 applies
    scan_operator = field_registry.get("scan_operator").get(output_tree)
    assert scan_operator == "LINE"

    # Rule3: if header_order_number is not empty and line_order_number is empty, then set ScanOperator to HEAD
    condition_1 = Condition(header_source_field, operator_not_empty, "")
    condition_2 = Condition(line_source_field, operator_empty, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "HEAD")
    rule = Rule(
        "Rule3",
        "Description3",
        [condition_1, condition_2],
        ANY,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule])

    # Rule3: perform
    with fixture("logistic_invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # Rule3: test ScanOperator, should be modified because condition_1 applies
    scan_operator = field_registry.get("scan_operator").get(output_tree)
    assert scan_operator == "HEAD"

    # Rule4: if header_order_number and line_order_number are empty, then set ScanOperator to EMPTY
    condition_1 = Condition(header_source_field, operator_empty, "")
    condition_2 = Condition(line_source_field, operator_empty, "")
    action = action_registry.get("set_str")
    action_with_value = ActionWithValue(action, target_field, "EMPTY")
    rule = Rule(
        "Rule4",
        "Description4",
        [condition_1, condition_2],
        ANY,
        [action_with_value],
        [],
        None,
    )
    rules = Rules([rule])

    # Rule4: perform
    with fixture("logistic_invoice.xml") as f:
        input_tree = etree.parse(f)
    output_tree = rules.perform(input_tree)

    # Rule4: test ScanOperator, should not be modified because both conditions does not apply
    scan_operator = field_registry.get("scan_operator").get(output_tree)
    assert scan_operator == "ORIGINAL"
