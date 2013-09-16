# -*- coding: utf-8 -*-

"""
module handing the object pages

Created: Aug 26, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.web.controllers.base import BaseController
import cherrypy
from ce1sus.brokers.definitionbroker import ObjectDefinitionBroker
from ce1sus.web.helpers.protection import require, privileged, requireReferer
from dagr.db.broker import OperationException, BrokerException, \
  ValidationException, NothingFoundException
import types

class ObjectController(BaseController):
  """Controller handling all the requests for objects"""

  def __init__(self):
    BaseController.__init__(self)
    self.objectBroker = self.brokerFactory(ObjectDefinitionBroker)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the object page

    :returns: generated HTML
    """

    template = self.getTemplate('/admin/objects/objectBase.html')
    return template.render()

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def leftContent(self):
    """
    renders the left content of the object index page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/objects/objectLeft.html')
    objects = self.objectBroker.getAll()
    return template.render(objects=objects)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def rightContent(self, objectid=0, obj=None):
    """
    renders the right content of the object index page

    :param objectid: The object id of the desired displayed object
    :type objectid: Integer
    :param obj: Similar to the previous attribute but prevents
                      additional loadings
    :type obj: ObjectDefinition

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/objects/objectRight.html')
    if obj is None:
      try:
        obj = self.objectBroker.getByID(objectid)
      except NothingFoundException:
        obj = None

    else:
      obj = obj
    remainingAttributes = None
    attributes = None
    if not obj is None:
      remainingAttributes = self.objectBroker.getAttributesByObject(
                                                obj.identifier, False)
      attributes = obj.attributes
    return template.render(objectDetails=obj,
                           remainingAttributes=remainingAttributes,
                           objectAttributes=attributes)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def addObject(self):
    """
    renders the add an object page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/objects/objectModal.html')
    return template.render(object=None, errorMsg=None)


  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def modifyObject(self, identifier=None, name=None,
                  description=None, action='insert'):
    """
    modifies or inserts a object with the data of the post

    :param identifier: The identifier of the object,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the object
    :type name: String
    :param description: The description of this object
    :type description: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/objects/objectModal.html')
    obj = self.objectBroker.buildObjectDefinition(identifier,
                                                  name,
                                                  description,
                                                  action)
    try:
      if action == 'insert':
        self.objectBroker.insert(obj)
      if action == 'update':
        self.objectBroker.update(obj)
      if action == 'remove':
        self.objectBroker.removeByID(obj.identifier)
      return self.returnAjaxOK()
    except OperationException as e:
      self.getLogger().info('OperationError occurred: {0}'.format(e))
      return 'Cannot delete this object. The object is still referenced.'
    except ValidationException:
      self.getLogger().info('Object is invalid')
      return self.returnAjaxPostError() + template.render(object=obj)
    except BrokerException as e:
      self.getLogger().info('An unexpected error occurred: {0}'.format(e))
      return e

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def editObject(self, objectid):
    """
    renders the edit an object page

    :param objectid: The object id of the desired displayed object
    :type objectid: Integer

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/objects/objectModal.html')
    errorMsg = None
    try:
      obj = self.objectBroker.getByID(objectid)
    except BrokerException as e:
      obj = None
      self.getLogger().error('An unexpected error occurred: {0}'.format(e))
      errorMsg = 'An unexpected error occurred: {0}'.format(e)
    return template.render(objectDetails=obj, errorMsg=errorMsg)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def editObjectAttributes(self, objectid, operation,
                     objectAttributes=None, remainingAttributes=None):
    """
    modifies the relation between a object and its attributes

    :param objectID: The objectID of the object
    :type objectID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingUsers: The identifiers of the users which the object is not
                            attributed to
    :type remainingUsers: Integer array
    :param objectUsers: The identifiers of the users which the object is
                       attributed to
    :type objectUsers: Integer array

    :returns: generated HTML
    """
    try:
      if operation == 'add':
        if not (remainingAttributes is None):
          if isinstance(remainingAttributes, types.StringTypes):
            self.objectBroker.addAttributeToObject(remainingAttributes,
                                                   objectid)
          else:
            for attribute in remainingAttributes:
              self.objectBroker.addAttributeToObject(attribute, objectid, False)
            self.objectBroker.doCommit()
      else:
        #Note objectAttributes may be a string or an array!!!
        if not (objectAttributes is None):
          if isinstance(objectAttributes, types.StringTypes):
            self.objectBroker.removeAttributeFromObject(objectAttributes,
                                                        objectid)
          else:
            for attribute in objectAttributes:
              self.objectBroker.removeAttributeFromObject(attribute, objectid)
            self.objectBroker.doCommit()
      return self.returnAjaxOK()
    except BrokerException as e:
      return e
