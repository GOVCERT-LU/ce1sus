# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 31, 2014
"""

import json

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.search import SearchController
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.report import Report, Reference
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, RestHandlerException, RestHandlerNotFoundException, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SearchHandler(RestBaseHandler):

  def __init__(self, config):
    super(SearchHandler, self).__init__(config)
    self.search_controller = self.controller_factory(SearchController)

  @rest_method(default=True)
  @methods(allowed=['POST'])
  @require()
  def search(self, **args):
    cache_object = self.get_cache_object(args)
    try:
      json = args.get('json', None)
      if json:
        needle = json.get('value', None)
        if needle and len(needle) > 2:
          operator = json.get('operator', None)
          if operator in ['<', '<=', '==', '>=', '>', 'like']:
            definition_id = json.get('field', None)

            return self.__prossess_search(needle, operator, definition_id, cache_object)

          else:
            raise RestHandlerException(u'Operator "{0}" is unsupported'.format(operator))
        else:
          raise RestHandlerException(u'Search value "{0}" is too short'.format(needle))
      else:
        raise RestHandlerException(u'Post does not hold any body')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __check_permissions(self, event, item):
    return True
    if item:
      return self.is_item_viewable(event, item)
    else:
      return self.is_event_viewable(event)

  def __prossess_search(self, needle, operator, definition_id, cache_object):
    """ Note returns only the events which can be viewed """
    results = self.search_controller.search(needle, operator, definition_id)
    result = list()
    cache_object = cache_object.make_copy()
    cache_object.user.privileged = False
    cache_object.details = False
    cache_object.inflated = False
    for found_value in results:
      if isinstance(found_value, Event):
        if self.__check_permissions(found_value, None):
          # eventpermissions = self.event_controller.get_event_user_permissions(found_value, cache_object.user)
          result.append({'event': found_value.to_dict(cache_object),
                         'object': None,
                         'observable': None,
                         'attribute': None,
                         })
      elif isinstance(found_value, Object):
        event = found_value.event
        if self.__check_permissions(event, found_value):
          # eventpermissions = self.event_controller.get_event_user_permissions(event, cache_object.user)
          result.append({'event': event.to_dict(cache_object),
                         'object': found_value.to_dict(cache_object),
                         'attribute': None,
                         })
      elif isinstance(found_value, Attribute):
        event = found_value.value_base.event
        if self.__check_permissions(event, found_value):

          # eventpermissions = self.event_controller.get_event_user_permissions(event, cache_object.user)
          result.append({'event': event.to_dict(cache_object),
                         'attribute': found_value.to_dict(cache_object),
                         })
      elif isinstance(found_value, Observable):
        event = found_value.root
        if self.__check_permissions(event, found_value):
          # eventpermissions = self.event_controller.get_event_user_permissions(event, cache_object.user)
          result.append({'event': event.to_dict(cache_object),
                         'object': None,
                         'attribute': None,
                         })
      elif isinstance(found_value, ObservableComposition):
        event = found_value.root
        if self.__check_permissions(event, found_value):
          # eventpermissions = self.event_controller.get_event_user_permissions(event, cache_object.user)
          result.append({'event': event.to_dict(cache_object),
                         'object': None,
                         'attribute': None,
                         })
      elif isinstance(found_value, Report):
        event = found_value.event
        if self.__check_permissions(event, found_value):
          # eventpermissions = self.event_controller.get_event_user_permissions(event, cache_object.user)
          result.append({'event': event.to_dict(cache_object),
                         'report': found_value.to_dict(cache_object),
                         'reference': None,
                         })
      elif isinstance(found_value, Reference):
        event = found_value.report.event
        if self.__check_permissions(event, found_value):
          # eventpermissions = self.event_controller.get_event_user_permissions(event, cache_object.user)
          result.append({'event': event.to_dict(cache_object),
                         'report': found_value.report.to_dict(cache_object),
                         'reference': found_value.to_dict(cache_object),
                         })
      elif isinstance(found_value, STIXHeader):
        pass
      elif isinstance(found_value, StructuredText):
        pass
      else:
        attribute = found_value.attribute
        obj = attribute.object
        event = obj.event
        if self.__check_permissions(event, attribute):
          # eventpermissions = self.event_controller.get_event_user_permissions(event, cache_object.user)
          result.append({'event': event.to_dict(cache_object),
                         'observable': obj.observable.to_dict(cache_object),
                         'object': obj.to_dict(cache_object),
                         'attribute': attribute.to_dict(cache_object),
                         })
    return result

  @rest_method(default=False)
  @methods(allowed=['GET'])
  @require()
  def attributes(self, **args):
    cache_object = self.get_cache_object(args)
    try:
      result = list()
      # Add any
      result.append({'identifier': None, 'name': 'Any'})
      # Generic container fields
      result.append({'identifier': 'uuid', 'name': 'uuid'})
      result.append({'identifier': 'title', 'name': 'title'})
      result.append({'identifier': 'description', 'name': 'description'})

      attributes = self.search_controller.get_all_attributes()
      for attribtue in attributes:
        attr_dict = attribtue.to_dict(cache_object)
        result.append(attr_dict)

      references = self.search_controller.get_all_references()
      for reference in references:
        ref_dict = reference.to_dict(cache_object)
        result.append(ref_dict)
      # Report fields
      return result
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
