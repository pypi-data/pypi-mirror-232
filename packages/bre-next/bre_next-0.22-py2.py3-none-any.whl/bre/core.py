# -*- coding: utf-8 -*-
import logging
from copy import deepcopy
from enum import IntEnum

from lxml import etree

logger = logging.getLogger(__name__)

ANY = "any"
ALL = "all"

LINECODING_BASE_PATH = "/Invoice/LineCoding"
LINE_BASE_PATH = "/Invoice/Line"
ORDER_BASE_PATH = "/Invoice/Header/Order/OrderNumber"


class FieldType(IntEnum):
    HEADER = 1
    LINE = 2
    LINECODING = 3
    ORDER = 4
    EXTENSION = 5
    CUSTOM = 6
    PO_LOOKUP = 7


# date     YYYY-MM-DD
# decimal  100.00####
# string   TEST
# boolean  false


class Rule:
    """Rule that has conditions to perform actions on an ISP-InvoiceXML-tree

    :param title: (short) title of a Rule
    :param description: function description of a Rule
    :param conditions: list of one or more :class:`Condition` instance(s)
    :param type_: Rule active for :data:`ANY` or ALL condition(s)
    :param actions: list of one or more :class:`ActionWithValue` instance(s)
    """

    # tabel met RULES (worden beheerd door ScanConsultant)
    # een RULE heeft een korte en lange omschrijving
    # een RULE heeft nul of meerdere CONDITIES  (nul = altijd geldig)
    # een RULE heeft één TYPE (type=ANY of type=ALL
    # wat wil zeggen dat bij gebruik van meerdere CONDITIES,
    # ze of allemaal moeten gelden of minimaal één)
    # een RULE heeft één of meerdere ACTIES

    def __init__(self, title, description, conditions, type_, actions, subrules, parent_rule):
        logger.debug("Init rule `%s`, `%s`", title, description)
        self.title = title
        self.description = description
        self._conditions = conditions
        self._type = type_
        self._actions = actions
        self._subrules = subrules
        self._parent_rule = parent_rule

    def perform(self, input_tree, output_tree):
        """Perform the action(s) if the condition(s) match

        :param input_tree: lxml-tree of ISP-InvoiceXML
        :param output_tree: lxml-tree of ISP-InvoiceXML
        """
        logger.debug("Test if rule applies `%s`, `%s`", self.title, self.description)
        # we also check on order_fields, as we do not want rules with only order fields to always match.
        if self._match_header(input_tree) and self._match_order(input_tree) and self._match_line(input_tree):
            logger.debug(
                "Perform rule title=`%s`, desc=`%s`, type=`%s`",
                self.title,
                self.description,
                self._type,
            )
            self._execute(output_tree)
            self._execute_subrules(input_tree, output_tree)
            self._add_rule_in_xml(output_tree)

    def dump(self):
        return {
            "title": self.title,
            "description": self.description,
            "conditions": [condition.dump() for condition in self._conditions],
            "type": self._type,
            "actions": [action.dump() for action in self._actions],
        }

    @classmethod
    def load(cls, data, field_registry, operator_registry, action_registry):
        return cls(
            data["title"],
            data["description"],
            [Condition.load(item, field_registry, operator_registry) for item in data["conditions"]],
            data["type"],
            [ActionWithValue.load(item, action_registry, field_registry) for item in data["actions"]],
            [],
            None,
        )

    def _execute(self, tree):
        # TODO: Investigate some kind of "LineRule" to split off line logic
        origins = [
            Origin(
                type=FieldType.LINE,
                identifier_name="LineNumber",
                get_identifier=get_line_identifier,
                base_path=LINE_BASE_PATH,
            ),
            Origin(
                type=FieldType.ORDER,
                identifier_name="OrderNumber",
                get_identifier=get_order_identifier,
                base_path=ORDER_BASE_PATH,
            ),
        ]
        for origin in origins:
            origin_conditions = origin.get_conditions(self._conditions)
            line_actions = self.get_line_actions()
            linecoding_actions = self.get_linecoding_actions()

            origin_els = origin.get_origin_elements(tree)
            # For every origin element, check if conditions match
            # If so, execute actions
            for origin_el in origin_els:
                if origin_conditions and self._match_origin_el(origin_el, origin.get_conditions(self._conditions)):
                    self.perform_line_actions(tree, origin_el, line_actions, origin)
                    self.perform_linecoding_actions(tree, origin_el, linecoding_actions, origin)

        header_actions = [action for action in self._actions if action.is_header_action()]

        for action in header_actions:
            action.perform(tree)

    def get_line_actions(self):
        return [action for action in self._actions if action.is_line_action()]

    def get_linecoding_actions(self):
        return [action for action in self._actions if action.is_linecoding_action()]

    def _execute_subrules(self, input_tree, output_tree):
        for subrule in self._subrules:
            subrule.perform(input_tree, output_tree)

    def perform_line_actions(self, tree, el, actions, origin):
        if len(actions) == 0:
            return

        identifier = origin.get_identifier(el)
        line = origin.get_line_for_identifier(tree, identifier)

        for action in actions:
            action.perform(el, line)

    def perform_linecoding_actions(self, tree, el, actions, origin):
        if len(actions) == 0:
            return

        ensure_linecoding_for_origin(tree, el, origin)
        identifier = origin.get_identifier(el)
        linecoding = origin.get_linecoding_for_identifier(tree, identifier)

        for action in actions:
            action.perform(el, linecoding)

    def _match_header(self, tree):
        conditions = [condition for condition in self._conditions if condition.is_header_condition()]

        if len(conditions) == 0:
            # has no header conditions at all, which is actually seen as a match
            return True

        excluded_conditions = [
            condition
            for condition in self._conditions
            if (condition.is_order_condition() or condition.is_line_condition())
        ]
        return self._match_global(tree, conditions, excluded_conditions)

    def _match_order(self, tree):
        conditions = [condition for condition in self._conditions if condition.is_order_condition()]

        if len(conditions) == 0:
            # has no order conditions at all, which is actually seen as a match
            return True

        excluded_conditions = [
            condition
            for condition in self._conditions
            if (condition.is_header_condition() or condition.is_line_condition())
        ]
        return self._match_global(tree, conditions, excluded_conditions)

    def _match_line(self, tree):
        conditions = [condition for condition in self._conditions if condition.is_line_condition()]

        if len(conditions) == 0:
            # has no line conditions at all, which is actually seen as a match
            return True

        excluded_conditions = [
            condition
            for condition in self._conditions
            if (condition.is_order_condition() or condition.is_header_condition())
        ]
        return self._match_global(tree, conditions, excluded_conditions)

    # match_global is used to see if ANY field matches the conditions for a rule. In the case of ORDER fields,
    # we can have N of them. The "regular" match still goes field by field
    def _match_global(self, tree, conditions, excluded_conditions):
        if len(conditions) == 0 and len(excluded_conditions) == 0:
            return True
        if len(conditions) == 0:
            return False

        if self._type == ANY:
            # match ANY, test for both conditions and excluded_conditions
            return self._match_any_global(tree, (conditions + excluded_conditions))
        elif self._type == ALL:
            # match ALL, test for conditions only
            return self._match_all_global(tree, conditions)
        raise Error("Unknown type: {}".format(self._type))

    def _match_all_global(self, tree, conditions):
        for condition in conditions:
            if not condition.match_global(tree):
                logger.debug("Not all condition(s) match")
                return False
        logger.debug("All condition(s) match")
        return True

    def _match_any_global(self, tree, conditions):
        for condition in conditions:
            if condition.match_global(tree):
                logger.debug("At least one condition matches")
                return True
        logger.debug("None of the condition(s) match")
        return False

    def _match_origin_el(self, origin_el, conditions):
        return self._match(origin_el, conditions)

    def _match(self, tree, conditions):
        if len(conditions) == 0:
            return True

        if self._type == ANY:
            return self._match_any(tree, conditions)
        elif self._type == ALL:
            return self._match_all(tree, conditions)
        raise Error("Unknown type: {}".format(self._type))

    def _match_all(self, tree, conditions):
        for condition in conditions:
            if not condition.match(tree):
                logger.debug("Not all condition(s) match")
                return False
        logger.debug("All condition(s) match")
        return True

    def _match_any(self, tree, conditions):
        for condition in conditions:
            if condition.match(tree):
                logger.debug("At least one condition matches")
                return True
        logger.debug("None of the condition(s) match")
        return False

    def _add_rule_in_xml(self, tree):
        if self._parent_rule is not None:
            return

        # test if <BusinessRules> is already in <Invoice>, else create
        # append <Rule><Title> self.title </Title></Rule
        logger.debug("add_rule_in_xml `%s`", self.title)

        try:
            rules = tree.xpath("/Invoice/BusinessRules")
        except AttributeError:
            # XML-tree does not exist, should only happen during pytest
            logger.error("Not xml-tree found in rule `%s`", self.title)
            return False

        if not rules:
            root = tree.xpath("/Invoice")[0]
            rules = etree.SubElement(root, "BusinessRules")
        else:
            rules = rules[0]

        # append <Rule><Title> self.title </Title></Rule
        rule = etree.SubElement(rules, "Rule")
        title = etree.SubElement(rule, "Title")
        title.text = self.title


