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

  def insert(self, obj, user, json):
    definition = self.get_main_definition()
    attribute = self.create_attribute(obj, definition, user, json)
    return attribute, None, None

  def get_data(self, attribute, parameters):
    return list()

  def get_view_type(self):
    return 'plain'

  def update(self, attribute, user, json):
    attribute.populate(json)
    return attribute

  def require_js(self):
    return False
