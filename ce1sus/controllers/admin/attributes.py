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
from ce1sus.web.helpers.protection import require, privileged, require_referer
from dagr.db.broker import BrokerException, \
                          ValidationException, NothingFoundException, \
                          DeletionException, IntegrityException
from ce1sus.brokers.definition.handlerdefinitionbroker import \
                                                        AttributeHandlerBroker
import types as types


class AttributeController(Ce1susBaseController):
  """Controller handling all the requests for attributes"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.attribute_broker = self.broker_factory(AttributeDefinitionBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the attribute page

    :returns: generated HTML
    """

    template = self._get_template('/admin/attributes/attributeBase.html')
    return self.clean_html_code(template.render())

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def left_content(self):
    """
    renders the left content of the attribute index page

    :returns: generated HTML
    """
    template = self._get_template('/admin/attributes/attributeLeft.html')

    attributes = self.attribute_broker.get_all()
    return self.clean_html_code(template.render(attributes=attributes))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def right_content(self, attributeid=0, attribute=None):
    """
    renders the right content of the attribute index page

    :param attributeid: The attribute id of the desired displayed attribute
    :type attributeid: Integer
    :param attribute: Similar to the previous attribute but prevents
                      additional loadings
    :type attribute: AttributeDefinition

    :returns: generated HTML
    """
    template = self._get_template('/admin/attributes/attributeRight.html')

    if attribute is None:
      try:
        attribute = self.attribute_broker.get_by_id(attributeid)
      except NothingFoundException:
        attribute = None

    else:
      attribute = attribute

    remainingObjects = None
    attributeObjects = None
    if not attribute is None:
      remainingObjects = self.attribute_broker.get_objects_by_attribute(
                                                attribute.identifier, False)
      attributeObjects = attribute.objects

    cbValues = AttributeDefinition.get_table_definitions()
    return self.clean_html_code(template.render(attributeDetails=attribute,
                           remainingObjects=remainingObjects,
                           attributeObjects=attributeObjects,
                  cbHandlerValues=self.handler_broker.get_handler_definitions(),
                           cbValues=cbValues))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def add_attribute(self):
    """
    renders the add an attribute page

    :returns: generated HTML
    """
    template = self._get_template('/admin/attributes/attributeModal.html')
    cbValues = AttributeDefinition.get_table_definitions()
    cbHandlerValues = self.handler_broker.get_handler_definitions()
    return self.clean_html_code(template.render(attribute=None,
                           errorMsg=None,
                           cbValues=cbValues,
                           cbHandlerValues=cbHandlerValues))

  # pylint: disable=R0913
  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def modify_attribute(self, identifier=None, name=None, description='',
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
    template = self._get_template('/admin/attributes/attributeModal.html')
    try:
      attribute = self.attribute_broker.build_attribute_definition(identifier,
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
        self.attribute_broker.insert(attribute)
      if action == 'update':
        self.attribute_broker.update(attribute)
      if action == 'remove':
        self.attribute_broker.removeByID(identifier)

        # ok everything went right
      return self._return_ajax_ok()
    except ValidationException:
      self._get_logger().info('Attribute is invalid')
      return self._return_ajax_post_error() + self.clean_html_code(
                                                      template.render(
                                                      attribute=attribute,
                  cbValues=AttributeDefinition.get_table_definitions(),
                  cbHandlerValues=self.handler_broker.get_handler_definitions()))
    except IntegrityException:
      self._get_logger().info(('User tried to delete item {0} which is '
                             + 'still referenced.').format(identifier))
      return 'Error: There are still attributes using this definition.'
    except BrokerException as e:
      self._get_logger().info('An unexpected error occurred: {0}'.format(e))
      return "Error {0}".format(e)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def editAttribute(self, attributeid):
    """
    renders the edit an attribute page

    :param attributeid: The attribute id of the desired displayed attribute
    :type attributeid: Integer

    :returns: generated HTML
    """
    template = self._get_template('/admin/attributes/attributeModal.html')
    errorMsg = None
    try:
      attribute = self.attribute_broker.get_by_id(attributeid)
    except BrokerException as e:
      attribute = None
      self._get_logger().error('An unexpected error occurred: {0}'.format(e))
      errorMsg = 'An unexpected error occurred: {0}'.format(e)
    cbValues = AttributeDefinition.get_table_definitions()
    cbHandlerValues = self.handler_broker.get_handler_definitions()
    return self.clean_html_code(template.render(attribute=attribute,
                           errorMsg=errorMsg,
                           cbValues=cbValues,
                           cbHandlerValues=cbHandlerValues))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_object_attributes(self, attributeid, operation, attributeObjects=None,
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
            self.attribute_broker.add_object_to_attribute(remainingObjects,
                                                      attributeid)
          else:
            for obj in remainingObjects:
              self.attribute_broker.add_object_to_attribute(obj,
                                                        attributeid,
                                                        False)
            self.attribute_broker.session.commit()
      else:
        if not (attributeObjects is None):
          if isinstance(attributeObjects, types.StringTypes):
            self.attribute_broker.remove_object_from_attribute(attributeObjects,
                                                           attributeid)
          else:
            for obj in attributeObjects:
              self.attribute_broker.remove_object_from_attribute(obj,
                                                             attributeid,
                                                             False)
            self.attribute_broker.session.commit()
      return self._return_ajax_ok()
    except BrokerException as e:
      return "Error {0}".format(e)
