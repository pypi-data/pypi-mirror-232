# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal

from lxml import etree

from .fields import field_registry
from .utils import fixture


def test_string_extractors():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    _vendor_number = field_registry.get("vendor_number").get(tree)
    _invoice_number = field_registry.get("vendor_invoice_number").get(tree)
    _company_code = field_registry.get("company_code").get(tree)
    _vendor_bank_account = field_registry.get("vendor_bank_account").get(tree)
    _order_number = field_registry.get("order_number").get(tree)
    _debit_credit = field_registry.get("debit_credit").get(tree)
    _base_country = field_registry.get("base_country").get(tree)
    _invoice_type = field_registry.get("invoice_type").get(tree)
    _business_area = field_registry.get("business_area").get(tree)
    _document_text = field_registry.get("document_text").get(tree)
    _header_text_01 = field_registry.get("header_text_01").get(tree)
    _header_text_02 = field_registry.get("header_text_02").get(tree)
    _header_text_03 = field_registry.get("header_text_03").get(tree)
    _assignment = field_registry.get("assignment").get(tree)
    _scan_operator = field_registry.get("scan_operator").get(tree)
    _scan_source = field_registry.get("scan_source").get(tree)
    _reviewer = field_registry.get("reviewer").get(tree)
    _routing_code = field_registry.get("routing_code").get(tree)
    _vendor_vat_id = field_registry.get("vendor_vat_id").get(tree)
    _vendor_gln = field_registry.get("vendor_gln").get(tree)
    _customerparty_gln = field_registry.get("customerparty_gln").get(tree)
    _currency_code = field_registry.get("currency_code").get(tree)
    _initiating_party_name = field_registry.get("initiating_party_name").get(tree)
    _mail_company_code = field_registry.get("mail_company_code").get(tree)
    _from_address = field_registry.get("from_address").get(tree)
    _to_address = field_registry.get("to_address").get(tree)
    _mail_subject = field_registry.get("mail_subject").get(tree)
    _structured_statement = field_registry.get("structured_statement").get(tree)
    _payment_id = field_registry.get("payment_id").get(tree)
    _additional_coding = field_registry.get("additional_coding").get(tree)
    _target_group = field_registry.get("target_group").get(tree)
    assert _vendor_number == "100004"
    assert _invoice_number == "2012 00696"
    assert _company_code == "998"
    assert _vendor_bank_account == "NL27RABO0172000939"
    assert _order_number == "123 456"
    assert _debit_credit == "Debit"
    assert _base_country == "NL"
    assert _invoice_type == "InvoiceType"
    assert _business_area == "100"
    assert _document_text == "TEST"
    assert _header_text_01 == "H_T_1"
    assert _header_text_02 == "H_T_2"
    assert _header_text_03 == "H_T_3"
    assert _assignment == "Assignment"
    assert _scan_operator == "Koen"
    assert _scan_source == "EDI"
    assert _reviewer == "Marcel"
    assert _routing_code == "ROUT001"
    assert _vendor_vat_id == "NL820646374B01"
    assert _vendor_gln == "VendorGLN"
    assert _customerparty_gln == "CustomerPartyGLN"
    assert _currency_code == "EUR"
    assert _initiating_party_name == "Brabanthallen"
    assert _mail_company_code == "100"
    assert _from_address == "sender@example.com"
    assert _to_address == "receiver@example.com"
    assert _mail_subject == "A mail!"
    assert _structured_statement == "+++119/0044/05742+++"
    assert _payment_id == "16 18032 09050 00000 02303 27226"
    assert _additional_coding == "false"
    assert _target_group == "TG1"


def test_decimal_extractors():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    _invoice_amount = field_registry.get("invoice_amount").get(tree)
    _tax_amount = field_registry.get("tax_amount").get(tree)
    _tax_percent = field_registry.get("tax_percent").get(tree)
    _credit_limit = field_registry.get("credit_limit").get(tree)
    _blocked_amount = field_registry.get("blocked_amount").get(tree)
    assert _invoice_amount == Decimal("100.00")
    assert _tax_amount == Decimal("21.12")
    assert _tax_percent == Decimal("21.00")
    assert _credit_limit == Decimal("1.34")
    assert _blocked_amount == Decimal("0.00")


