# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""
from ce1sus.db.classes.internal.common import ValueTable
from ce1sus.handlers.references.generichandler import GenericHandler


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class TextHandler(GenericHandler):
  """The generic handler for handling known atomic values"""
  @staticmethod
  def get_uuid():
    return '04fc6ca0-d3c4-11e4-8830-0800200c9a66'

  @staticmethod
  def get_description():
    return u'Text Handler, usable for a textlines'

  @staticmethod
  def get_allowed_types():
    return [ValueTable.TEXT_VALUE]

  @staticmethod
  def get_view_type():
    return 'text'