class Rules:
    def __init__(self, rules):
        self._rules = rules

    def perform(self, input_tree):
        output_tree = deepcopy(input_tree)
        for rule in self._rules:
            # output tree can be modified during `perform`
            # we want to reuse that result as new input for the next rule
            input_tree = deepcopy(output_tree)
            rule.perform(input_tree, output_tree)
        return output_tree

    def dump(self):
        return {"rules": [rule.dump() for rule in self._rules]}

    @classmethod
    def load(cls, data, field_registry, operator_registry, action_registry):
        rules = [
            Rule.load(rule_item, field_registry, operator_registry, action_registry) for rule_item in data["rules"]
        ]
        return cls(rules)


class Condition:
    def __init__(self, field, operator, value):
        logger.debug("Init condition `%s`, `%s`, `%s`", field.id, operator.label, value)
        self._field = field
        self._operator = operator
        self._value = value
        self._datatyped_value = field.datatype.parse(value)

    def match_global(self, tree):
        # If we match on order_conditions or line_conditions, we have the possiblity of
        # N of those fields. If one of the N match, we return True
        if self.is_order_condition():
            extracted_values = [el.text for el in tree.xpath(ORDER_BASE_PATH)]
            for value in extracted_values:
                if self._operator.evaluate(value, self._value):
                    return True
            return False
        if self.is_line_condition():
            extracted_values = self._field.manipulators(tree, None)

            for value in extracted_values:
                if self._operator.evaluate(value.get(), self._datatyped_value):
                    return True
            return False

        # No order or line field -- continue as normal
        return self.match(tree)

    def match(self, tree):
        extracted_value = self._field.get(tree)

        logger.debug(
            "Match `%s`, value `%s` with extracted value `%s` ?",
            self._operator.label,
            self._value,
            extracted_value,
        )

        if extracted_value is None:
            return False
        return self._operator.evaluate(extracted_value, self._datatyped_value)

    def dump(self):
        value = self._operator.compare_datatype.serialize(self._value)
        return {"field": self._field.id, "operator": self._operator.id, "value": value}

    def get_type(self):
        return self._field._type

    def is_header_condition(self):
        return self._field.is_header_field()

    def is_line_condition(self):
        return self._field.is_line_field()

    def is_order_condition(self):
        return self._field.is_order_field()

    @classmethod
    def load(cls, data, field_registry, operator_registry):
        operator = operator_registry.get(data["operator"])
        value = operator.compare_datatype.parse(data["value"])
        return cls(field_registry.get(data["field"]), operator, value)


