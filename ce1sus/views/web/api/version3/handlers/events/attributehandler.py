# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 29, 2014
"""

from ce1sus.controllers.base import ControllerNothingFoundException, \
  ControllerException
from ce1sus.controllers.events.attributecontroller import AttributeController
from ce1sus.db.classes.common import ValueException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, \
  RestHandlerNotFoundException, RestHandlerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributesHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.attribute_controller = AttributeController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'DELETE'])
  def attribute(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      json = args.get('json')
      if len(path) < 1:
        raise RestHandlerException(u'Invalid request - Attribute needs to be called with an ID')
      elif len(path) == 1:
        requested_object = self.parse_path(path, method)
        attribute_id = requested_object.get('event_id')
        attribute = self.attribute_controller.get_attribute_by_id(attribute_id)
        event = attribute.object.event
        user = self.get_user()
        if method == 'GET':
          self.check_if_event_is_viewable(event)
          return attribute.to_dict(details, inflated)
        elif method == 'PUT':
          try:
            self.check_if_event_is_modifiable(event)
            attribute.populate(json)
            self.attribute_controller.update_attribute(attribute, user, True)
            return attribute.to_dict(details, inflated)
          except ValueException as error:
            raise RestHandlerException(error)
        elif method == 'DELETE':
          self.check_if_event_is_deletable(event)
          self.attribute_controller.remove_attribute(attribute, user, True)
          return 'Deleted object'
      else:
        raise RestHandlerException(u'Invalid request - Attribute does not support sub calls')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
