# -*- coding: utf-8 -*-

"""
module providing support for tickets handling

Created: Aug, 2013
"""
from ce1sus.handlers.references.generichandler import GenericHandler


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class LinkHandler(GenericHandler):

  @staticmethod
  def get_uuid():
    return 'b69aca60-a2dc-11e4-bcd8-0800200c9a66'

  @staticmethod
  def get_description():
    return u'Handler for Links'

  @staticmethod
  def get_view_type():
    return 'link'

  @staticmethod
  def require_js():
    return False
