# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.web.controllers.base import BaseController
import cherrypy
from ce1sus.web.helpers.protection import require
from ce1sus.brokers.eventbroker import EventBroker, ObjectBroker, \
                  AttributeBroker, Attribute
from ce1sus.brokers.definitionbroker import AttributeDefinitionBroker
from ce1sus.web.helpers.protection import requireReferer
from dagr.db.broker import ValidationException, \
BrokerException
from ce1sus.web.helpers.handlers.base import HandlerException
import types
from dagr.web.helpers.pagination import Paginator
from ce1sus.api.ticketsystem import TicketSystemBase
from ce1sus.web.helpers.handlers.base import HandlerBase
from cherrypy.lib.static import serve_file
from ce1sus.brokers.valuebroker import ValueBroker

class AttributesController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.attributeBroker = self.brokerFactory(AttributeBroker)
    self.def_attributesBroker = self.brokerFactory(AttributeDefinitionBroker)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)
    self.valueBroker = self.brokerFactory(ValueBroker)

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the events page

    :returns: generated HTML
    """
    return self.__class__.__name__ + ' is not implemented'

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def addAttribute(self, eventID, objectID):
    """
     renders the file for adding attributes

    :returns: generated HTML
    """
    # Clear Session variable
    getattr(cherrypy, 'session')['instertAttribute'] = None
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)

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
  @require(requireReferer(('/internal')))
  def addFile(self, eventID, value=None):
    """
    Uploads a file to the tmp dir
    """

    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)

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
    if size == 0:
      self.getLogger().fatal('Upload of the given file failed.')
    filepath = '/tmp/' + value.filename
    return self.returnAjaxOK() + '*{0}*'.format(filepath)


  # pylint: disable=R0914,R0912
  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def modifyAttribute(self, **kwargs):
    """
    Modification on the attributes of objects
    """
    # Clear Session variable
    getattr(cherrypy, 'session')['instertAttribute'] = None

    eventID = kwargs.get('eventID', None)
    if not eventID is None:
      attributeID = kwargs.get('attributeID', None)
      objectID = kwargs.get('objectID', None)
      definition = kwargs.get('definition', None)
      action = kwargs.get('action', None)
      values = kwargs.get('value', None)
      # remove unnecessary elements from the parameters
      params = { k : v for k, v in kwargs.iteritems() if k not in ['eventID',
                                                                'attributeID',
                                                                   'objectID',
                                                                   'definition',
                                                                   'action'] }
      # right checks
      event = self.eventBroker.getByID(eventID)
      self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)
      obj = self.objectBroker.getByID(objectID)
      try:
        if action != 'remove':
          definition = self.def_attributesBroker.getByID(definition)
          handler = HandlerBase.getHandler(definition)
          # expect generated attributes back
          attributes = handler.populateAttributes(params,
                                                  obj,
                                                  definition,
                                                  self.getUser())
          if attributes is None:
            raise HandlerException(('{0}.getAttributes '
                                    + 'does not return attributes ').format(
                                                      definition.handlerName))
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
          # update last seen etc of event
          self.eventBroker.updateLastSeen(event, self.getUser(), False)
        if action == 'remove':
          self.attributeBroker.removeByID(attributeID, commit=True)
        self.attributeBroker.doCommit(True)
        return self.returnAjaxOK()
      except ValidationException as e:
        self.getLogger().info(e)
      except BrokerException as e:
        self.getLogger().fatal(e)
        return "Error {0}".format(e)
      except HandlerException as e:
        self.getLogger().fatal(e)
        return "Error {0}".format(e)
      template = self.getTemplate('/events/event/attributes/'
                                    + 'attributesModal.html')
      cbDefinitions = self.def_attributesBroker.getCBValues(
                                                      obj.definition.identifier)
      if not (attributes is None):
        if (len(attributes) == 1):
          attribute = attributes[0]
        else:
          attribute = attributes[0]
          attribute.value = values
        # store in session
        getattr(cherrypy, 'session')['instertAttribute'] = attribute
      return self.returnAjaxPostError() + template.render(eventID=eventID,
                             objectID=objectID,
                             attribute=attribute,
                             cbDefinitions=cbDefinitions,
                             errorMsg=None,
                             enabled=True)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def view(self, eventID, objectID, attributeID):
    """
     renders the file with the requested attribute

    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)

    template = self.getTemplate('/events/event/attributes/attributesModal.html')
    obj = self.objectBroker.getByID(objectID)
    cbDefinitions = self.def_attributesBroker.getCBValues(
                                                    obj.definition.identifier)
    attribute = self.attributeBroker.getByID(attributeID)
    return template.render(eventID=eventID,
                           objectID=objectID,
                           attribute=attribute,
                           cbDefinitions=cbDefinitions,
                           errorMsg=None,
                           enabled=False)

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def inputHandler(self, defattribID, eventID, enabled, attributeID=None):
    """
    renders the form or input of the requested handler

    :param defattribID: ID of the selected definition
    :type defattribID: Integer
    :param enabled: Set to '1' if the inputs are enables
    :type enabled: String
    :param attributeID: the if of the desited displayed attribute
    :type attributeID: Integer

    :returns: generated HTML
    """

    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)

    # get Definition
    attribute = None
    if (not attributeID is None) and (attributeID != 'None'):
      attribute = self.attributeBroker.getByID(attributeID)
    else:
      # is an attribute in the session
      try:
        attribute = getattr(cherrypy, 'session')['instertAttribute']
      except KeyError:
        attribute = None

    if attribute is None:
      definition = self.def_attributesBroker.getByID(defattribID)
    else:
      definition = attribute.definition

    handler = HandlerBase.getHandler(definition)
    if enabled == '1':
      enableView = True
    else:
      enableView = False
    return handler.render(enableView, eventID, self.getUser(), attribute)

  @require(requireReferer(('/internal')))
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
    rtPaginator = Paginator(items=TicketSystemBase.
                            getInstance().getAllTickets(),
                            labelsAndProperty=labels)
    return template.render(rtPaginator=rtPaginator,
                           rtUrl=TicketSystemBase.
                           getInstance().getBaseTicketUrl())

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def file(self, eventID, attributeID, action):
    """
    Returns a file to download
    """
    # right checks
    del action
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)
    attribute = self.attributeBroker.getByID(attributeID)
    stringValue = self.valueBroker.getByID(attribute.value_id)
    filepath = stringValue.value
    return serve_file(filepath, "application/x-download", "attachment")
