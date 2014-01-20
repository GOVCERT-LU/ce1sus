# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.helpers.handlers.generichandler import GenericHandler
from dagr.helpers.strings import plaintext2html


class TextHandler(GenericHandler):
  """The generic handler for handling known atomic values"""
  def __init__(self):
    GenericHandler.__init__(self)

  def render(self, enabled, eventID, enableShare, user, definition, attribute=None):
    template = (self.
                getTemplate('/events/event/attributes/handlers/text.html')
                )
    if definition.share:
      defaultShareValue = 1
    else:
      defaultShareValue = 0
    string = template.render(attribute=attribute,
                             enabled=enabled,
                             defaultShareValue=defaultShareValue,
                             enableShare=enableShare)
    return string

  def convertToAttributeValue(self, value):
    return value.value
