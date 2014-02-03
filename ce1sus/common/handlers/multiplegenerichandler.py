# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Sep 19, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.common.handlers.generichandler import GenericHandler
import dagr.helpers.strings as strings


class MultipleGenericHandler(GenericHandler):

  def populate_attributes(self, params, obj, definition, user):
    attributes = list()
    values = params.get('value').split('\n')
    for value in values:
      stringValue = value.replace('\r', '')
      if (strings.isNotNull(stringValue)):
        params['value'] = stringValue
        attribute = GenericHandler.populate_attributes(self,
                                                    params,
                                                    obj,
                                                    definition,
                                                    user)
        attributes.append(attribute)
    return attributes

  def render(self, enabled, eventID, enableShare, user, definition, attribute=None):
    return self.renderTemplate('/events/event/attributes/handlers/multGeneric.html',
                               attribute,
                               definition,
                               enabled,
                               enableShare)