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
from ce1sus.db.classes.cstix.indicator.indicator import Indicator
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

            results = self.__prossess_search(needle, operator, definition_id, cache_object)
            self.set_authorized_cache(cache_object.authorized_cache)
            return results
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

  def __check_permission(self, item, cache_object):
    result = self.permission_controller.is_instance_viewable(item, cache_object)
    if result:
      if not isinstance(item, Event):
        parent = item.parent
        if parent:
          return self.__check_permission(parent, cache_object)
    return result

  def __check_permissions(self, event, item, cache_object):
    if self.permission_controller.is_instance_viewable(event, cache_object):
      if item:
        return self.__check_permission(item, cache_object)
    else:
      return False
    
  def __make_search_result(self, instance, cache_object):

    if isinstance(instance, Event):
      if self.__check_permissions(instance, None, cache_object):
        return {'event': instance.to_dict(cache_object)}

    elif isinstance(instance, Object):
      event = instance.event
      if self.__check_permissions(event, instance, cache_object):

        return {'event': event.to_dict(cache_object),
                'object': instance.to_dict(cache_object),
                }
    elif isinstance(instance, Attribute):
      event = instance.value_base.event
      if self.__check_permissions(event, instance, cache_object):

        return {'event': event.to_dict(cache_object),
                'attribute': instance.to_dict(cache_object),
                }
    elif isinstance(instance, Observable):
      event = instance.root
      if self.__check_permissions(event, instance, cache_object):

        return {'event': event.to_dict(cache_object),
                'observable': instance.to_dict(cache_object),
                }
    elif isinstance(instance, Indicator):
      event = instance.root
      if self.__check_permissions(event, instance, cache_object):

        return {'event': event.to_dict(cache_object),
                'indicator': instance.to_dict(cache_object),
                }
    elif isinstance(instance, ObservableComposition):
      event = instance.root
      if self.__check_permissions(event, instance, cache_object):
        return {'event': event.to_dict(cache_object),
                'composed_observable': instance.to_dict(cache_object),
                }
    elif isinstance(instance, Report):
      event = instance.event
      if self.__check_permissions(event, instance, cache_object):

        return {'event': event.to_dict(cache_object),
                'report': instance.to_dict(cache_object),
                }
    elif isinstance(instance, Reference):
      event = instance.report.event
      if self.__check_permissions(event, instance, cache_object):

        return {'event': event.to_dict(cache_object),
                'reference': instance.to_dict(cache_object),
                }
    elif isinstance(instance, STIXHeader):
      event = instance.parent
      if self.__check_permissions(instance, event, cache_object):

        return {'event': event.to_dict(cache_object),
                'stix_header': instance.to_dict(cache_object)}
    elif isinstance(instance, StructuredText):
      parent = instance.parent
      return self.__make_search_result(parent, cache_object)
    else:
      attribute = instance.attribute
      event = attribute.object.event
      if self.__check_permissions(event, attribute, cache_object):

        return {'event': event.to_dict(cache_object),
                'attribute': attribute.to_dict(cache_object)
               }
      
  def __prossess_search(self, needle, operator, definition_id, cache_object):
    """ Note returns only the events which can be viewed """
    results = self.search_controller.search(needle, operator, definition_id)
    result = list()
    cache_object_copy = cache_object.make_copy()
    cache_object_copy.details = True
    cache_object_copy.inflated = False
    for found_value in results:
      result.append(self.__make_search_result(found_value, cache_object_copy))
      
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
