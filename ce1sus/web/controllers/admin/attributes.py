# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from c17Works.web.controllers.base import BaseController
import cherrypy
from ce1sus.brokers.definitionbroker import AttributeDefinitionBroker, \
 AttributeDefinition
from ce1sus.web.helpers.protection import require, privileged
from c17Works.db.broker import OperationException, BrokerException, \
  ValidationException, NothingFoundException
from c17Works.helpers.converters import ObjectConverter
import types as types
import c17Works.helpers.string as string

class AttributeController(BaseController):
  """Controller handling all the requests for attributes"""

  def __init__(self):
    BaseController.__init__(self)
    self.attributeBroker = self.brokerFactory(AttributeDefinitionBroker)

  @require(privileged())
  @cherrypy.expose
  def index(self):
    """
    renders the attribute page

    :returns: generated HTML
    """

    template = self.getTemplate('/admin/attributes/attributeBase.html')
    return template.render()

  @cherrypy.expose
  def leftContent(self):
    """
    renders the left content of the attribute index page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/attributes/attributeLeft.html')

    attributes = self.attributeBroker.getAll()
    return template.render(attributes=attributes)

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
    return template.render(attributeDetails=attribute,
                           remainingObjects=remainingObjects,
                           attributeObjects=attributeObjects,
                           cbHandlerValues=AttributeDefinition.getHandlerDefinitions(),
                           cbValues=cbValues)


  @cherrypy.expose
  def addAttribute(self):
    """
    renders the add an attribute page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/attributes/attributeModal.html')
    cbValues = AttributeDefinition.getTableDefinitions()
    cbHandlerValues = AttributeDefinition.getHandlerDefinitions()
    return template.render(attribute=None,
                           errorMsg=None,
                           cbValues=cbValues,
                           cbHandlerValues=cbHandlerValues)


  @require(privileged())
  @cherrypy.expose
  def modifyAttribute(self, identifier=None, name=None, description='',
                      regex='^.*$', classIndex=0, action='insert', handlerIndex=0):
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


    errorMsg = None
    attribute = AttributeDefinition()
    if not action == 'insert':
      attribute = self.attributeBroker.getByID(identifier)
      if attribute.deletable == 0:
        raise BrokerException('Attribute cannot be edited or deleted')
    if not action == 'remove':
      attribute.name = name
      attribute.description = description
      ObjectConverter.setInteger(attribute, 'classIndex', classIndex)
      ObjectConverter.setInteger(attribute, 'handlerIndex', handlerIndex)

      if string.isNotNull(regex):
        regex = '^.*$'
      attribute.regex = regex

      try:
        if action == 'insert':
          attribute.deletable = 1
          self.attributeBroker.insert(attribute)
        if action == 'update':
          self.attributeBroker.update(attribute)
        action = None
      except ValidationException:
        self.getLogger().info('Attribute is invalid')
      except BrokerException as e:
        self.getLogger().info('An unexpected error occurred: {0}'.format(e))
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
    else:
      try:
        self.attributeBroker.removeByID(attribute.identifier)
        action = None
      except OperationException:
        errorMsg = ('Cannot delete this attribute.' +
                    ' The attribute is still referenced.')


    if action == None:
      # ok everything went right
      return self.returnAjaxOK()
    else:
      return template.render(attribute=attribute,
                             errorMsg=errorMsg,
                             cbValues=AttributeDefinition.getTableDefinitions(),
                             cbHandlerValues=AttributeDefinition.getHandlerDefinitions())

  @require(privileged())
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
    return template.render(attribute=attribute,
                           errorMsg=errorMsg,
                           cbValues=cbValues,
                           cbHandlerValues=cbHandlerValues)

  @cherrypy.expose
  def editObjectAttributes(self, attributeid, operation, attributeObjects=None,
                          remainingObjects=None):
    """
    modifies the relation between a attribute and its attributes

    :param attributeID: The attributeID of the attribute
    :type attributeID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingUsers: The identifiers of the users which the attribute is not
                            attributed to
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
      return e
