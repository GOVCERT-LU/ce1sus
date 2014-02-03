# -*- coding: utf-8 -*-

"""
module handing the object pages

Created: Aug 26, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.brokers.definition.objectdefinitionbroker import \
                                                      ObjectDefinitionBroker
from ce1sus.web.helpers.protection import require, privileged, require_referer
from dagr.db.broker import IntegrityException, BrokerException, \
  ValidationException, NothingFoundException
import types


class ObjectController(Ce1susBaseController):
  """Controller handling all the requests for objects"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.object_broker = self.broker_factory(ObjectDefinitionBroker)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the object page

    :returns: generated HTML
    """

    template = self._get_template('/admin/objects/objectBase.html')

    return self.clean_html_code(template.render())

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def left_content(self):
    """
    renders the left content of the object index page

    :returns: generated HTML
    """
    template = self._get_template('/admin/objects/objectLeft.html')
    objects = self.object_broker.get_all()
    return self.clean_html_code(template.render(objects=objects))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def right_content(self, objectid=0, obj=None):
    """
    renders the right content of the object index page

    :param objectid: The object id of the desired displayed object
    :type objectid: Integer
    :param obj: Similar to the previous attribute but prevents
                      additional loadings
    :type obj: ObjectDefinition

    :returns: generated HTML
    """
    template = self._get_template('/admin/objects/objectRight.html')
    if obj is None:
      try:
        obj = self.object_broker.get_by_id(objectid)
      except NothingFoundException:
        obj = None

    else:
      obj = obj
    remaining_attributes = None
    attributes = None
    if not obj is None:
      remaining_attributes = self.object_broker.get_attributes_by_object(
                                                obj.identifier, False)
      attributes = obj.attributes
    return self.clean_html_code(template.render(objectDetails=obj,
                           remaining_attributes=remaining_attributes,
                           objectAttributes=attributes))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def add_object(self):
    """
    renders the add an object page

    :returns: generated HTML
    """
    template = self._get_template('/admin/objects/objectModal.html')
    return self.clean_html_code(template.render(object=None, errorMsg=None))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def modify_object(self, identifier=None, name=None,
                  description=None, action='insert', share=None):
    """
    modifies or inserts a object with the data of the post

    :param identifier: The identifier of the object,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the object
    :type name: String
    :param description: The description of this object
    :type description: String
    :param action: action which is taken (i.error. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    template = self._get_template('/admin/objects/objectModal.html')
    obj = self.object_broker.build_object_definition(identifier,
                                                  name,
                                                  description,
                                                  action,
                                                  share)
    try:
      if action == 'insert':
        self.object_broker.insert(obj)
      if action == 'update':
        self.object_broker.update(obj)
      if action == 'remove':
        self.object_broker.remove_by_id(obj.identifier)
      return self._return_ajax_ok()
    except IntegrityException as error:
      self._get_logger().info('OperationError occurred: {0}'.format(error))
      return 'Cannot delete this object. The object is still referenced.'
    except ValidationException:
      self._get_logger().info('Object is invalid')
      return self._return_ajax_post_error() + self.clean_html_code(
                                                        template.render(
                                                                  object=obj))
    except BrokerException as error:
      self._get_logger().info('An unexpected error occurred: {0}'.format(error))
      return "Error {0}".format(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_object(self, objectid):
    """
    renders the edit an object page

    :param objectid: The object id of the desired displayed object
    :type objectid: Integer

    :returns: generated HTML
    """
    template = self._get_template('/admin/objects/objectModal.html')
    error_msg = None
    try:
      obj = self.object_broker.get_by_id(objectid)
    except BrokerException as e:
      obj = None
      self._get_logger().error('An unexpected error occurred: {0}'.format(e))
      error_msg = 'An unexpected error occurred: {0}'.format(e)
    return self.clean_html_code(template.render(object=obj, error_msg=error_msg))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_object_attributes(self, objectid, operation,
                     object_attributes=None, remaining_attributes=None):
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
        if not (remaining_attributes is None):
          if isinstance(remaining_attributes, types.StringTypes):
            self.object_broker.add_attribute_to_object(remaining_attributes,
                                                   objectid)
          else:
            for attribute in remaining_attributes:
              self.object_broker.add_attribute_to_object(attribute,
                                                     objectid,
                                                     False)
            self.object_broker.do_commit()
      else:
        #Note object_attributes may be a string or an array!!!
        if not (object_attributes is None):
          if isinstance(object_attributes, types.StringTypes):
            self.object_broker.remove_attribute_from_object(object_attributes,
                                                        objectid)
          else:
            for attribute in object_attributes:
              self.object_broker.remove_attribute_from_object(attribute, objectid)
            self.object_broker.do_commit()
      return self._return_ajax_ok()
    except BrokerException as error:
      return "Error {0}".format(error)
