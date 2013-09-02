"""module holding all controllers needed for the event handling"""
from cgitb import handler

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
from ce1sus.web.helpers.handlers.base import HandlerException, HandlerBase
import types
from importlib import import_module
from framework.web.helpers.pagination import Paginator, PaginatorOptions
from ce1sus.api.ticketsystem import TicketSystemBase

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
  def addFile(self, value=None):
    if value.file is None:
      return 'No file selected. Try again.'
    size = 0
    fileObj = open('/tmp/' + value.filename, 'a')
    while True:
      data = value.file.read(8192)
      if not data:
        break
      fileObj.write(data)
      size += len(data)
    fileObj.close()

    filepath = '/tmp/' + value.filename
    return self.returnAjaxOK() + '*{0}*'.format(filepath)


  def __getHandler(self, definition):

    # GethandlerClass
    temp = definition.handlerName.rsplit('.', 1)
    module = import_module('.' + temp[0], 'ce1sus.web.helpers.handlers')
    clazz = getattr(module, temp[1])
    # instantiate
    handler = clazz()
    # check if handler base is implemented
    if not isinstance(handler, HandlerBase):
       raise HandlerException('{0} does not implement HandlerBase'.format(definition.handlerName))
    return handler

  @cherrypy.expose
  @require()
  def modifyAttribute(self, **kwargs):
                      # eventID=None, attributeID=None,
                      #      objectID=None, definition=None, value=None,
                      #      action=None):
    """
    Modification on the attributes of objects
    """
    params = cherrypy.request.params
    eventID = params.get('eventID', None)
    attributeID = params.get('attributeID', None)
    objectID = params.get('objectID', None)
    definition = params.get('definition', None)
    action = params.get('action', None)
    # remove unnecessary elements from the parameters
    params = { k : v for k, v in params.iteritems() if k not in ['eventID', 'attributeID', 'objectID', 'definition', 'action'] }


    errorMsg = ''
    attributes = list()
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)
    obj = self.objectBroker.getByID(objectID)
    try:
      if action != 'remove':

        definition = self.def_attributesBroker.getByID(definition)
        handler = self.__getHandler(definition)
        # expect generated attributes back
        attributes = handler.populateAttributes(params, obj, definition, self.getUser())  # from handler
        if attributes is None:
          raise HandlerException('{0}.getAttributes does not return attributes '.format(definition.handlerName))


        if not isinstance(attributes, types.StringTypes):
          if not isinstance(attributes, types.ListType):
            if isinstance(attributes, Attribute):
              temp = attributes
              attributes = list()
              attributes.append(temp)

      # doAction for all attributes
      if action == 'insert':
        for attribute in attributes:
          self.attributeBroker.insert(attribute, commit=False)
        self.attributeBroker.doCommit(True)
      if action == 'remove':
        self.attributeBroker.removeByID(attributeID, commit=True)


      return self.returnAjaxOK()
    except ValidationException as e:
      self.getLogger().info(e)
      errorMsg = e

    except BrokerException as e:
      errorMsg = e

    except HandlerException as e:
      errorMsg = e


    template = self.getTemplate('/events/event/attributes/'
                                  + 'attributesModal.html')

    cbDefinitions = self.def_attributesBroker.getCBValues(
                                                    obj.definition.identifier)
    if not (attributes is None):
      if (len(attributes) > 1):
        attribute = None
        errorMsg = '{0} Please try again'.format(errorMsg)
      else:
        if (len(attributes) == 1):
          attribute = attributes[0]
    else:
      attribute = None

    return template.render(eventID=eventID,
                           objectID=objectID,
                           attribute=attribute,
                           cbDefinitions=cbDefinitions,
                           errorMsg=errorMsg)

  @cherrypy.expose
  @require()
  def view(self, eventID, objectID, attributeID):
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
                           enabled=False)

  @cherrypy.expose
  def inputHandler(self, defattribID, enabled, attributeID=None):
    # get Definition
    definition = self.def_attributesBroker.getByID(defattribID)
    handler = self.__getHandler(definition)
    attribute = None
    if not attributeID is None:
      attribute = self.attributeBroker.getByID(attributeID)
    if enabled == '1':
      enableView = True
    else:
      enableView = False
    return handler.render(enableView, attribute)

  @cherrypy.expose
  def getTickets(self):
    """
    renders the file for displaying the tickets out of RT

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/event/attributes/tickets.html')
    labels = [{'idLink':'#'},
              {'title':'Title'},
              {'selector':'Options'}]
    # the labels etc is handled by the RTTable.html
    rtPaginator = Paginator(items=TicketSystemBase.getInstance().getAllTickets(),
                          labelsAndProperty=labels)
    return template.render(rtPaginator=rtPaginator,
                           rtUrl=TicketSystemBase.getInstance().getBaseTicketUrl())
