# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal

from lxml import etree

from bre.actions import action_registry
from bre.core import ActionWithValue

from .fields import field_registry
from .utils import fixture

empty_xml = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Invoice><Header></Header></Invoice>
"""


def test_set_str():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("set_str")
    field = field_registry.get("company_code")
    action = ActionWithValue(set, field, "100")
    action.perform(tree)
    assert tree.xpath("/Invoice/Header/CompCodeFin")[0].text == "100"


def test_prefix_str():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    prefix = action_registry.get("prefix_str")
    field = field_registry.get("company_code")
    action = ActionWithValue(prefix, field, "prefix")
    action.perform(tree)
    assert field.get(tree) == "prefix998"


def test_postfix_str():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    postfix = action_registry.get("postfix_str")
    field = field_registry.get("company_code")
    action = ActionWithValue(postfix, field, "postfix")
    action.perform(tree)
    assert field.get(tree) == "998postfix"


def test_strip_str():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    strip = action_registry.get("strip_str")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(strip, field, None)
    action.perform(tree)
    assert tree.xpath("/Invoice/Header/InvoiceNumber")[0].text == "201200696"


def test_delete_str():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    delete = action_registry.get("delete_str")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)
    assert tree.xpath("/Invoice/Header/InvoiceNumber") == []


def test_delete_str_empty():
    tree = etree.fromstring(empty_xml)
    delete = action_registry.get("delete_str")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)
    assert tree.xpath("/Invoice/Header/InvoiceNumber") == []


def test_delete_str_tag():
    # ISP45-683: Delete of a tag failed at all
    # invoice.xml has `/Invoice/Header/AdditionalFields/Field@generic_1`
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)

    # test if we have a value upfront
    generic_1 = field_registry.get("generic_1").get(tree)
    assert generic_1 == "just a random text"

    # perform the action
    delete = action_registry.get("delete_str")
    field = field_registry.get("generic_1")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)

    # test that value has been deleted
    generic_1 = field_registry.get("generic_1").get(tree)
    assert generic_1 == ""

    # test that amount_1, date_1 and freightcosts (with the same XML-tag) are still available
    amount_1 = field_registry.get("amount_1").get(tree)
    date_1 = field_registry.get("date_1").get(tree)
    freightcosts = field_registry.get("freightcosts").get(tree)
    assert amount_1 == Decimal("40.21")
    assert date_1 == date(2016, 9, 8)
    assert freightcosts == Decimal("60.68")


def test_delete_str_missing_element_tree():
    # ISP45-683: Delete of a tag failed if the parent tag does not exist
    # empty_xml does not even have `/Invoice/Header/AdditionalFields`
    tree = etree.fromstring(empty_xml)

    # test if we have no value upfront
    generic_1 = field_registry.get("generic_1").get(tree)
    assert generic_1 == ""

    # perform the action
    delete = action_registry.get("delete_str")
    field = field_registry.get("generic_1")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)

    # test that value is still empty
    generic_1 = field_registry.get("generic_1").get(tree)
    assert generic_1 == ""


def test_delete_multiple_elements():
    # load XML
    with fixture("logistic_invoice.xml") as f:
        tree = etree.parse(f)

    # create action to delete ordernumbers from the header
    field = field_registry.get("order_number")
    delete = action_registry.get("delete_str")
    action = ActionWithValue(delete, field, None)

    # test XML before action
    order_numbers = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert len(order_numbers) == 2

    # perform the action
    action.perform(tree)

    # test XML after action
    order_numbers = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert len(order_numbers) == 0

    # load XML
    with fixture("logistic_invoice.xml") as f:
        tree = etree.parse(f)

    # create action to delete po_lookups from the header
    field = field_registry.get("po_lookup")
    delete = action_registry.get("delete_str")
    action = ActionWithValue(delete, field, None)

    # test XML before action
    po_lookups = tree.xpath("/Invoice/Header/POLookups/POLookup")
    assert len(po_lookups) == 2

    # perform the action
    action.perform(tree)

    # test XML after action
    po_lookups = tree.xpath("/Invoice/Header/POLookups/POLookup")
    assert len(po_lookups) == 0

    # load XML
    with fixture("logistic_invoice.xml") as f:
        tree = etree.parse(f)

    # create action to delete ordernumbers from the line(s)
    line_source_field = field_registry.get("line_ordernumber")
    delete = action_registry.get("delete_str")
    action = ActionWithValue(delete, line_source_field, None)

    # test XML before action
    lines = tree.xpath("Line")
    assert len(lines) == 2
    assert lines[0].xpath("LineNumber")[0].text == "10"
    assert lines[1].xpath("LineNumber")[0].text == "20"
    assert lines[0].xpath("OrderNumber")[0].text == "30095280/36.20.93"
    assert lines[1].xpath("OrderNumber")[0].text == "30099471/99.90.07"

    # perform the action
    action.perform(tree)

    # test XML after action
    lines = tree.xpath("Line")
    assert len(lines) == 2
    assert lines[0].xpath("LineNumber")[0].text == "10"
    assert lines[1].xpath("LineNumber")[0].text == "20"
    assert lines[0].xpath("OrderNumber") == []
    assert lines[1].xpath("OrderNumber") == []


def test_set_decimal():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("set_decimal")
    field = field_registry.get("credit_limit")
    action = ActionWithValue(set, field, Decimal("3.14"))
    action.perform(tree)
    assert field.get(tree) == Decimal("3.14")


def test_delete_decimal():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    delete = action_registry.get("delete_decimal")
    field = field_registry.get("credit_limit")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)
    assert field.get(tree) is None


def test_absolute_decimal():
    with fixture("nega.xml") as f:
        tree = etree.parse(f)
    absolute = action_registry.get("absolute_decimal")
    field = field_registry.get("credit_limit")
    action = ActionWithValue(absolute, field, None)
    action.perform(tree)
    assert field.get(tree) == Decimal("1.34")


def test_absolute_decimal2():
    with fixture("nega.xml") as f:
        tree = etree.parse(f)
    absolute = action_registry.get("absolute_decimal")
    field = field_registry.get("tax_amount")
    action = ActionWithValue(absolute, field, None)
    action.perform(tree)
    assert field.get(tree) == Decimal("21.12")


def test_negative_decimal():
    with fixture("nega.xml") as f:
        tree = etree.parse(f)
    negative = action_registry.get("negative_decimal")
    field = field_registry.get("credit_limit")
    action = ActionWithValue(negative, field, None)
    action.perform(tree)
    assert field.get(tree) == Decimal("1.34")


def test_negative_decimal2():
    with fixture("nega.xml") as f:
        tree = etree.parse(f)
    negative = action_registry.get("negative_decimal")
    field = field_registry.get("tax_amount")
    action = ActionWithValue(negative, field, None)
    action.perform(tree)
    assert field.get(tree) == Decimal("-21.12")


def test_set_date():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("set_date")
    field = field_registry.get("posting_date")
    action = ActionWithValue(set, field, date(2017, 2, 2))
    action.perform(tree)
    assert field.get(tree) == date(2017, 2, 2)


def test_delete_date():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    delete = action_registry.get("delete_date")
    field = field_registry.get("posting_date")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)
    assert field.get(tree) is None


def test_set_currency():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("set_str")
    field = field_registry.get("currency_code")
    action = ActionWithValue(set, field, "SGD")
    action.perform(tree)
    assert tree.xpath("/Invoice/Header/TotalAmount/@currency") == ["SGD"]


def test_set_currency_empty_xml():
    # set currency attribute, even when the TotalAmount field doesn't exist
    tree = etree.fromstring(empty_xml)
    set = action_registry.get("set_str")
    field = field_registry.get("currency_code")
    action = ActionWithValue(set, field, "GPB")
    action.perform(tree)
    assert tree.xpath("/Invoice/Header/TotalAmount/@currency") == ["GPB"]


def test_tax_percentage_action():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("set_str")
    field = field_registry.get("tax_percent")
    action = ActionWithValue(set, field, "21.000")
    action.perform(tree)
    assert tree.xpath("/Invoice/Header/Tax/TotalTax/@percentquantity")[0] == "21.000"


def test_shifted_vat_action():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("set_str")
    field = field_registry.get("tax_shifted")
    action = ActionWithValue(set, field, "true")
    action.perform(tree)
    assert tree.xpath("/Invoice/Header/Tax/TotalTax/@taxshifted")[0] == "true"


def test_additional_coding():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    field = field_registry.get("additional_coding")
    set = action_registry.get("set_str")
    action = ActionWithValue(set, field, "true")
    action.perform(tree)

    assert tree.xpath("/Invoice/Process/AdditionalCoding")[0].text == "true"

    with fixture("invoice2.xml") as f:
        tree = etree.parse(f)

    action.perform(tree)

    assert tree.xpath("/Invoice/Process/AdditionalCoding")[0].text == "true"

    tree = etree.fromstring(empty_xml)

    action.perform(tree)
    assert tree.xpath("/Invoice/Process/AdditionalCoding")[0].text == "true"


def test_target_group():
    # our action is to set TargetGroup to TG2
    field = field_registry.get("target_group")
    set = action_registry.get("set_str")
    action = ActionWithValue(set, field, "TG2")

    # get handle to invoice.xml where TargetGroup == TG1
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    assert tree.xpath("/Invoice/Process/TargetGroup")[0].text == "TG1"

    # perform action and test that TargetGroup has been set to TG2
    action.perform(tree)
    assert tree.xpath("/Invoice/Process/TargetGroup")[0].text == "TG2"

    # get handle to invoice.xml where TargetGroup is missing
    with fixture("invoice2.xml") as f:
        tree = etree.parse(f)
    assert len(tree.xpath("/Invoice/Process/TargetGroup")) == 0

    # perform action and test that TargetGroup has been set to TG2
    action.perform(tree)
    assert tree.xpath("/Invoice/Process/TargetGroup")[0].text == "TG2"

    # get handle to an empty XML where everything is missing
    tree = etree.fromstring(empty_xml)
    assert len(tree.xpath("/Invoice/Process/TargetGroup")) == 0

    # perform action and test that TargetGroup has been set to TG2
    action.perform(tree)
    assert tree.xpath("/Invoice/Process/TargetGroup")[0].text == "TG2"


def test_multi_value_order_number_strip():
    with fixture("multivalue_whitespace.xml") as f:
        tree = etree.parse(f)
    strip = action_registry.get("strip_str")
    field = field_registry.get("order_number")
    action = ActionWithValue(strip, field, None)
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert len(matches) == 2
    assert matches[0].text == "0011600006"
    assert matches[1].text == "0011600007"


def test_multi_value_order_number_prefix():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    prefix = action_registry.get("prefix_str")
    field = field_registry.get("order_number")
    action = ActionWithValue(prefix, field, "prefix")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert len(matches) == 2
    assert matches[0].text == "prefix0011600006"
    assert matches[1].text == "prefix0011600007"


def test_multi_value_order_number_postfix():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    postfix = action_registry.get("postfix_str")
    field = field_registry.get("order_number")
    action = ActionWithValue(postfix, field, "postfix")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert len(matches) == 2
    assert matches[0].text == "0011600006postfix"
    assert matches[1].text == "0011600007postfix"


def test_multi_value_order_number_set():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("set_str")
    field = field_registry.get("order_number")
    action = ActionWithValue(set, field, "new")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert len(matches) == 1
    assert matches[0].text == "new"


def test_multi_value_order_number_delete():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    delete = action_registry.get("delete_str")
    field = field_registry.get("order_number")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert len(matches) == 0


def test_multi_value_tax_amount_set():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("set_decimal")
    field = field_registry.get("tax_amount")
    action = ActionWithValue(set, field, Decimal("6.0"))
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Tax/TotalTax")
    assert len(matches) == 1
    assert matches[0].text == "6"


def test_multi_value_tax_amount_delete():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    delete = action_registry.get("delete_decimal")
    field = field_registry.get("tax_amount")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Tax/TotalTax")
    assert len(matches) == 0


def test_multi_value_tax_shifted_set():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("set_str")
    field = field_registry.get("tax_shifted")
    action = ActionWithValue(set, field, "true")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Tax/TotalTax")
    assert len(matches) == 2  # has two taxlines
    assert matches[0].get("taxshifted") == "true"
    # see release notes, initially set up to only set the first instance/occurance
    # TODO : do we want to change that?
    assert matches[1].get("taxshifted") is None


def test_multi_value_tax_shifted_delete():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    delete = action_registry.get("delete_str")
    field = field_registry.get("tax_shifted")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Tax/TotalTax")
    assert len(matches) == 2  # attribute got delete, but tag did not
    assert matches[0].text == "21.00"
    assert matches[0].get("percentquantity") == "21.00"
    assert matches[0].get("currency") == "EUR"
    assert matches[1].text == "0.00"
    assert matches[1].get("percentquantity") == "0.00"
    assert matches[1].get("currency") == "EUR"


def test_string_left_string():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_left_string")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(set, field, "-")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/InvoiceNumber")
    assert matches[0].text == "IO"


def test_string_left_integer():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_left_integer")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(set, field, 5)
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/InvoiceNumber")
    assert matches[0].text == "IO-1"


def test_string_right_string():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_right_string")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(set, field, "-")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/InvoiceNumber")
    assert matches[0].text == "123456-ABC"


def test_string_right_integer():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_right_integer")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(set, field, 5)
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/InvoiceNumber")
    assert matches[0].text == "3456-ABC"


def test_string_leftback_string():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_leftback_string")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(set, field, "-")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/InvoiceNumber")
    assert matches[0].text == "IO-123456"


def test_string_leftback_integer():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_leftback_integer")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(set, field, 5)
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/InvoiceNumber")
    assert matches[0].text == "IO-12345"


def test_string_rightback_string():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_rightback_string")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(set, field, "-")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/InvoiceNumber")
    assert matches[0].text == "ABC"


def test_string_rightback_integer():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_rightback_integer")
    field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(set, field, 5)
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/InvoiceNumber")
    assert matches[0].text == "-ABC"


def test_string_left_string_no_action():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_left_string")
    field = field_registry.get("order_number")
    action = ActionWithValue(set, field, "-")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert matches[0].text == "0011600006"


def test_string_right_string_no_action():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_right_string")
    field = field_registry.get("order_number")
    action = ActionWithValue(set, field, "-")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert matches[0].text == "0011600006"


def test_string_leftback_string_no_action():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_leftback_string")
    field = field_registry.get("order_number")
    action = ActionWithValue(set, field, "-")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert matches[0].text == "0011600006"


def test_string_rightback_string_no_action():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    set = action_registry.get("string_rightback_string")
    field = field_registry.get("order_number")
    action = ActionWithValue(set, field, "-")
    action.perform(tree)
    matches = tree.xpath("/Invoice/Header/Order/OrderNumber")
    assert matches[0].text == "0011600006"


def test_action_within_lines():
    with fixture("invoice_linecoding.xml") as f:
        tree = etree.parse(f)
    copy = action_registry.get("set_str")
    source_field = field_registry.get("line_UserArea01")
    target_field = field_registry.get("linecoding_description")

    action = ActionWithValue(copy, target_field, "", source_field)
    action.perform(tree, source_field.manipulators(tree, None)[0].get_element().getparent())
    assert target_field.get(tree) == source_field.get(tree)


def test_copy():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    copy = action_registry.get("set_str")
    source_field = field_registry.get("order_number")
    target_field = field_registry.get("vendor_invoice_number")

    action = ActionWithValue(copy, target_field, "", source_field)
    action.perform(tree)
    assert target_field.get(tree) == source_field.get(tree)


def test_copy_with_prefix():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    prefix = action_registry.get("prefix_str")
    source_field = field_registry.get("order_number")
    target_field = field_registry.get("vendor_invoice_number")
    prefix_value = "test"

    action = ActionWithValue(prefix, target_field, prefix_value, source_field)
    action.perform(tree)
    assert target_field.get(tree) == prefix_value + source_field.get(tree)


def test_copy_with_empty_source_field():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    copy = action_registry.get("set_str")
    source_field = field_registry.get("vendor_bank_account")
    target_field = field_registry.get("vendor_invoice_number")

    action = ActionWithValue(copy, target_field, "", source_field)
    action.perform(tree)
    assert target_field.get(tree) == ""
    assert target_field.get(tree) == source_field.get(tree)


def test_copy_source_field_does_not_exist():
    with fixture("multivalue.xml") as f:
        tree = etree.parse(f)
    copy = action_registry.get("set_str")
    source_field = field_registry.get("customerparty_telephone")
    target_field = field_registry.get("vendor_invoice_number")
    action = ActionWithValue(copy, target_field, "", source_field)
    action.perform(tree)
    assert target_field.get(tree) == ""
    assert target_field.get(tree) == source_field.get(tree)


def test_delete_attribute_value():
    # NEXT-4166: Deleting an attribute resulted in deleting the complete tag, which should not
    # invoice.xml does have `/Invoice/Header/Tax/TotalTax@percentquantity`
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)

    # test if we have values upfront
    tax_amount = field_registry.get("tax_amount").get(tree)
    tax_percent = field_registry.get("tax_percent").get(tree)
    tax_shifted = field_registry.get("tax_shifted").get(tree)
    assert tax_amount == Decimal("21.12")
    assert tax_percent == Decimal("21.00")
    assert tax_shifted == "true"

    # perform the action
    delete = action_registry.get("delete_decimal")
    field = field_registry.get("tax_percent")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)

    # test that value has been deleted
    assert field.get(tree) is None

    # test that tax_amount and tax_shifted are still available
    tax_amount = field_registry.get("tax_amount").get(tree)
    tax_shifted = field_registry.get("tax_shifted").get(tree)
    assert tax_amount == Decimal("21.12")
    assert tax_shifted == "true"


def test_delete_attribute_value_missing_tree():
    # NEXT-4166: Deleting an attribute resulted in deleting the complete tag, which should not
    # empty_xml does have `/Invoice/Header/Tax/TotalTax` at all, delete method should not fail
    tree = etree.fromstring(empty_xml)

    # test if we have no values upfront
    tax_amount = field_registry.get("tax_amount").get(tree)
    tax_percent = field_registry.get("tax_percent").get(tree)
    tax_shifted = field_registry.get("tax_shifted").get(tree)
    assert tax_amount is None
    assert tax_percent is None
    assert tax_shifted == ""

    # perform the action
    delete = action_registry.get("delete_decimal")
    field = field_registry.get("tax_percent")
    action = ActionWithValue(delete, field, None)
    action.perform(tree)

    # test that values are still empty
    tax_amount = field_registry.get("tax_amount").get(tree)
    tax_percent = field_registry.get("tax_percent").get(tree)
    tax_shifted = field_registry.get("tax_shifted").get(tree)
    assert tax_amount is None
    assert tax_percent is None
    assert tax_shifted == ""
