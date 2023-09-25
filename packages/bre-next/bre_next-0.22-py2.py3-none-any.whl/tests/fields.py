from bre import datatypes
from bre.core import FieldRegistry, FieldType
from bre.i18n import _

field_registry = FieldRegistry()

register = field_registry.register

BOOLEAN_CHOICES = [(_("true"), "true"), (_("false"), "false")]


def register_header():
    """
    <Invoice>
        <Header>
            <BaseCountry />
            <BookingDate />
            <BusinessArea />
            <CompCodeFin />
            <CreditLimit />
            <DocumentText />
            <HeaderText01 />
            <HeaderText02 />
            <HeaderText03 />
            <InvoiceClass />
            <InvoiceDate />
            <InvoiceNumber />
            <InvoiceType />
            <PaymentAgreementAmount />
            <PaymentReference />
            <PaymentID />
            <Reviewer />
            <RoutingCode />
            <TaxDate />
            <TotalAmount currency="" />
            <UserArea01 />
            <UserArea02 />
            <UserArea03 />
            <UserArea04 />
            <UserArea05 />
            <UserArea06 />
            <UserArea07 />
            <UserArea08 />
            <UserArea09 />
            <UserArea10 />
            <VendorAssignment />
        </Header>
    </Invoice>
    """
    register(
        "base_country",
        _("base_country"),
        datatypes.String,
        "/Invoice/Header/BaseCountry",
    )

    register("posting_date", _("posting_date"), datatypes.Date, "/Invoice/Header/BookingDate")

    register(
        "business_area",
        _("business_area"),
        datatypes.String,
        "/Invoice/Header/BusinessArea",
    )

    register(
        "company_code",
        _("company_code"),
        datatypes.String,
        "/Invoice/Header/CompCodeFin",
    )

    register(
        "credit_limit",
        _("credit_limit"),
        datatypes.Decimal,
        "/Invoice/Header/CreditLimit",
    )

    register(
        "document_text",
        _("document_text"),
        datatypes.String,
        "/Invoice/Header/DocumentText",
    )

    register(
        "header_text_01",
        _("header_text_01"),
        datatypes.String,
        "/Invoice/Header/HeaderText01",
    )

    register(
        "header_text_02",
        _("header_text_02"),
        datatypes.String,
        "/Invoice/Header/HeaderText02",
    )

    register(
        "header_text_03",
        _("header_text_03"),
        datatypes.String,
        "/Invoice/Header/HeaderText03",
    )

    register(
        "invoice_type",
        _("invoice_type"),
        datatypes.String,
        "/Invoice/Header/InvoiceClass",
    )

    register(
        "vendor_invoice_date",
        _("vendor_invoice_date"),
        datatypes.Date,
        "/Invoice/Header/InvoiceDate",
    )

    register(
        "vendor_invoice_number",
        _("vendor_invoice_number"),
        datatypes.String,
        "/Invoice/Header/InvoiceNumber",
    )

    register(
        "debit_credit",
        _("debit_credit"),
        datatypes.String,  # choice Debit and Credit
        "/Invoice/Header/InvoiceType",
        choices=[(_("Debit"), "Debit"), (_("Credit"), "Credit")],
    )

    register(
        "blocked_amount",
        _("blocked_amount"),
        datatypes.Decimal,
        "/Invoice/Header/PaymentAgreementAmount",
    )

    register(
        "structured_statement",
        _("structured_statement"),
        datatypes.String,
        "/Invoice/Header/PaymentReference",
    )

    register(
        "payment_id",
        _("payment_id"),
        datatypes.String,
        "/Invoice/Header/PaymentID",
    )

    register("reviewer", _("reviewer"), datatypes.String, "/Invoice/Header/Reviewer")

    register(
        "routing_code",
        _("routing_code"),
        datatypes.String,
        "/Invoice/Header/RoutingCode",
    )

    register(
        "tax_date",
        _("tax_date"),
        datatypes.Date,
        "/Invoice/Header/TaxDate",
    )

    register(
        "invoice_amount",
        _("invoice_amount"),
        datatypes.Decimal,
        "/Invoice/Header/TotalAmount",
    )

    register(
        "currency_code",
        _("currency_code"),
        datatypes.String,
        "/Invoice/Header/TotalAmount",
        "currency",
    )

    register(
        "header_userarea01",
        _("header_userarea01"),
        datatypes.String,
        "/Invoice/Header/UserArea01",
    )

    register(
        "header_userarea02",
        _("header_userarea02"),
        datatypes.String,
        "/Invoice/Header/UserArea02",
    )

    register(
        "header_userarea03",
        _("header_userarea03"),
        datatypes.String,
        "/Invoice/Header/UserArea03",
    )

    register(
        "header_userarea04",
        _("header_userarea04"),
        datatypes.String,
        "/Invoice/Header/UserArea04",
    )

    register(
        "header_userarea05",
        _("header_userarea05"),
        datatypes.String,
        "/Invoice/Header/UserArea05",
    )

    register(
        "header_userarea06",
        _("header_userarea06"),
        datatypes.String,
        "/Invoice/Header/UserArea06",
    )

    register(
        "header_userarea07",
        _("header_userarea07"),
        datatypes.String,
        "/Invoice/Header/UserArea07",
    )

    register(
        "header_userarea08",
        _("header_userarea08"),
        datatypes.String,
        "/Invoice/Header/UserArea08",
    )

    register(
        "header_userarea09",
        _("header_userarea09"),
        datatypes.String,
        "/Invoice/Header/UserArea09",
    )

    register(
        "header_userarea10",
        _("header_userarea10"),
        datatypes.String,
        "/Invoice/Header/UserArea10",
    )

    register(
        "assignment",
        _("assignment"),
        datatypes.String,
        "/Invoice/Header/VendorAssignment",
    )


