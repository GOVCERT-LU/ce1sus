# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""


from ce1sus.db.classes.internal.common import ValueTable
from ce1sus.handlers.base import AttributeHandlerBase

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class GenericHandler(AttributeHandlerBase):
  """The generic handler for handling known atomic values"""
  @staticmethod
  def get_uuid():
    return 'dea62bf0-8deb-11e3-baa8-0800200c9a66'

  @staticmethod
  def get_description():
    return u'Generic Handler, usable for a single line entry'

  @staticmethod
  def get_additional_object_uuids():
    return list()

  @staticmethod
  def get_allowed_types():
    return [ValueTable.TEXT_VALUE,
            ValueTable.STRING_VALUE,
            ValueTable.NUMBER_VALUE
            ]

  @staticmethod
  def get_additinal_attribute_uuids():
    return list()

  def assemble(self, obj, json):
    attribute = self.create_attribute(obj, json)
    return [attribute]

  @staticmethod
  def get_view_type():
    return 'plain'

  @staticmethod
  def require_js():
    return False
