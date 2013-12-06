# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                                  AttributeDefinitionBroker, \
                                                  AttributeDefinition
from ce1sus.web.helpers.protection import require, privileged, requireReferer
from dagr.db.broker import BrokerException, \
                          ValidationException, NothingFoundException, \
                          DeletionException, OperationException
import types as types


class AttributeController(Ce1susBaseController):
  """Controller handling all the requests for attributes"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.attributeBroker = self.brokerFactory(AttributeDefinitionBroker)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the attribute page

    :returns: generated HTML
    """

    template = self.getTemplate('/admin/attributes/attributeBase.html')
    return self.cleanHTMLCode(template.render())

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def leftContent(self):
    """
    renders the left content of the attribute index page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/attributes/attributeLeft.html')

    attributes = self.attributeBroker.getAll()
    return self.cleanHTMLCode(template.render(attributes=attributes))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def rightContent(self, attributeid=0, attribute=None):
    """
    renders the right content of the attribute index page

    :param attributeid: The attribute id of the desired displayed attribute
    :type attributeid: Integer
    :param attribute: Similar to the previous attribute but prevents
                      additional loadings
    :type attribute: AttributeDefinition

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/attributes/attributeRight.html')

    if attribute is None:
      try:
        attribute = self.attributeBroker.getByID(attributeid)
      except NothingFoundException:
        attribute = None

    else:
      attribute = attribute

    remainingObjects = None
    attributeObjects = None
    if not attribute is None:
      remainingObjects = self.attributeBroker.getObjectsByAttribute(
                                                attribute.identifier, False)
      attributeObjects = attribute.objects

    cbValues = AttributeDefinition.getTableDefinitions()
    return self.cleanHTMLCode(template.render(attributeDetails=attribute,
                           remainingObjects=remainingObjects,
                           attributeObjects=attributeObjects,
                  cbHandlerValues=AttributeDefinition.getHandlerDefinitions(),
                           cbValues=cbValues))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def addAttribute(self):
    """
    renders the add an attribute page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/attributes/attributeModal.html')
    cbValues = AttributeDefinition.getTableDefinitions()
    cbHandlerValues = AttributeDefinition.getHandlerDefinitions()
    return self.cleanHTMLCode(template.render(attribute=None,
                           errorMsg=None,
                           cbValues=cbValues,
                           cbHandlerValues=cbHandlerValues))

  # pylint: disable=R0913
  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def modifyAttribute(self, identifier=None, name=None, description='',
                      regex='^.*$', classIndex=0, action='insert',
                      handlerIndex=0, share=None, relation=None):
    """
    modifies or inserts an attribute with the data of the post

    :param identifier: The identifier of the attribute,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the attribute
    :type name: String
    :param description: The description of this attribute
    :type description: String
    :param regex: The regular expression to use to verify if the value is
                  correct
    :type regex: String
    :param classIndex: The index of the table to use for storing or getting the
                       attribute actual value
    :type classIndex: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/attributes/attributeModal.html')
    try:
      attribute = self.attributeBroker.buildAttributeDefinition(identifier,
                                                              name,
                                                              description,
                                                              regex,
                                                              classIndex,
                                                              action,
                                                              handlerIndex,
                                                              share,
                                                              relation)
    except DeletionException as e:
      return "Error {0}".format(e)

    try:
      if action == 'insert':
        self.attributeBroker.insert(attribute)
      if action == 'update':
        self.attributeBroker.update(attribute)
      if action == 'remove':
        self.attributeBroker.removeByID(identifier)

        # ok everything went right
      return self.returnAjaxOK()
    except ValidationException:
      self.getLogger().info('Attribute is invalid')
      return self.returnAjaxPostError() + self.cleanHTMLCode(template.render(attribute=attribute,
                  cbValues=AttributeDefinition.getTableDefinitions(),
                  cbHandlerValues=AttributeDefinition.getHandlerDefinitions()))
    except OperationException:
      self.getLogger().info(('User tried to delete item {0} which is '
                             + 'still referenced.').format(identifier))
      return 'Error: There are still attributes using this definition.'
    except BrokerException as e:
      self.getLogger().info('An unexpected error occurred: {0}'.format(e))
      return "Error {0}".format(e)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def editAttribute(self, attributeid):
    """
    renders the edit an attribute page

    :param attributeid: The attribute id of the desired displayed attribute
    :type attributeid: Integer

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/attributes/attributeModal.html')
    errorMsg = None
    try:
      attribute = self.attributeBroker.getByID(attributeid)
    except BrokerException as e:
      attribute = None
      self.getLogger().error('An unexpected error occurred: {0}'.format(e))
      errorMsg = 'An unexpected error occurred: {0}'.format(e)
    cbValues = AttributeDefinition.getTableDefinitions()
    cbHandlerValues = AttributeDefinition.getHandlerDefinitions()
    return self.cleanHTMLCode(template.render(attribute=attribute,
                           errorMsg=errorMsg,
                           cbValues=cbValues,
                           cbHandlerValues=cbHandlerValues))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def editObjectAttributes(self, attributeid, operation, attributeObjects=None,
                          remainingObjects=None):
    """
    modifies the relation between a attribute and its attributes

    :param attributeID: The attributeID of the attribute
    :type attributeID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingUsers: The identifiers of the users which the attribute is
                            not attributed to
    :type remainingUsers: Integer array
    :param attributeUsers: The identifiers of the users which the attribute is
                       attributed to
    :type attributeUsers: Integer array

    :returns: generated HTML
    """
    try:
      if operation == 'add':
        if not (remainingObjects is None):
          if isinstance(remainingObjects, types.StringTypes):
            self.attributeBroker.addObjectToAttribute(remainingObjects,
                                                      attributeid)
          else:
            for obj in remainingObjects:
              self.attributeBroker.addObjectToAttribute(obj,
                                                        attributeid,
                                                        False)
            self.attributeBroker.session.commit()
      else:
        if not (attributeObjects is None):
          if isinstance(attributeObjects, types.StringTypes):
            self.attributeBroker.removeObjectFromAttribute(attributeObjects,
                                                           attributeid)
          else:
            for obj in attributeObjects:
              self.attributeBroker.removeObjectFromAttribute(obj,
                                                             attributeid,
                                                             False)
            self.attributeBroker.session.commit()
      return self.returnAjaxOK()
    except BrokerException as e:
      return "Error {0}".format(e)
