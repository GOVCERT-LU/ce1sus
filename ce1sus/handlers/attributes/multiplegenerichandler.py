# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Sep 19, 2013
"""
import types

from ce1sus.handlers.attributes.generichandler import GenericHandler


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MultipleGenericHandler(GenericHandler):

  @staticmethod
  def get_uuid():
    return '08645c00-8dec-11e3-baa8-0800200c9a66'

  @staticmethod
  def get_description():
    return u'Multiple Generic Handler, usable for a multi-line entries'

  def insert(self, obj, user, json):
    value = json.get('value', None)
    if value:
      definition = self.get_main_definition()
      if isinstance(value, types.StringTypes):
        values = self.__get_string_attribtues(value)
      else:
        values = value
      attributes = list()
      for value in values:
        value = value.strip('\n\r')
        json['value'] = value
        attribute = self.create_attribute(obj, definition, user, json)
        attributes.append(attribute)
      attribute = attributes.pop(0)
      return attribute, attributes, None

  def __get_string_attribtues(self, value):
    return value.split('\n')

  def get_view_type(self):
    return 'multiline'
