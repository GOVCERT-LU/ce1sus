# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""


from ce1sus.db.classes.common import ValueTable
from ce1sus.handlers.base import HandlerBase, HandlerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class GenericHandler(HandlerBase):
    """The generic handler for handling known atomic values"""

    @staticmethod
    def get_uuid():
        return 'dea62bf0-8deb-11e3-baa8-0800200c9a66'

    @staticmethod
    def get_description():
        return u'Generic Handler, usable for a single line entry'

    def get_additional_object_chksums(self):
        return list()

    @staticmethod
    def get_allowed_types():
        return [ValueTable.TEXT_VALUE,
                ValueTable.STRING_VALUE,
                ValueTable.NUMBER_VALUE
                ]

    def get_additinal_attribute_chksums(self):
        return list()

    def insert(self, obj, user, json):
        definition = self.get_main_definition()
        attribute = self.create_attribute(obj, definition, user, json)
        return [attribute], None

    def get_data(self, attribute, parameters):
        return list()

    def get_view_type(self):
        return 'plain'

    def update(self, attribute, user, json):
        attribute.populate(json)
        return attribute

    def require_js(self):
        return False

    def get_main_attribute(self, attributes):
        main_def = self.get_main_definition()
        for attr in attributes:
            if attr.definition.uuid == main_def.uuid:
                return attr
        raise HandlerException('Main attribute cannot be found')
