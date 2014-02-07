# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.web.rest.handlers.restbase import RestBaseHandler
from ce1sus.api.restclasses import RestEvent
from ce1sus.controllers.event.event import EventController
from dagr.controllers.base import ControllerException
from ce1sus.controllers.base import ControllerNothingFoundException
from dagr.helpers.validator.objectvalidator import ObjectValidator


class RestEventHandler(RestBaseHandler):

  PARAMETER_MAPPER = {'metadata': 'view_metadata'}

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.event_controller = EventController(config)

  def view_metadata(self, uuid, **options):
    try:
      event = self.event_controller.get_by_uuid(uuid)
      self._check_if_event_is_viewable(event)
      owner = self._is_event_owner(event)
      return self.return_object(event, owner, False, False)
    except ControllerNothingFoundException as error:
      return self._raise_nothing_found(error)
    except ControllerException as error:
      return self._raise_error('ControllerException', error=error)

  def view(self, uuid, **options):
    try:
      event = self.event_controller.get_by_uuid(uuid)
      self._is_event_viewable(event)
      owner = self._is_event_owner(event)

      with_definition = options.get('fulldefinitions', False)
      return self.return_object(event, owner, True, with_definition)
    except ControllerNothingFoundException as error:
      return self._raise_nothing_found(error)
    except ControllerException as error:
      return self._raise_error('ControllerException', error=error)

  def _raise_invalid_error(self, obj):
    error_msg = ObjectValidator.getFirstValidationError(obj)
    self._raise_error('InvalidException', msg=error_msg)

  def update(self, uuid, **options):
    if not uuid:
      try:
        rest_event = self.get_post_object()

        user = self._get_user()
        event = self.convert_to_db_Object(rest_event, user, 'insert')
        # first check if event is valid
        valid = event.validate()
        if valid:
          for obj in event.objects:
            valid = obj.validate()
            if valid:
              for attribute in obj.attribtues:
                valid = attribute.validate()
                if not valid:
                  self._raise_invalid_error(attribute)
            else:
              # action when not valid
              self._raise_invalid_error(obj)
            event, valid = self.event_controller.insert_event(user, event)
        else:
          # action when not valid
          self._raise_invalid_error(event)

        with_definition = options.get('fulldefinitions', False)
        # obj = self._object_to_json(event, True, True, with_definition)
        rest_event = RestEvent()
        rest_event.uuid = event.uuid
        return self.return_object(event, True, True, with_definition)
      except ControllerException as error:
        return self._raise_error('ControllerException', error=error)

    else:
      return self._raise_error('Exception', msg='Not Implemented')

  def get_function_name(self, parameter, action):
    if action == 'GET':
      return RestEventHandler.PARAMETER_MAPPER.get(parameter, None)
    return None
