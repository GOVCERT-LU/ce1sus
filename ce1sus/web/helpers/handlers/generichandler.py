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
from ce1sus.brokers.event.attributebroker import Attribute
from dagr.helpers.datumzait import datumzait
from dagr.helpers.converters import ObjectConverter
from ce1sus.helpers.bitdecoder import BitValue


class GenericHandler(HandlerBase):
  """The generic handler for handling known atomic values"""
  def __init__(self):
    HandlerBase.__init__(self)
    self.definition = None

  def populateAttributes(self, params, obj, definition, user):
    attribute = Attribute()
    attribute.identifier = None
    value = params.get('value')
    if isinstance(value, list):
      value = value[0]
    attribute.value = value.strip()
    attribute.obejct = obj
    attribute.object_id = obj.identifier
    attribute.definition = definition
    attribute.def_attribute_id = definition.identifier
    attribute.definition = definition
    attribute.created = datumzait.utcnow()
    attribute.modified = datumzait.utcnow()
    attribute.creator = user
    attribute.creator_id = user.identifier
    attribute.modifier_id = user.identifier
    attribute.modifier = user
    attribute.creator = user
    ObjectConverter.setInteger(attribute,
                               'ioc',
                               params.get('ioc', '0').strip())
    attribute.bitValue = BitValue('0', attribute)
    attribute.bitValue.isWebInsert = True
    attribute.bitValue.isValidated = True
    if definition.share == 1:
      attribute.bitValue.isSharable = True
    else:
      attribute.bitValue.isSharable = False
    return attribute

  def getAttributesIDList(self):
    return list()

  def render(self, enabled, eventID, user, definition, attribute=None):
    template = (self.
                  getTemplate('/events/event/attributes/handlers/generic.html')
                  )
    if definition.share:
      defaultShareValue = 1
    else:
      defaultShareValue = 0
    string = template.render(attribute=attribute,
                             enabled=enabled,
                             defaultShareValue=defaultShareValue)
    return string

  def convertToAttributeValue(self, value):
    return value.value
