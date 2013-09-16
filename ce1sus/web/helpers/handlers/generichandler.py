# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.helpers.handlers.base import HandlerBase
from ce1sus.brokers.eventbroker import Attribute
from datetime import datetime

class GenericHandler(HandlerBase):
  """The generic handler for handling known atomic values"""
  def __init__(self):
    HandlerBase.__init__(self)

  def populateAttributes(self, params, obj, definition, user):
    attribute = Attribute()
    attribute.identifier = None
    attribute.value = params.get('value')
    attribute.obejct = obj
    attribute.object_id = obj.identifier
    attribute.def_attribute_id = definition.identifier
    attribute.definition = definition
    attribute.created = datetime.now()
    attribute.modified = datetime.now()
    attribute.creator = user
    attribute.creator_id = user.identifier
    attribute.modifier_id = user.identifier
    attribute.modifier = user
    attribute.creator = user
    return attribute

  def getAttributesNameList(self):
    return list()

  def render(self, enabled, eventID, user, attribute=None):
    template = (self.
                  getTemplate('/events/event/attributes/handlers/generic.html'))
    string = template.render(attribute=attribute, enabled=enabled)
    return string

  def convertToAttributeValue(self, value):
    return value.value