class Field:
    def __init__(
        self,
        id,
        label,
        datatype,
        xpath,
        attribute_name=None,
        attribute_value=None,
        choices=None,
        type=FieldType.HEADER,
    ):
        self.id = id
        self.label = label
        self.datatype = datatype
        self._xpath = xpath
        self._parent_xpath = xpath.rsplit("/", 1)[0]
        self._attribute_name = attribute_name
        self._attribute_value = attribute_value
        self._choices = choices
        self._type = type
        if choices is not None:
            self._choice_values = set([value for (dummy, value) in choices])
        else:
            self._choice_values = None

    def _get_manipulators_xpath(self, tree):
        if self._type == FieldType.HEADER or self._type == FieldType.EXTENSION or self._type == FieldType.CUSTOM:
            return self._xpath

        if isinstance(tree, etree._Element):
            # If we have an _Element, we want to work relative to that
            # element. To do that we make the manipulators xpath
            # <current_element>/foo. This is achieved by prefixing xpath with .
            return "." + self._xpath
        elif self._type == FieldType.LINECODING:
            return LINECODING_BASE_PATH + self._xpath
        elif self._type == FieldType.LINE:
            return LINE_BASE_PATH + self._xpath
        elif self._type == FieldType.ORDER:
            return ORDER_BASE_PATH + self._xpath
        else:
            raise Error("Unknown FieldType: {}".format(self._type))

    def _get_manipulators_element(self, tree):
        if (
            self._type == FieldType.HEADER
            or self._type == FieldType.EXTENSION
            or self._type == FieldType.CUSTOM
            or not isinstance(tree, etree._Element)
        ):
            return tree

        # The passed in element is of the same type as the field type, no need to do anything
        if self._type == FieldType.LINE and tree.tag == "Line":
            return tree
        elif self._type == FieldType.LINECODING and tree.tag == "LineCoding":
            return tree
        elif self._type == FieldType.ORDER and tree.tag == "OrderNumber":
            return tree

        # We need to find the appropriate line for linecoding or vice versa
        # because this field is of the other type than the input field
        # e.g. We got a Line field but need a linecoding element
        path = ""
        linenumber = tree.xpath("LineNumber")[0].text
        if self._type == FieldType.LINE:
            path = LINE_BASE_PATH + '/LineNumber[text()="' + linenumber + '"]'
        else:
            path = LINECODING_BASE_PATH + '/LineNumber[text()="' + linenumber + '"]'

        return tree.xpath(path)[0].getparent()

    def manipulators(self, tree, source_field):
        # Determine which element we want to operate on
        # For a linecoding type field we want to get the LineCoding element with
        # a certain linenumber
        manipulator_element = self._get_manipulators_element(tree)
        source_manipulator = None
        if source_field is not None:
            source_manipulator = source_field.get_first_manipulator(tree)

        # Xpath of the manipulator, can be absolute or relative depending on input
        # and type of field
        xpath = self._get_manipulators_xpath(tree)

        els = tree.xpath(xpath)
        if not els:
            return [
                Manipulator(
                    manipulator_element,
                    xpath,
                    self.datatype,
                    0,
                    self._attribute_name,
                    self._attribute_value,
                    True,
                    source_manipulator,
                )
            ]
        result = [
            Manipulator(
                manipulator_element,
                xpath,
                self.datatype,
                i,
                self._attribute_name,
                self._attribute_value,
                False,
                source_manipulator,
            )
            for i in range(len(els))
        ]
        result[0].first = True
        return result

    def get(self, tree):
        return self.get_first_manipulator(tree).get()

    def get_first_manipulator(self, tree):
        return self.manipulators(tree, None)[0]

    def get_allowed_operators(self, operator_registry):
        return operator_registry.all_by_datatype(self.datatype, self._choices is not None)

    def get_allowed_actions(self, action_registry):
        return action_registry.all_by_datatype(self.datatype, self._choices is not None)

    def get_choices(self):
        return self._choices

    def is_allowed_choice(self, value):
        if self._choices is None:
            return True
        # we always want to allow the None choice, because some operators
        # don't take a value
        if value is None:
            return True
        return value in self._choice_values

    def is_header_field(self):
        return self._type == FieldType.HEADER or self._type == FieldType.EXTENSION or self._type == FieldType.CUSTOM

    def is_line_field(self):
        return self._type == FieldType.LINE

    def is_linecoding_field(self):
        return self._type == FieldType.LINECODING

    def is_order_field(self):
        return self._type == FieldType.ORDER


