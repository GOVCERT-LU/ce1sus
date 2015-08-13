# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""
from ce1sus.db.classes.internal.common import ValueTable
from ce1sus.handlers.attributes.generichandler import GenericHandler


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class TextHandler(GenericHandler):
  """The generic handler for handling known atomic values"""
  @staticmethod
  def get_uuid():
    return '1a8ec7d0-8dec-11e3-baa8-0800200c9a66'

  @staticmethod
  def get_description():
    return u'Text Handler, usable for a textlines'

  def get_additional_object_chksums(self):
    return list()

  @staticmethod
  def get_allowed_types():
    return [ValueTable.TEXT_VALUE]

  def get_additinal_attribute_chksums(self):
    return list()

  def get_view_type(self):
    return 'text'
