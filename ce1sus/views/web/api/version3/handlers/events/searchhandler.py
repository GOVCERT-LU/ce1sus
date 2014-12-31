# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 31, 2014
"""

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.search import SearchController
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, RestHandlerException, RestHandlerNotFoundException, require, valid_uuid
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.event import Event
from ce1sus.db.classes.object import Object
from ce1sus.db.classes.observables import Observable, ObservableComposition

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SearchHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.search_controller = SearchController(config)

  @rest_method(default=True)
  @methods(allowed=['POST'])
  @require()
  def search(self, **args):
    try:
      json = args.get('json', None)
      if json:
        needle = json.get('value', None)
        if needle and len(needle) > 2:
          operator = json.get('operator', None)
          if operator in ['<', '<=', '==', '>=', '>', 'like']:
            definition_id = json.get('field', None)
            if definition_id is not None:
              if not (valid_uuid(definition_id) or definition_id == 'uuid'):
                raise RestHandlerException(u'Definition uuid "{0}" is valid'.format(definition_id))

            return self.__prossess_search(needle, operator, definition_id)

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

  def __prossess_search(self, needle, operator, definition_id):
    results = self.search_controller.search(needle, operator, definition_id)
    result = list()
    for found_value in results:
      # TODO find a unified way to do this
      # TODO: include user!!!!! IMPORTANT
      if isinstance(found_value, Event):
        result.append({'event': found_value.to_dict(False, False),
                       'object': None,
                       'observable': None,
                       'attribute': None,
                       })
      elif isinstance(found_value, Object):
        event = found_value.event
        result.append({'event': event.to_dict(False, False),
                       'object': found_value.to_dict(False, False),
                       'observable': found_value.observable.to_dict(False, False),
                       'attribute': None,
                       })
      elif isinstance(found_value, Attribute):
        obj = found_value.object
        event = obj.event
        result.append({'event': event.to_dict(False, False),
                       'object': obj.to_dict(False, False),
                       'observable': obj.observable.to_dict(False, False),
                       'attribute': found_value.to_dict(False, False),
                       })
      elif isinstance(found_value, Observable):
        event = found_value.event
        result.append({'event': event.to_dict(False, False),
                       'object': None,
                       'observable': found_value.to_dict(False, False),
                       'attribute': None,
                       })
      elif isinstance(found_value, ObservableComposition):
        event = found_value.parent.event
        result.append({'event': event.to_dict(False, False),
                       'object': None,
                       'observable': found_value.to_dict(False, False),
                       'attribute': None,
                       })
      else:
        attribute = found_value.attribute
        obj = attribute.object
        event = obj.event
        result.append({'event': event.to_dict(False, False),
                       'observable': obj.observable.to_dict(False, False),
                       'object': obj.to_dict(False, False),
                       'attribute': attribute.to_dict(False, False),
                       })
    return result

  @rest_method(default=False)
  @methods(allowed=['GET'])
  @require()
  def attributes(self, **args):
    try:
      result = list()
      # Add any
      result.append({'identifier': None, 'name': 'Any'})
      result.append({'identifier': 'uuid', 'name': 'uuid'})
      attributes = self.search_controller.get_all_attributes()
      for attribtue in attributes:
        result.append(attribtue.to_dict(False, False))
      return result
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