class FieldRegistry:
    def __init__(self):
        self._fields = {}

    def clear(self):
        self._fields = {}

    def register(self, *args, **kw):
        field = Field(*args, **kw)
        self._fields[field.id] = field

    def get(self, id):
        return self._fields[id]

    def all(self):
        return self._fields.values()


class Operator:
    def __init__(
        self,
        id,
        label,
        func,
        extracted_datatype,
        compare_datatype,
        order=0,
        for_choices=False,
    ):
        logger.debug(
            "Init operator `%s`, extract `%s`, compare `%s`",
            label,
            extracted_datatype,
            compare_datatype,
        )
        self.id = id
        self.label = label
        self.extracted_datatype = extracted_datatype
        self.compare_datatype = compare_datatype
        self.order = order
        self._func = func
        self.for_choices = for_choices

    def evaluate(self, extracted_value, compare_value):
        logger.debug(
            "Evaluate operator `%s`, extract `%s`, compare `%s`",
            self._func,
            extracted_value,
            compare_value,
        )
        return self._func(extracted_value, compare_value)

    def convert(self, s):
        return self.compare_datatype.parse(s)


class OperatorRegistry:
    # lijst met operators om te gebruiken per datatype
    def __init__(self):
        self._operators_by_datatype = {}
        self._operators_by_id = {}
        self._order_count = 0

    def register(self, label, extracted_datatype, compare_datatype, order=None, for_choices=False):
        if order is None:
            order = self._order_count
            self._order_count += 1

        def decorator(func):
            id = func.__name__
            operator = Operator(
                id,
                label,
                func,
                extracted_datatype,
                compare_datatype,
                order,
                for_choices,
            )
            self._operators_by_datatype.setdefault(extracted_datatype, set()).add(operator)
            self._operators_by_id[id] = operator
            return func

        return decorator

    def get(self, id):
        return self._operators_by_id[id]

    def all_by_datatype(self, datatype, has_choices=False):
        result = self._operators_by_datatype.get(datatype, set())
        if has_choices:
            result = set([entry for entry in result if entry.for_choices])
        return result

    def all(self):
        return self._operators_by_id.values()


