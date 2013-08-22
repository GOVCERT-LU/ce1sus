"""module holding all controllers needed for the event handling"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.web.controllers.base import BaseController
import cherrypy
from ce1sus.web.helpers.protection import require
from ce1sus.brokers.eventbroker import EventBroker, ObjectBroker, \
                  AttributeBroker, Attribute
from ce1sus.brokers.definitionbroker import AttributeDefinitionBroker
from ce1sus.web.helpers.protection import privileged
from framework.db.broker import ValidationException, \
BrokerException


class AttributesController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.attributeBroker = self.brokerFactory(AttributeBroker)
    self.def_attributesBroker = self.brokerFactory(AttributeDefinitionBroker)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)

  @require(privileged())
  @cherrypy.expose
  def index(self):

    """
    renders the events page

    :returns: generated HTML
    """

    return self.__class__.__name__ + ' is not implemented'

  @cherrypy.expose
  def addAttribute(self, eventID, objectID):
    """
     renders the file for adding attributes

    :returns: generated HTML
    """
    template = self.getTemplate('/events/event/attributes/attributesModal.html')
    obj = self.objectBroker.getByID(objectID)
    cbDefinitions = self.def_attributesBroker.getCBValues(
                                                    obj.definition.identifier)
    return template.render(eventID=eventID,
                           objectID=objectID,
                           attribute=None,
                           cbDefinitions=cbDefinitions,
                           errorMsg=None,
                           enabled=True)


  @cherrypy.expose
  @require()
  def modifyAttribute(self, eventID=None, attributeID=None,
                            objectID=None, definition=None, value=None,
                            action=None):
    """
    Modification on the attributes of objects
    """
    event = self.eventBroker.getByID(eventID)

    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)

    try:

      obj = self.objectBroker.getByID(objectID)

      attribute = Attribute()
      if not action == 'insert':
        attribute.identifier = attributeID

      if not action == 'remove':
        attribute.object_id = obj.identifier
        attribute.object = obj

        # get definition
        definition = self.def_attributesBroker.getByID(definition)
        attribute.def_attribute_id = definition.identifier
        attribute.definition = definition

        attribute.value = value
        attribute.creator = self.getUser()
        attribute.user_id = attribute.creator.identifier


      try:
        if action == 'insert':
          self.attributeBroker.insert(attribute)
        if action == 'update':
          attribute.identifier = attributeID
          temp = self.attributeBroker.getByID(attributeID)
          attribute.value_id = temp.value_id
          self.attributeBroker.update(attribute)
        if action == 'remove':
          temp = self.attributeBroker.getByID(attributeID)
          obj.removeAttribute(temp)

        return self.returnAjaxOK()
        # update last_seen
        # TODO: Update Event
        # self.updateEvent(event, False)
      except ValidationException as e:
        self.getLogger().info(e)
        template = self.getTemplate('/events/event/attributes/'
                                    + 'attributesModal.html')
        cbDefinitions = self.def_attributesBroker.getCBValues(
                                                    obj.definition.identifier)
        return template.render(eventID=eventID,
                           objectID=objectID,
                           attribute=attribute,
                           cbDefinitions=cbDefinitions,
                           errorMsg=None)




    except BrokerException as e:
      template = self.getTemplate('/events/event/attributes/'
                                  + 'attributesModal.html')
      obj = self.objectBroker.getByID(objectID)
      cbDefinitions = self.def_attributesBroker.getCBValues(
                                                    obj.definition.identifier)
      return template.render(eventID=eventID,
                           objectID=objectID,
                           attribute=attribute,
                           cbDefinitions=cbDefinitions,
                           errorMsg=e)

  @cherrypy.expose
  @require()
  def view(self, eventID, objectID, attributeID, enabled=False):
    """
     renders the file with the requested attribute

    :returns: generated HTML
    """
    template = self.getTemplate('/events/event/attributes/attributesModal.html')
    obj = self.objectBroker.getByID(objectID);
    cbDefinitions = self.def_attributesBroker.getCBValues(
                                                    obj.definition.identifier)
    attribute = self.attributeBroker.getByID(attributeID)
    return template.render(eventID=eventID,
                           objectID=objectID,
                           attribute=attribute,
                           cbDefinitions=cbDefinitions,
                           errorMsg=None,
                           enabled=enabled)


  @cherrypy.expose
  @require()
  def edit(self, eventID, objectID, attributeID):
    """
     renders the file with the requested comment

    :returns: generated HTML
    """
    # is the same just that some elements are enabled
    return self.view(eventID, objectID, attributeID, True)
