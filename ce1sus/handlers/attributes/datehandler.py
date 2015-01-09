# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""
from ce1sus.db.classes.common import ValueTable
from ce1sus.handlers.attributes.generichandler import GenericHandler


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class DateHandler(GenericHandler):
  """The generic handler for handling known atomic values"""

  @staticmethod
  def get_uuid():
    return '11406d00-8dec-11e3-baa8-0800200c9a66'

  @staticmethod
  def get_description():
    return u'Handler for Dates'

  @staticmethod
  def get_allowed_types():
    return [ValueTable.DATE_VALUE]

  def get_view_type(self):
    return 'date'