class ActionWithValue:
    def __init__(self, action, field, value, source_valuefield=None):
        self._action = action
        self._field = field
        if not field.is_allowed_choice(value):
            raise Error("Value not in choices: {}".format(value))
        self._value = value
        self._source_valuefield = source_valuefield

    def perform(self, tree, linecoding=None):
        self._action.perform(tree, self._field, self._value, linecoding, self._source_valuefield)

    def dump(self):
        value = self._action.value_datatype.serialize(self._value)

        return {"action": self._action.id, "field": self._field.id, "value": value}

    def is_header_action(self):
        return self._field.is_header_field()

    def is_line_action(self):
        return self._field.is_line_field()

    def is_linecoding_action(self):
        return self._field.is_linecoding_field()

    def is_order_action(self):
        return self._field.is_order_field()

    @classmethod
    def load(cls, data, action_registry, field_registry):
        action = action_registry.get(data["action"])
        value = action.value_datatype.parse(data["value"])
        return cls(action, field_registry.get(data["field"]), value)


def xpath_ensure_ancestors(tree, xpath):
    els = tree.xpath(xpath)
    if els:
        return els[0]
    # we need to make a parent
    parent_xpath, element_name = xpath.rsplit("/", 1)
    el = xpath_ensure_ancestors(tree, parent_xpath)

    return etree.SubElement(el, element_name)