def test_date_extractors():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    _vendor_invoice_date = field_registry.get("vendor_invoice_date").get(tree)
    _posting_date = field_registry.get("posting_date").get(tree)
    _mail_date = field_registry.get("mail_date").get(tree)
    _tax_date = field_registry.get("tax_date").get(tree)
    assert _vendor_invoice_date == date(2012, 6, 1)
    assert _posting_date == date(2017, 1, 23)
    assert _mail_date == date(2017, 1, 1)
    assert _tax_date == date(2016, 8, 5)


def test_date_empty():
    with fixture("invoice_empty_tags.xml") as f:
        tree = etree.parse(f)
    _vendor_invoice_date = field_registry.get("vendor_invoice_date").get(tree)
    _posting_date = field_registry.get("posting_date").get(tree)
    _tax_date = field_registry.get("tax_date").get(tree)
    assert _vendor_invoice_date is None
    assert _posting_date is None
    assert _tax_date is None


def test_amount_empty():
    with fixture("invoice_empty_tags.xml") as f:
        tree = etree.parse(f)
    _invoice_amount = field_registry.get("invoice_amount").get(tree)
    _tax_amount = field_registry.get("tax_amount").get(tree)
    _credit_limit = field_registry.get("credit_limit").get(tree)
    _blocked_amount = field_registry.get("blocked_amount").get(tree)
    assert _invoice_amount is None
    assert _tax_amount is None
    assert _credit_limit is None
    assert _blocked_amount is None


def test_string_empty():
    with fixture("invoice_empty_tags.xml") as f:
        tree = etree.parse(f)
    _vendor_number = field_registry.get("vendor_number").get(tree)
    _invoice_number = field_registry.get("vendor_invoice_number").get(tree)
    _company_code = field_registry.get("company_code").get(tree)
    _vendor_bank_account = field_registry.get("vendor_bank_account").get(tree)
    _order_number = field_registry.get("order_number").get(tree)
    _debit_credit = field_registry.get("debit_credit").get(tree)
    _base_country = field_registry.get("base_country").get(tree)
    _invoice_type = field_registry.get("invoice_type").get(tree)
    _business_area = field_registry.get("business_area").get(tree)
    _document_text = field_registry.get("document_text").get(tree)
    _header_text_01 = field_registry.get("header_text_01").get(tree)
    _header_text_02 = field_registry.get("header_text_02").get(tree)
    _header_text_03 = field_registry.get("header_text_03").get(tree)
    _assignment = field_registry.get("assignment").get(tree)
    _scan_operator = field_registry.get("scan_operator").get(tree)
    _scan_source = field_registry.get("scan_source").get(tree)
    _reviewer = field_registry.get("reviewer").get(tree)
    _routing_code = field_registry.get("routing_code").get(tree)
    _vendor_vat_id = field_registry.get("vendor_vat_id").get(tree)
    _currency_code = field_registry.get("currency_code").get(tree)
    _structured_statement = field_registry.get("structured_statement").get(tree)
    _payment_id = field_registry.get("payment_id").get(tree)
    _additional_coding = field_registry.get("additional_coding").get(tree)
    _target_group = field_registry.get("target_group").get(tree)
    assert _vendor_number == ""
    assert _invoice_number == ""
    assert _company_code == ""
    assert _vendor_bank_account == ""
    assert _order_number == ""
    assert _debit_credit == ""
    assert _base_country == ""
    assert _invoice_type == ""
    assert _business_area == ""
    assert _document_text == ""
    assert _header_text_01 == ""
    assert _header_text_02 == ""
    assert _header_text_03 == ""
    assert _assignment == ""
    assert _scan_operator == ""
    assert _scan_source == ""
    assert _reviewer == ""
    assert _routing_code == ""
    assert _vendor_vat_id == ""
    assert _currency_code == ""
    assert _structured_statement == ""
    assert _payment_id == ""
    assert _additional_coding == ""
    assert _target_group == ""