def register_header_orders():
    """
    <Invoice>
        <Header>
            <Order>
                <OrderNumber />
            </Order>
        </Header>
    </Invoice>
    """
    register(
        "order_number",
        _("order_number"),
        datatypes.String,
        "/Invoice/Header/Order/OrderNumber",
    )

    register(
        "order_order_number",
        _("order_order_number"),
        datatypes.String,
        "",
        type=FieldType.ORDER,
    )


def register_header_po_lookups():
    """
    <Invoice>
        <Header>
            <POLookups>
                <POLookup />
            </Order>
        </Header>
    </Invoice>
    """
    register(
        "po_lookup",
        _("po_lookup"),
        datatypes.String,
        "/Invoice/Header/POLookups/POLookup",
    )

    register(
        "po_lookups_po_lookup",
        _("po_lookups_po_lookup"),
        datatypes.String,
        "",
        type=FieldType.PO_LOOKUP,
    )


def register_header_customer_party():
    """
    <Invoice>
        <Header>
            <Parties>
                <CustomerParty>
                    <Department />
                    <GLN />
                    <Name />
                    <PartyId />
                    <TaxId />
                    <Addresses>
                        <PrimaryAddress>
                            <AddressLine />
                            <BankAccount />
                            <ChamberofCommerce />
                            <City />
                            <Country />
                            <PostalCode />
                            <Telephone />
                        </PrimaryAddress>
                    </Addresses>
                    <Contact>
                        <Description />
                    </Contact>
                </CustomerParty>
            </Parties>
        </Header>
    </Invoice>
    """
    register(
        "customerparty_department",
        _("customerparty_department"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/Department",
    )

    register(
        "customerparty_gln",
        _("customerparty_gln"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/GLN",
    )

    register(
        "customerparty_name",
        _("customerparty_name"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/Name",
    )

    register(
        "customerparty_number",
        _("customerparty_number"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/PartyId",
    )

    register(
        "customerparty_taxid",
        _("customerparty_taxid"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/TaxId",
    )

    register(
        "customerparty_address",
        _("customerparty_address"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/Addresses/PrimaryAddress/AddressLine",
    )

    register(
        "customerparty_bankaccount",
        _("customerparty_bankaccount"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/Addresses/PrimaryAddress/BankAccount",
    )

    register(
        "customerparty_coc",
        _("customerparty_coc"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/Addresses/PrimaryAddress/ChamberofCommerce",
    )

    register(
        "customerparty_city",
        _("customerparty_city"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/Addresses/PrimaryAddress/City",
    )

    register(
        "customerparty_country",
        _("customerparty_country"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/Addresses/PrimaryAddress/Country",
    )

    register(
        "customerparty_postal",
        _("customerparty_postal"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/Addresses/PrimaryAddress/PostalCode",
    )

    register(
        "customerparty_telephone",
        _("customerparty_telephone"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/Addresses/PrimaryAddress/Telephone",
    )

    register(
        "customerparty_contactdesc",
        _("customerparty_contactdesc"),
        datatypes.String,
        "/Invoice/Header/Parties/CustomerParty/Contact/Description",
    )


def register_header_initiating_party():
    """
    <Invoice>
        <Header>
            <Parties>
                <InitiatingParty>
                    <GLN />
                    <Name />
                </InitiatingParty>
            </Parties>
        </Header>
    </Invoice>
    """
    register(
        "initiating_party_gln",
        _("initiating_party_gln"),
        datatypes.String,
        "/Invoice/Header/Parties/InitiatingParty/GLN",
    )

    register(
        "initiating_party_name",
        _("initiating_party_name"),
        datatypes.String,
        "/Invoice/Header/Parties/InitiatingParty/Name",
    )


def register_header_shipto_party():
    """
    <Invoice>
        <Header>
            <Parties>
                <ShipToParty>
                    <GLN />
                </ShipToParty>
            </Parties>
        </Header>
    </Invoice>
    """
    register(
        "shiptoparty_gln",
        _("shiptoparty_gln"),
        datatypes.String,
        "/Invoice/Header/Parties/ShipToParty/GLN",
    )


def register_header_vendor_party():
    """
    <Invoice>
        <Header>
            <Parties>
                <VendorParty>
                    <Department />
                    <GLN />
                    <Name />
                    <PartyId />
                    <TaxId />
                    <Addresses>
                        <PrimaryAddress>
                            <AddressLine />
                            <BankAccount />
                            <ChamberofCommerce />
                            <City />
                            <Country />
                            <PostalCode />
                            <Telephone />
                        </PrimaryAddress>
                    </Addresses>
                    <Contact>
                        <Description />
                    </Contact>
                </VendorParty>
            </Parties>
        </Header>
    </Invoice>
    """
    register(
        "vendor_department",
        _("vendor_department"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/Department",
    )

    register(
        "vendor_gln",
        _("vendor_gln"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/GLN",
    )

    register(
        "vendor_name",
        _("vendor_name"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/Name",
    )

    register(
        "vendor_number",
        _("vendor_number"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/PartyId",
    )

    register(
        "vendor_vat_id",
        _("vendor_vat_id"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/TaxId",
    )

    register(
        "vendor_address",
        _("vendor_address"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/Addresses/PrimaryAddress/AddressLine",
    )

    register(
        "vendor_bank_account",
        _("vendor_bank_account"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/Addresses/PrimaryAddress/BankAccount",
    )

    register(
        "vendor_coc",
        _("vendor_coc"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/Addresses/PrimaryAddress/ChamberofCommerce",
    )

    register(
        "vendor_city",
        _("vendor_city"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/Addresses/PrimaryAddress/City",
    )

    register(
        "vendor_country",
        _("vendor_country"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/Addresses/PrimaryAddress/Country",
    )

    register(
        "vendor_postal",
        _("vendor_postal"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/Addresses/PrimaryAddress/PostalCode",
    )

    register(
        "vendor_telephone",
        _("vendor_telephone"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/Addresses/PrimaryAddress/Telephone",
    )

    register(
        "vendor_contactdesc",
        _("vendor_contactdesc"),
        datatypes.String,
        "/Invoice/Header/Parties/VendorParty/Contact/Description",
    )


def register_header_tax():
    """
    <Invoice>
        <Header>
            <Tax>
                <TotalTax percentquantity="" taxshifted="">
            </Tax>
        </Header>
    </Invoice>
    """
    register("tax_amount", _("tax_amount"), datatypes.Decimal, "/Invoice/Header/Tax/TotalTax")

    register(
        "tax_percent",
        _("tax_percent"),
        datatypes.Decimal,
        "/Invoice/Header/Tax/TotalTax",
        "percentquantity",
    )

    register(
        "tax_shifted",
        _("tax_shifted"),
        datatypes.String,
        "/Invoice/Header/Tax/TotalTax",
        "taxshifted",
        choices=BOOLEAN_CHOICES,
    )


def register_header_additional():
    """
    <Invoice>
        <Header>
            <AdditionalFields>
                <Field key="amount_1" />
                <Field key="amount_2" />
                <Field key="amount_3" />
                <Field key="date_1" />
                <Field key="date_2" />
                <Field key="date_3" />
                <Field key="generic_1" />
                <Field key="generic_2" />
                <Field key="generic_3" />
                <Field key="freightcosts" />
                <Field key="ordercosts" />
                <Field key="packagingcosts" />
            </AdditionalFields>
        </Header>
    </Invoice>
    """
    register(
        "amount_1",
        _("amount_1"),
        datatypes.Decimal,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="amount_1",
    )

    register(
        "amount_2",
        _("amount_2"),
        datatypes.Decimal,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="amount_2",
    )

    register(
        "amount_3",
        _("amount_3"),
        datatypes.Decimal,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="amount_3",
    )

    register(
        "date_1",
        _("date_1"),
        datatypes.Date,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="date_1",
    )

    register(
        "date_2",
        _("date_2"),
        datatypes.Date,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="date_2",
    )

    register(
        "date_3",
        _("date_3"),
        datatypes.Date,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="date_3",
    )

    register(
        "generic_1",
        _("generic_1"),
        datatypes.String,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="generic_1",
    )

    register(
        "generic_2",
        _("generic_2"),
        datatypes.String,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="generic_2",
    )

    register(
        "generic_3",
        _("generic_3"),
        datatypes.String,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="generic_3",
    )

    register(
        "freightcosts",
        _("freightcosts"),
        datatypes.Decimal,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="freightcosts",
    )

    register(
        "ordercosts",
        _("ordercosts"),
        datatypes.Decimal,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="ordercosts",
    )

    register(
        "packagingcosts",
        _("packagingcosts"),
        datatypes.Decimal,
        "/Invoice/Header/AdditionalFields/Field",
        attribute_name="key",
        attribute_value="packagingcosts",
    )


def register_process():
    """
    <Invoice>
        <Process>
            <AdditionalCoding />
            <TargetGroup />
        </Process>
    </Invoice>
    """
    register(
        "additional_coding",
        _("additional_coding"),
        datatypes.String,
        "/Invoice/Process/AdditionalCoding",
        choices=BOOLEAN_CHOICES,
    )

    register(
        "target_group",
        _("target_group"),
        datatypes.String,
        "/Invoice/Process/TargetGroup",
    )


def register_scan():
    """
    <Invoice>
        <Scan>
            <ScanOperator />
            <Source />
            <MailOrigin>
                <CompCodeFin />
                <FromAddress />
                <MailDate />
                <MailSubject />
                <ToAddress />
            </MailOrigin>
        </Scan>
    </Invoice>
    """
    register(
        "scan_operator",
        _("scan_operator"),
        datatypes.String,
        "/Invoice/Scan/ScanOperator",
    )

    register("scan_source", _("scan_source"), datatypes.String, "/Invoice/Scan/Source")

    register(
        "mail_company_code",
        _("mail_company_code"),
        datatypes.String,
        "/Invoice/Scan/MailOrigin/CompCodeFin",
    )

    register(
        "from_address",
        _("from_address"),
        datatypes.String,
        "/Invoice/Scan/MailOrigin/FromAddress",
    )

    register("mail_date", _("mail_date"), datatypes.Date, "/Invoice/Scan/MailOrigin/MailDate")

    register(
        "mail_subject",
        _("mail_subject"),
        datatypes.String,
        "/Invoice/Scan/MailOrigin/MailSubject",
    )

    register(
        "to_address",
        _("to_address"),
        datatypes.String,
        "/Invoice/Scan/MailOrigin/ToAddress",
    )


def register_line():
    """
    <Invoice>
        <Line>
            <ArticleNumber />
            <Description />
            <InternalArticleNumber />
            <ItemAmount />
            <ItemQuantity />
            <ItemUnit />
            <LineNumber />
            <Note />
            <OrderLineNumber />
            <OrderNumber />
            <TotalAmount />
            <UserArea01 />
            <UserArea02 />
            <UserArea03 />
            <UserArea04 />
            <UserArea05 />
            <UserArea06 />
            <UserArea07 />
            <UserArea08 />
            <UserArea09 />
            <UserArea10 />
        </Line>
    </Invoice>
    """

    register(
        "line_articlenumber",
        _("Line ArticleNumber"),
        datatypes.String,
        "/ArticleNumber",
        type=FieldType.LINE,
    )

    register(
        "line_description",
        _("Line description"),
        datatypes.String,
        "/Description",
        type=FieldType.LINE,
    )

    register(
        "line_internalarticlenumber",
        _("Line InternalArticleNumber"),
        datatypes.String,
        "/InternalArticleNumber",
        type=FieldType.LINE,
    )

    register(
        "line_itemamount",
        _("Line ItemAmount"),
        datatypes.Decimal,
        "/ItemAmount",
        type=FieldType.LINE,
    )

    register(
        "line_quantity",
        _("Line Quantity"),
        datatypes.Decimal,
        "/ItemQuantity",
        type=FieldType.LINE,
    )

    register(
        "line_itemunit",
        _("Line ItemUnit"),
        datatypes.String,
        "/ItemUnit",
        type=FieldType.LINE,
    )

    register(
        "line_linenumber",
        _("Line Number"),
        datatypes.String,
        "/LineNumber",
        type=FieldType.LINE,
    )

    register("line_note", _("Line Note"), datatypes.String, "/Note", type=FieldType.LINE)

    register(
        "line_orderlinenumber",
        _("Line OrderLineNumber"),
        datatypes.String,
        "/OrderLineNumber",
        type=FieldType.LINE,
    )

    register(
        "line_ordernumber",
        _("Line OrderNumber"),
        datatypes.String,
        "/OrderNumber",
        type=FieldType.LINE,
    )

    register(
        "line_total_amount",
        _("Line TotalAmount"),
        datatypes.Decimal,
        "/TotalAmount",
        type=FieldType.LINE,
    )

    register(
        "line_UserArea01",
        _("line_userarea01"),
        datatypes.String,
        "/UserArea01",
        type=FieldType.LINE,
    )

    register(
        "line_UserArea02",
        _("line_userarea02"),
        datatypes.String,
        "/UserArea02",
        type=FieldType.LINE,
    )

    register(
        "line_UserArea03",
        _("line_userarea03"),
        datatypes.String,
        "/UserArea03",
        type=FieldType.LINE,
    )

    register(
        "line_UserArea04",
        _("line_userarea04"),
        datatypes.String,
        "/UserArea04",
        type=FieldType.LINE,
    )

    register(
        "line_UserArea05",
        _("line_userarea05"),
        datatypes.String,
        "/UserArea05",
        type=FieldType.LINE,
    )

    register(
        "line_UserArea06",
        _("line_userarea06"),
        datatypes.String,
        "/UserArea06",
        type=FieldType.LINE,
    )

    register(
        "line_UserArea07",
        _("line_userarea07"),
        datatypes.String,
        "/UserArea07",
        type=FieldType.LINE,
    )

    register(
        "line_UserArea08",
        _("line_userarea08"),
        datatypes.String,
        "/UserArea08",
        type=FieldType.LINE,
    )

    register(
        "line_UserArea09",
        _("line_userarea09"),
        datatypes.String,
        "/UserArea09",
        type=FieldType.LINE,
    )

    register(
        "line_UserArea10",
        _("line_userarea10"),
        datatypes.String,
        "/UserArea10",
        type=FieldType.LINE,
    )


def register_line_coding():
    """
    <Invoice>
        <LineCoding>
            <Amount />
            <Asset />
            <CostCenter />
            <Description />
            <GeneralLedger />
            <Project />
            <TaxCode />
        </LineCoding>
    </Invoice>
    """
    register(
        "linecoding_amount",
        _("Linecoding Amount"),
        datatypes.String,
        "/Amount",
        type=FieldType.LINECODING,
    )

    register(
        "linecoding_asset",
        _("Linecoding Asset"),
        datatypes.String,
        "/Asset",
        type=FieldType.LINECODING,
    )

    register(
        "linecoding_cost_center",
        _("Linecoding Costcenter"),
        datatypes.String,
        "/CostCenter",
        type=FieldType.LINECODING,
    )

    register(
        "linecoding_description",
        _("Linecoding Description"),
        datatypes.String,
        "/Description",
        type=FieldType.LINECODING,
    )

    register(
        "linecoding_general_ledger",
        _("Linecoding Generalledger"),
        datatypes.String,
        "/GeneralLedger",
        type=FieldType.LINECODING,
    )

    register(
        "linecoding_project",
        _("Linecoding Project"),
        datatypes.String,
        "/Project",
        type=FieldType.LINECODING,
    )

    register(
        "linecoding_taxcode",
        _("Linecoding Taxcode"),
        datatypes.String,
        "/TaxCode",
        type=FieldType.LINECODING,
    )


def register_extension():
    field_registry.register(
        "extension_000000_amount",
        _("extension_000000_amount"),
        datatypes.Decimal,
        "/Invoice/Header/ExtensionFields/Amount",
        type=FieldType.EXTENSION,
    )
    field_registry.register(
        "extension_000000_description",
        _("extension_000000_description"),
        datatypes.String,
        "/Invoice/Header/ExtensionFields/Description",
        type=FieldType.EXTENSION,
    )


def register_custom_fields():
    field_registry.register(
        "custom_str0",
        _("custom_str0"),
        datatypes.String,
        "/Invoice/Header/CustomFields/custom_str0",
        type=FieldType.CUSTOM,
    )
    field_registry.register(
        "custom_bool0",
        _("custom_bool0"),
        datatypes.String,
        "/Invoice/Header/CustomFields/custom_bool0",
        type=FieldType.CUSTOM,
    )


# Basic Invoice Header fields
register_header()

# Ordernumber(s)
register_header_orders()

# PO lookup(s)
register_header_po_lookups()

# Parties (Customer, Initiating, ShipTo, Vendor)
register_header_customer_party()
register_header_initiating_party()
register_header_shipto_party()
register_header_vendor_party()

# Tax information
register_header_tax()

# Additional Header fields
register_header_additional()

# Process information
register_process()

# Scan (and email) information
register_scan()

# Line and LineCoding
register_line()
register_line_coding()

# Extensions
register_extension()

# Custom fields
register_custom_fields()


# TODO; ISP-SmartScan; /Invoice/Header/CurrencyCode
# TODO; IDT/Iris/EDI;  /Invoice/Header/TotalAmount/@currency

# TODO; ISP-SmartScan; taxamount	/Invoice/Header/Tax/TaxLine/TaxAmount
# TODO; IDT/Iris/EDI;  taxamount	/Invoice/Header/Tax/TotalTax
