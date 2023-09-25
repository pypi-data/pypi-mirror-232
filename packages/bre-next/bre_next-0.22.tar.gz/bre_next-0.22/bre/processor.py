import io
import logging

from lxml import etree

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self, rules):
        self._rules = rules

    def perform(self, file, file_name):
        try:
            file_tree = etree.parse(file)
        except Exception as e:
            logger.error("Error processing {}".format(file_name))
            logger.exception(e)
            return None
        output_tree = self._rules.perform(file_tree)
        output_as_string = etree.tostring(output_tree, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        return io.BytesIO(output_as_string)
