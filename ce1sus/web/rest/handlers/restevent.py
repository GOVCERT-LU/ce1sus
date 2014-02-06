# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.web.rest.handlers.restbase import RestBaseHandler
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.brokers.staticbroker import TLPLevel, Risk, Analysis, Status
from ce1sus.api.restclasses import RestEvent
from ce1sus.controllers.event.event import EventController
from dagr.controllers.base import ControllerException
from ce1sus.controllers.base import ControllerNothingFoundException


class RestEventHandler(RestBaseHandler):

  PARAMETER_MAPPER = {'metadata': 'view_metadata'}

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.event_controller = EventController(config)

  def view_metadata(self, uuid, **options):
    try:
      event = self.event_controller.get_by_uuid(uuid)
      self._check_if_event_is_viewable(event)
      owner = self._check_if_event_owner(event)
      return self.return_object(event, owner, False, False)
    except ControllerNothingFoundException as error:
      return self._raise_nothing_found(error)
    except ControllerException as error:
      return self._raise_error('ControllerException', error)

  def view(self, uuid, **options):
    try:
      event = self.event_controller.get_by_uuid(uuid)
      self._check_if_event_is_viewable(event)
      owner = self._check_if_event_owner(event)

      with_definition = options.get('fulldefinitions', False)

      return self.return_object(event, owner, True, with_definition)
    except ControllerNothingFoundException as error:
      return self._raise_nothing_found(error)
    except ControllerException as error:
      return self._raise_error('ControllerException', error)

  def update(self, uuid, **options):
    if not uuid:
      try:
        rest_event = self.get_post_object()

        user = self._get_user()
        event = self.event_controller.populate_rest_event(user, rest_event, 'insert')
        event, valid = self.event_controller.insert_event(user, event, False)
        if valid:
          # if the event is valid continue with the objects
          for obj in rest_event.objects:
            # create object
            db_object = self.__convert_rest_object(obj, event, event, commit=False)
            event.objects.append(db_object)

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
