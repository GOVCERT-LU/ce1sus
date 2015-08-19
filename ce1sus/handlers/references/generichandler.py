# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""


from ce1sus.handlers.base import ReferenceHandlerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class GenericHandler(ReferenceHandlerBase):
  """The generic handler for handling known atomic values"""

  @staticmethod
  def get_uuid():
    return '4af84930-97e8-11e4-bd06-0800200c9a66'

  @staticmethod
  def get_description():
    return u'Generic Handler, usable for a single line entry'

  def assemble(self, report, json):
    reference = self.create_reference(report, json)
    return [reference]

  @staticmethod
  def get_view_type():
    return 'plain'

  @staticmethod
  def require_js():
    return False

  @staticmethod
  def get_additinal_reference_uuids():
    return list()