def test_empty_xml():
    empty_xml = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Invoice><Header></Header></Invoice>
"""
    tree = etree.fromstring(empty_xml)
    _vendor_number = field_registry.get("vendor_number").get(tree)
    _currency_code = field_registry.get("currency_code").get(tree)
    assert _vendor_number == ""
    assert _currency_code == ""


def test_empty_vendor_number():
    no_vendor_xml = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Invoice>
    <Header>
        <Parties>
            <VendorParty>
                <PartyId></PartyId>
            </VendorParty>
        </Parties>
    </Header>
</Invoice>
"""
    tree = etree.fromstring(no_vendor_xml)
    _vendor_number = field_registry.get("vendor_number").get(tree)
    assert _vendor_number == ""


def test_customer_party():
    with fixture("customerparty.xml") as f:
        tree = etree.parse(f)
    _department = field_registry.get("customerparty_department").get(tree)
    _gln = field_registry.get("customerparty_gln").get(tree)
    _name = field_registry.get("customerparty_name").get(tree)
    _number = field_registry.get("customerparty_number").get(tree)
    _taxid = field_registry.get("customerparty_taxid").get(tree)
    _address = field_registry.get("customerparty_address").get(tree)
    _bankaccount = field_registry.get("customerparty_bankaccount").get(tree)
    _coc = field_registry.get("customerparty_coc").get(tree)
    _city = field_registry.get("customerparty_city").get(tree)
    _country = field_registry.get("customerparty_country").get(tree)
    _postal = field_registry.get("customerparty_postal").get(tree)
    _telephone = field_registry.get("customerparty_telephone").get(tree)
    _contact = field_registry.get("customerparty_contactdesc").get(tree)
    assert _department == "Development"
    assert _gln == "4000001000005"
    assert _name == "ISProjects Onroerend goed"
    assert _number == "13901555"
    assert _taxid == "NL000099998B57"
    assert _address == "Rompertdreef 9"
    assert _bankaccount == "NL00RABO0172000000"
    assert _coc == "40413215"
    assert _city == "'s-Hertogenbosch"
    assert _country == "NL"
    assert _postal == "5233ED"
    assert _telephone == "073-6233808"
    assert _contact == "e.vanderwerff@isprojects.nl"


def test_vendor_party():
    with fixture("vendorparty.xml") as f:
        tree = etree.parse(f)
    _department = field_registry.get("vendor_department").get(tree)
    _gln = field_registry.get("vendor_gln").get(tree)
    _name = field_registry.get("vendor_name").get(tree)
    _number = field_registry.get("vendor_number").get(tree)
    _taxid = field_registry.get("vendor_vat_id").get(tree)
    _address = field_registry.get("vendor_address").get(tree)
    _bank_account = field_registry.get("vendor_bank_account").get(tree)
    _coc = field_registry.get("vendor_coc").get(tree)
    _city = field_registry.get("vendor_city").get(tree)
    _country = field_registry.get("vendor_country").get(tree)
    _postal = field_registry.get("vendor_postal").get(tree)
    _telephone = field_registry.get("vendor_telephone").get(tree)
    _contact = field_registry.get("vendor_contactdesc").get(tree)
    assert _department == "ICT"
    assert _gln == "9501101020016"
    assert _name == "NOAB"
    assert _number == "13901556"
    assert _taxid == "NL802706228B01"
    assert _address == "Postbus 2478"
    assert _bank_account == "NL00ABNA0172000000"
    assert _coc == "40413216"
    assert _city == "Cromvoirt"
    assert _country == "NLD"
    assert _postal == "5202CL"
    assert _telephone == "073-6141419"
    assert _contact == "j.vangils@isprojects.nl"