class Origin:
    def __init__(self, type, identifier_name, get_identifier, base_path):
        self.type = type
        self.identifier_name = identifier_name
        self.get_identifier = get_identifier
        self.base_path = base_path

    def get_origin_elements(self, tree):
        return tree.xpath(self.base_path)

    def get_conditions(self, all_conditions):
        return [condition for condition in all_conditions if condition.get_type() == self.type]

    def is_known_identifier(self, tree, identifier):
        path = LINECODING_BASE_PATH + '/{}[text()="{}"]'.format(self.identifier_name, identifier)
        amount = len(tree.xpath(path))
        if amount == 0:
            return False
        if amount == 1:
            return True
        raise Error("Multiple CodingLines found with the same LineNumber")

    def set_identifier(self, el, identifier):
        line_number = etree.SubElement(el, self.identifier_name)
        line_number.text = identifier

    def get_line_for_identifier(self, tree, identifier):
        path = LINE_BASE_PATH + '/{}[text()="{}"]'.format(self.identifier_name, identifier)
        els = tree.xpath(path)
        return els[0].getparent()

    def get_linecoding_for_identifier(self, tree, identifier):
        path = LINECODING_BASE_PATH + '/{}[text()="{}"]'.format(self.identifier_name, identifier)
        els = tree.xpath(path)
        return els[0].getparent()


def get_order_identifier(el):
    return el.text


def get_line_identifier(el):
    result = el.xpath("LineNumber")
    if len(result) == 0:
        return None
    if len(result) > 1:
        raise Error("Should only have one identifier")
    else:
        return result[0].text


def ensure_linecoding_for_origin(tree, origin_el, origin):
    identifier = origin.get_identifier(origin_el)

    # No linenumber for Line, create both linenumber and linecoding
    if identifier is None:
        create_linecoding_and_identifier(tree, origin_el, origin)
    else:
        # There is a linenumber, just create a linecoding
        create_linecoding_for_identifier(tree, identifier, origin)


def create_linecoding_and_identifier(tree, origin_el, origin):
    # We need to create a new linecoding with a unique LineNumber
    # To get a unique LineNumber we can fetch the current number of
    # linecodings and add one to it
    linecoding_count = len(tree.xpath(LINECODING_BASE_PATH))
    linenumber = str(linecoding_count + 1)

    # Create the linecoding
    linecoding = etree.SubElement(tree.getroot(), "LineCoding")

    # Create and set the linenumber for both line and linecoding
    origin.set_identifier(linecoding, linenumber)
    origin.set_identifier(origin_el, linenumber)


def create_linecoding_for_identifier(tree, identifier, origin):
    if origin.is_known_identifier(tree, identifier):
        return

    # Create LineCoding for linenumber, since none exists
    linecoding = etree.SubElement(tree.getroot(), "LineCoding")
    origin.set_identifier(linecoding, identifier)


