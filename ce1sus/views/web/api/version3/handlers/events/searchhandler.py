# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 31, 2014
"""

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.search import SearchController
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.event import Event
from ce1sus.db.classes.object import Object
from ce1sus.db.classes.observables import Observable, ObservableComposition
from ce1sus.db.classes.report import Report, Reference
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, RestHandlerException, RestHandlerNotFoundException, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SearchHandler(RestBaseHandler):

    def __init__(self, config):
        RestBaseHandler.__init__(self, config)
        self.search_controller = self.controller_factory(SearchController)

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

    def __check_permissions(self, event, item):
        if item:
            return self.is_item_viewable(event, item)
        else:
            return self.is_event_viewable(event)

    def __prossess_search(self, needle, operator, definition_id):
        """ Note returns only the events which can be viewed """
        results = self.search_controller.search(needle, operator, definition_id)
        result = list()
        for found_value in results:
            user = self.get_user()
            # TODO: include user!!!!! IMPORTANT if the event is extracted by mistake
            if isinstance(found_value, Event):
                if self.__check_permissions(found_value, None):
                    eventpermissions = self.event_controller.get_event_user_permissions(found_value, user)
                    result.append({'event': found_value.to_dict(False, False, eventpermissions, user),
                                   'object': None,
                                   'observable': None,
                                   'attribute': None,
                                   })
            elif isinstance(found_value, Object):
                event = found_value.event
                if self.__check_permissions(event, found_value):
                    eventpermissions = self.event_controller.get_event_user_permissions(event, user)
                    result.append({'event': event.to_dict(False, False, eventpermissions, user),
                                   'object': found_value.to_dict(False, False, eventpermissions, user),
                                   'observable': found_value.observable.to_dict(False, False, eventpermissions, user),
                                   'attribute': None,
                                   })
            elif isinstance(found_value, Attribute):
                obj = found_value.object
                event = obj.event
                if self.__check_permissions(event, found_value):
                    eventpermissions = self.event_controller.get_event_user_permissions(event, user)
                    result.append({'event': event.to_dict(False, False, eventpermissions, user),
                                   'object': obj.to_dict(False, False, eventpermissions, user),
                                   'observable': obj.observable.to_dict(False, False, eventpermissions, user),
                                   'attribute': found_value.to_dict(False, False, eventpermissions, user),
                                   })
            elif isinstance(found_value, Observable):
                event = found_value.parent
                if self.__check_permissions(event, found_value):
                    eventpermissions = self.event_controller.get_event_user_permissions(event, user)
                    result.append({'event': event.to_dict(False, False, eventpermissions, user),
                                   'object': None,
                                   'observable': found_value.to_dict(False, False, eventpermissions, user),
                                   'attribute': None,
                                   })
            elif isinstance(found_value, ObservableComposition):
                event = found_value.parent.parent
                if self.__check_permissions(event, found_value):
                    eventpermissions = self.event_controller.get_event_user_permissions(event, user)
                    result.append({'event': event.to_dict(False, False, eventpermissions, user),
                                   'object': None,
                                   'observable': found_value.to_dict(False, False, eventpermissions, user),
                                   'attribute': None,
                                   })
            elif isinstance(found_value, Report):
                event = found_value.event
                if self.__check_permissions(event, found_value):
                    eventpermissions = self.event_controller.get_event_user_permissions(event, user)
                    result.append({'event': event.to_dict(False, False, eventpermissions, user),
                                   'report': found_value.to_dict(False, False, eventpermissions, user),
                                   'reference': None,
                                   })
            elif isinstance(found_value, Reference):
                event = found_value.report.event
                if self.__check_permissions(event, found_value):
                    eventpermissions = self.event_controller.get_event_user_permissions(event, user)
                    result.append({'event': event.to_dict(False, False, eventpermissions, user),
                                   'report': found_value.report.to_dict(False, False, eventpermissions, user),
                                   'reference': found_value.to_dict(False, False, eventpermissions, user),
                                   })
            else:
                attribute = found_value.attribute
                obj = attribute.object
                event = obj.event
                if self.__check_permissions(event, attribute):
                    eventpermissions = self.event_controller.get_event_user_permissions(event, user)
                    result.append({'event': event.to_dict(False, False, eventpermissions, user),
                                   'observable': obj.observable.to_dict(False, False, eventpermissions, user),
                                   'object': obj.to_dict(False, False, eventpermissions, user),
                                   'attribute': attribute.to_dict(False, False, eventpermissions, user),
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
            # Generic container fields
            result.append({'identifier': 'uuid', 'name': 'uuid'})
            result.append({'identifier': 'title', 'name': 'title'})
            result.append({'identifier': 'description', 'name': 'description'})

            attributes = self.search_controller.get_all_attributes()
            for attribtue in attributes:
                attr_dict = attribtue.to_dict(False, False)
                attr_dict['identifier'] = 'attribute:{0}'.format(attr_dict['identifier'])
                result.append(attr_dict)

            references = self.search_controller.get_all_references()
            for reference in references:
                ref_dict = reference.to_dict(False, False)
                ref_dict['identifier'] = 'reference:{0}'.format(ref_dict['identifier'])
                result.append(ref_dict)
            # Report fields
            return result
        except ControllerNothingFoundException as error:
            raise RestHandlerNotFoundException(error)
        except ControllerException as error:
            raise RestHandlerException(error)
