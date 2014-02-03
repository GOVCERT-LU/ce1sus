# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy
from ce1sus.rest.restbase import RestControllerBase
from ce1sus.brokers.event.eventbroker import EventBroker
from dagr.db.broker import BrokerException, NothingFoundException
from dagr.helpers.datumzait import datumzait
import json


class RestSearchController(RestControllerBase):

  MAX_LIMIT = 20
  PARAMETER_MAPPER = {'attributes': 'view_attributes',
                      'events': 'viewEvents'}

  def __init__(self):
    RestControllerBase.__init__(self)
    self.event_broker = self.broker_factory(EventBroker)

  def __get_limit(self, options):
    limit = options.get('limit', RestSearchController.MAX_LIMIT / 2)

    # limit has to be between 0 and maximum value
    if limit < 0 or limit > RestSearchController.MAX_LIMIT:
      self.raise_error('InvalidArgument',
                      'The limit value has to be between 0 and 20')
    return limit

  def get_parent_object(self, event, obj, seen_events):
    if not obj.parent_object_id:
      return None

    org_parent_obj = self.object_broker.get_by_id(obj.parent_object_id)
    if org_parent_obj.bit_value.is_validated and org_parent_obj.bit_value.is_shareable:

      parent_object = seen_events[event.identifier][1].get(
                                                      org_parent_obj.identifier,
                                                      None
                                                        )
      if not parent_object:
        # memorize parent_object
        parent_object = org_parent_obj.to_rest_object(False)
        seen_events[event.identifier][1][org_parent_obj.identifier] = parent_object
        if org_parent_obj.parent_object_id:
          parent_parent_object = seen_events[event.identifier][1].get(
                                          org_parent_obj.parent_object.identifier,
                                          None
                                                                  )
          if not parent_parent_object:
            parent_parent_object = self.get_parent_object(event,
                                                      org_parent_obj,
                                                      seen_events)
            if parent_parent_object:
              rest_parent = parent_parent_object.to_rest_object(False)
              index = org_parent_obj.parent_object.identifier
              seen_events[event.identifier][1][index] = rest_parent
              parent_object.parent = rest_parent
            else:
              return None
          else:
            parent_object.parent = rest_parent

        else:
          rest_event = seen_events[event.identifier][0]
          rest_event.objects.append(parent_object)

      return parent_object
    else:
      return None

  def __check_if_belongs(self, identifier, array):
    if array:
      return identifier in array
    else:
      return True

  def view_attributes(self, uuid, api_key, **options):
    try:
      with_definition = options.get('fulldefinitions', False)
      # TODO use these!
      start_date = options.get('startdate', None)
      end_date = options.get('enddate', datumzait.utcnow())
      offset = options.get('page', 0)
      limit = self.__get_limit(options)

      # object type to look foor if specified
      perform_search = True
      object_needle = options.get('objecttype', None)
      object_definition = None
      if object_needle:
        object_definition = self.object_definition_broker.get_defintion_by_name(
                                                                  object_needle
                                                                   )

      # collect informations about the attribute to look for
      if perform_search:
        # object Attribues to look for
        needles = options.get('objectattributes', list())
        complete_needles = dict()
        for needle in needles:
            for key, value in needle.iteritems():
              definition = self.attribute_definition_broker.get_defintion_by_name(
                                                                          key.strip()
                                                                            )
              if definition.class_index != 0:
                complete_needles[value] = definition
        if not complete_needles:
          perform_search = False

      # Collect informations about the return values
      if perform_search:
        requested_attributes = list()
        for item in options.get('attributes', list()):
          definition = self.attribute_definition_broker.get_defintion_by_name(item.strip())
          requested_attributes.append(definition.identifier)
          # Note if no requested attribues are defined return all for the
          # object having the needle

      if perform_search:

        # find Matching attribtues
        matching_attributes = list()
        for definition, needle in complete_needles.iteritems():
          found_values = self.attribute_broker.lookforAttributeValue(needle,
                                                                 definition,
                                                                 '==')
          matching_attributes = matching_attributes + found_values

        # cache
        seen_items = dict()

        for item in matching_attributes:
          attribute = item.attribute
          # get the event
          event = attribute.object.event
          if not event:
            event = attribute.object.parent_event
          # check if attribute is sharable and validated
          if (attribute.bit_value.is_validated and attribute.bit_value.is_shareable) or self.is_event_owner(event,
                                                             self.getUserByAPIKey(api_key)):
            # check it is one of the requested attributes
            obj = attribute.object
            # check if the object is desired
            if (not object_definition or obj.def_object_id == object_definition.identifier):
              # check if object is sharable and validated
              if (obj.bit_value.is_validated and obj.bit_value.is_shareable) or self.is_event_owner(event,
                                                             self.getUserByAPIKey(api_key)):
                if requested_attributes:
                  # append only the requested attributes
                  neededAttributes = list()
                  for item in obj.attributes:
                    if item.def_attribute_id in requested_attributes:
                      neededAttributes.append(item)
                else:
                  # append all attributes
                  neededAttributes = obj.attributes

                try:
                  # check if the event can be accessed
                  self.checkIfViewable(event, self.get_user(api_key), False)

                  # get rest from cache
                  rest_event = seen_items.get(event.identifier, None)
                  if not rest_event:
                    # if not cached put it there
                    rest_event = event.to_rest_object(self.is_event_owner(event,
                                                             self.getUserByAPIKey(api_key)), False)
                    seen_items[event.identifier] = (rest_event, dict())
                  else:
                    # get it from cache
                    rest_event = rest_event[0]

                  # get obj from cache
                  rest_object = seen_items[event.identifier][1].get(obj.identifier,
                                                                  None)
                  if not rest_object:
                    rest_object = obj.to_rest_object(self.is_event_owner(event,
                                                             self.getUserByAPIKey(api_key)), False)
                    if obj.parent_object_id is None:
                      rest_event.objects.append(rest_object)
                    else:
                      parent_object = self.get_parent_object(event, obj, seen_items)
                      if parent_object:
                        parent_object.children.append(rest_object)

                    # append required attributes to the object
                    for item in neededAttributes:
                      rest_object.attributes.append(item.to_rest_object())

                    seen_items[event.identifier][1][obj.identifier] = rest_object

                except cherrypy.HTTPError:
                  # Do nothing if the user cant see the event
                  pass

              # make list of results

        result = list()
        if perform_search:

          for event, objs in seen_items.itervalues():
            del objs
            dictionary = dict(event.to_dict(full=True,
                               with_definition=with_definition).items()
                   )
            obj = json.dumps(dictionary)
            result.append(obj)

        result_dict = {'Results': result}
        return self._return_message(result_dict)

    except NothingFoundException as error:
      return self.raise_error('NothingFoundException', error)
    except BrokerException as error:
      return self.raise_error('BrokerException', error)

  def viewEvents(self, uuid, api_key, **options):
    try:
      # TODO use these!
      start_date = options.get('startdate', None)
      end_date = options.get('enddate', datumzait.utcnow())
      offset = options.get('page', 0)
      limit = self.__get_limit(options)

      # serach on objecttype
      object_type = options.get('objecttype', None)
      # with the following attribtes type + value
      object_attribtues = options.get('objectattributes', list())

      if object_type or object_attribtues:
        # process needles
        values_to_look_for = dict()

        for item in object_attribtues:
          for key, value in item.iteritems():
            definition = self.attribute_definition_broker.get_defintion_by_name(key)
            # TODO: search inside textfield
            if definition.class_index != 0:
              values_to_look_for[value] = definition

        matching_attributes = list()
        # find results
        for value, key in values_to_look_for.iteritems():
          foundValues = self.attribute_broker.lookforAttributeValue(key,
                                                                 value,
                                                                 '==')
          matching_attributes = matching_attributes + foundValues

        result = list()
        for needle in matching_attributes:
          try:
            event = needle.attribute.object.event
            if not event:
              event = needle.attribute.object.parent_event
            self.checkIfViewable(event, self.get_user(api_key), False)
            result.append(event.uuid)
          except cherrypy.HTTPError:
            pass
        result_dict = {'Results': result}
        return self._return_message(result_dict)
      else:
        self.raise_error('InvalidArgument',
                         'At least one argument has to be specified')

    except NothingFoundException as error:
      return self.raise_error('NothingFoundException', error)
    except BrokerException as error:
      return self.raise_error('BrokerException', error)

  def get_function_name(self, parameter, action):
    if action == 'GET':
      return RestSearchController.PARAMETER_MAPPER.get(parameter, None)
    return None