class Manipulator:
    """A way to interact with the XML through xpath."""

    def __init__(
        self,
        tree,
        xpath,
        datatype,
        index,
        attribute_name,
        attribute_value,
        first,
        source_manipulator,
    ):
        self._tree = tree
        self._xpath = xpath
        self._datatype = datatype
        self._index = index
        self._attribute_name = attribute_name
        self._attribute_value = attribute_value
        self.first = first
        self._source_manipulator = source_manipulator

    def get_element(self):
        # get element from XML via attribute_name and attribute_value
        if self._attribute_name is not None and self._attribute_value is not None:
            element = self._tree.xpath(self._xpath + "[@%s='%s']" % (self._attribute_name, self._attribute_value))
            return element[0] if element else None

        # get element straight from XML via XPath
        element = self._tree.xpath(self._xpath)

        # if we were not able to get the tag at all, return None
        return element[self._index] if element else None

    def has_source_manipulator(self):
        return self._source_manipulator is not None

    def get(self):
        if self.has_source_manipulator():
            return self._source_manipulator.get()

        # get element from XML
        el = self.get_element()
        if el is None:
            result = None
        # test if we need the value of the attribute
        elif self._attribute_name is not None and self._attribute_value is None:
            result = el.get(self._attribute_name)
        else:
            result = el.text
        if result is None:
            result = ""
        return self._datatype.parse(result)

    def set(self, value):
        """
        a few scenarios are supported here
        - just set the text-value of an element (ie. company_code)
        - and/or set the attribute_name + attribute_value with a fixed value (ie. generic_1)
        - and/or set the attribute_name with a fixed value,
          but the attribute_value with a variable text (ie. currency_code)
        """

        # get handle to element or create the element
        el = self.get_element()
        if el is None:
            el = xpath_ensure_ancestors(self._tree, self._xpath)

        # get text-value to set
        text = self._datatype.serialize(value)

        # test if we need to set attribute_name(s)/attribute_value(s)
        if self._attribute_name is not None:
            if self._attribute_value is None:
                # and/or set the attribute_name with a fixed value,
                # but the attribute_value with a variable text (ie. currency_code)
                el.set(self._attribute_name, text)
                return
            # and/or set the attribute_name + attribute_value with a fixed value (ie. generic_1)
            # do not return/exit here, because we might also want to set the text
            el.set(self._attribute_name, self._attribute_value)

        # just set the text-value of an element (ie. company_code)
        el.text = text

    def delete(self):
        el = self.get_element()
        if el is None:
            return

        if self._attribute_name is not None and self._attribute_value is None:
            # we are deleting an attribute
            if self._attribute_name in el.attrib:
                del el.attrib[self._attribute_name]
        else:
            # delete the element itself
            el.getparent().remove(el)


class Action:
    def __init__(
        self,
        id,
        label,
        field_datatype,
        value_datatype,
        func,
        order=0,
        for_choices=False,
        source_valuefield=None,
    ):
        self.id = id
        self.label = label
        self.field_datatype = field_datatype
        self.value_datatype = value_datatype
        self.order = order
        self._func = func
        self.for_choices = for_choices
        self._source_valuefield = source_valuefield

    def perform(self, tree, field, value, linecoding=None, source_field=None):
        element = tree

        if not field.is_header_field() and linecoding is not None:
            element = linecoding

        self._perform_for_element(element, field, value, source_field)

    def _perform_for_element(self, element, field, value, source_field):
        # go through manipulators in reverse order. This way we don't
        # shift the element indexes and this makes delete of multiple items
        # work
        for manipulator in reversed(field.manipulators(element, source_field)):
            self._func(manipulator, value)

    def convert(self, s):
        return self.value_datatype.parse(s)


class ActionRegistry:
    def __init__(self):
        self._actions_by_datatype = {}
        self._actions_by_id = {}
        self._order_count = 0

    def register(self, label, field_datatype, value_datatype, order=None, for_choices=False):
        if order is None:
            order = self._order_count
            self._order_count += 1

        def decorator(func):
            id = func.__name__
            action = Action(id, label, field_datatype, value_datatype, func, order, for_choices)
            self._actions_by_datatype.setdefault(field_datatype, set()).add(action)
            self._actions_by_id[id] = action
            return func

        return decorator

    def get(self, id):
        return self._actions_by_id[id]

    def all_by_datatype(self, datatype, has_choices=False):
        result = self._actions_by_datatype.get(datatype, set())
        if has_choices:
            result = set([entry for entry in result if entry.for_choices])
        return result

    def all(self):
        return self._actions_by_id.values()


class Error(Exception):
    pass
