from ce1sus.web.helpers.handlers.base import HandlerBase
from ce1sus.brokers.eventbroker import Attribute
from datetime import datetime

class GenericHandler(HandlerBase):

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

  def render(self, enabled, attribute=None):
    template = self.getTemplate('/events/event/attributes/handlers/generic.html')
    string = template.render(attribute=attribute, enabled=enabled)
    return string

  def convertToAttributeValue(self, value):
    return value.value