def test_freefields():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    _freightcosts = field_registry.get("freightcosts").get(tree)
    _date_1 = field_registry.get("date_1").get(tree)
    _generic_1 = field_registry.get("generic_1").get(tree)
    _amount_1 = field_registry.get("amount_1").get(tree)
    assert _freightcosts == Decimal("60.68")
    assert _date_1 == date(2016, 9, 8)
    assert _generic_1 == "just a random text"
    assert _amount_1 == Decimal("40.21")


def test_customfields():
    with fixture("invoice3.xml") as f:
        tree = etree.parse(f)
    _custom_bool0 = field_registry.get("custom_bool0").get(tree)
    _custom_str0 = field_registry.get("custom_str0").get(tree)
    assert _custom_bool0 == "true"
    assert _custom_str0 == "hello world"


def test_header_userarea():
    with fixture("invoice.xml") as f:
        tree = etree.parse(f)
    _header_userarea_01 = field_registry.get("header_userarea01").get(tree)
    _header_userarea_02 = field_registry.get("header_userarea02").get(tree)
    _header_userarea_03 = field_registry.get("header_userarea03").get(tree)
    _header_userarea_04 = field_registry.get("header_userarea04").get(tree)
    _header_userarea_05 = field_registry.get("header_userarea05").get(tree)
    _header_userarea_06 = field_registry.get("header_userarea06").get(tree)
    _header_userarea_07 = field_registry.get("header_userarea07").get(tree)
    _header_userarea_08 = field_registry.get("header_userarea08").get(tree)
    _header_userarea_09 = field_registry.get("header_userarea09").get(tree)
    _header_userarea_10 = field_registry.get("header_userarea10").get(tree)
    assert _header_userarea_01 == "ISP45-184-01"
    assert _header_userarea_02 == "ISP45-184-02"
    assert _header_userarea_03 == "ISP45-184-03"
    assert _header_userarea_04 == "ISP45-184-04"
    assert _header_userarea_05 == "ISP45-184-05"
    assert _header_userarea_06 == "ISP45-184-06"
    assert _header_userarea_07 == "ISP45-184-07"
    assert _header_userarea_08 == "ISP45-184-08"
    assert _header_userarea_09 == "ISP45-184-09"
    assert _header_userarea_10 == "ISP45-184-10"


def test_line_fields():
    with fixture("logistic_invoice.xml") as f:
        tree = etree.parse(f)

    # extractor only gets the first occurance
    line_articlenumber = field_registry.get("line_articlenumber").get(tree)
    line_description = field_registry.get("line_description").get(tree)
    line_internalarticlenumber = field_registry.get("line_internalarticlenumber").get(tree)
    line_itemamount = field_registry.get("line_itemamount").get(tree)
    line_quantity = field_registry.get("line_quantity").get(tree)
    line_itemunit = field_registry.get("line_itemunit").get(tree)
    line_linenumber = field_registry.get("line_linenumber").get(tree)
    line_orderlinenumber = field_registry.get("line_orderlinenumber").get(tree)
    line_ordernumber = field_registry.get("line_ordernumber").get(tree)
    line_total_amount = field_registry.get("line_total_amount").get(tree)
    line_UserArea01 = field_registry.get("line_UserArea01").get(tree)
    line_UserArea02 = field_registry.get("line_UserArea02").get(tree)
    line_UserArea04 = field_registry.get("line_UserArea04").get(tree)
    assert line_articlenumber == "6012280"
    assert line_description == "RADS COMP 11 750X 900    1068W"
    assert line_internalarticlenumber == "05413571019558"
    assert line_itemamount == Decimal("183.57")
    assert line_quantity == Decimal("1")
    assert line_itemunit == "PCE"
    assert line_linenumber == "10"
    assert line_orderlinenumber == "10"
    assert line_ordernumber == "30095280/36.20.93"
    assert line_total_amount == Decimal("46.81")
    assert line_UserArea01 == "GTIN: 05413571019558"
    assert line_UserArea02 == "Taxcategory: Taxcategory: "
    assert line_UserArea04 == "Total discount: 136.76"
