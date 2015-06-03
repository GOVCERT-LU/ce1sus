# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""


from ce1sus.handlers.base import HandlerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class GenericHandler(HandlerBase):
    """The generic handler for handling known atomic values"""

    @staticmethod
    def get_uuid():
        return '4af84930-97e8-11e4-bd06-0800200c9a66'

    @staticmethod
    def get_description():
        return u'Generic Handler, usable for a single line entry'

    def insert(self, report, user, json):
        definition = self.get_main_definition()
        reference = self.create_reference(report, definition, user, json)
        value = json.get('value', None)
        reference.value = value
        return reference, None, None

    def get_data(self, reference, parameters):
        return list()

    def get_view_type(self):
        return 'plain'

    def update(self, reference, user, json):
        reference.populate(json)
        return reference

    def require_js(self):
        return False

    def get_additinal_reference_chksums(self):
        return list()

    def get_additinal_attribute_chksums(self):
        return self.get_additinal_reference_chksums()
