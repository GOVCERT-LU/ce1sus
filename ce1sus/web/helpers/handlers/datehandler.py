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


class DateHandler(GenericHandler):
  """The generic handler for handling known atomic values"""

  def render(self, enabled, eventID, enableShare, user, definition, attribute=None):
    return self.renderTemplate('/events/event/attributes/handlers/datetime.html',
                               attribute,
                               definition,
                               enabled,
                               enableShare)
