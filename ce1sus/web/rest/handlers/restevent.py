# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.rest.restbase import RestControllerBase
from ce1sus.brokers.event.eventbroker import EventBroker
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.brokers.staticbroker import TLPLevel, Risk, Analysis, Status
from ce1sus.api.restclasses import RestEvent


class RestEventController(RestControllerBase):

  PARAMETER_MAPPER = {'metadata': 'view_metadata'}

  def __init__(self):
    RestControllerBase.__init__(self)
    self.event_broker = self.broker_factory(EventBroker)

  def view_metadata(self, uuid, api_key, **options):
    try:
      event = self.event_broker.get_by_uuid(uuid)
      self.checkIfViewable(event, self.get_user(api_key), False)
      obj = self._object_to_json(event,
                               self.is_event_owner(event, self.getUserByAPIKey(api_key)),
                               False,
                               False)
      return self._return_message(obj)
    except NothingFoundException as error:
      return self.raise_error('NothingFoundException', error)
    except BrokerException as error:
      return self.raise_error('BrokerException', error)

  def view(self, uuid, api_key, **options):
    try:
      event = self.event_broker.get_by_uuid(uuid)
      self.checkIfViewable(event, self.get_user(api_key), False)
      with_definition = options.get('fulldefinitions', False)
      obj = self._object_to_json(event,
                               self.is_event_owner(event, self.getUserByAPIKey(api_key)),
                               True,
                               with_definition)

      return self._return_message(obj)
    except NothingFoundException as error:
      return self.raise_error('NothingFoundException', error)
    except BrokerException as error:
      return self.raise_error('BrokerException', error)

  def delete(self, uuid, api_key, **options):
    try:
      event = self.event_broker.get_by_uuid(uuid)
      self.checkIfViewable(event, self.get_user(api_key), False)
      return self.raise_error('NotImplemented',
                             'The delete method has not been implemented')

    except NothingFoundException as error:
      return self.raise_error('NothingFoundException', error)
    except BrokerException as error:
      return self.raise_error('BrokerException', error)

  def update(self, uuid, api_key, **options):
    if not uuid:
      try:
        rest_event = self.get_post_object()
        # map rest_event on event
        user = self.get_user(api_key)
        event = self.event_broker.build_event(
                       None,
                       'insert',
                       Status.get_by_name(rest_event.status),
                       TLPLevel.get_by_name(rest_event.tlp),
                       rest_event.description,
                       rest_event.title,
                       rest_event.published,
                       rest_event.first_seen,
                       rest_event.last_seen,
                       Risk.get_by_name(rest_event.risk),
                       Analysis.get_by_name(rest_event.analysis),
                       user,
                       rest_event.uuid)
        event.bit_value.is_rest_instert = True
        if rest_event.share == 1:
          event.bit_value.is_shareable = True
        else:
          event.bit_value.is_shareable = False
        # flush to DB
        self.event_broker.insert(event, commit=False)

        for obj in rest_event.objects:
          # create object
          db_object = self.__convert_rest_object(obj, event, event, commit=False)
          event.objects.append(db_object)

        self.event_broker.do_commit(True)

        with_definition = options.get('fulldefinitions', False)
        # obj = self._object_to_json(event, True, True, with_definition)
        rest_event = RestEvent()
        rest_event.uuid = event.uuid
        return self._return_message(dict(rest_event.to_dict(full=True,
                             with_definition=with_definition).items()
                 ))

      except BrokerException as error:
        return self.raise_error('BrokerException', error)

    else:
      return self.raise_error('Exception', 'Not Implemented')

  def __convert_rest_object(self, obj, parent, event, commit=False):
    db_object = self._convert_to_object(obj, parent, event, commit=commit)
    # generate Attributes
    db_object.attributes = self._convert_to_attribues(obj.attributes,
                                                          db_object, commit)
    for child in obj.children:
      child_db_obj = self.__convert_rest_object(child, db_object, event, commit)
      db_object.children.append(child_db_obj)
    return db_object

  def get_function_name(self, parameter, action):
    if action == 'GET':
      return RestEventController.PARAMETER_MAPPER.get(parameter, None)
    return None
