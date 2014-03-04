# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.web.rest.handlers.restbase import RestBaseHandler
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
      owner = self._is_event_owner(event)
      if not owner:
        self._check_if_event_is_viewable(event)
      self._check_if_event_is_viewable(event)

      return self.return_object(event, owner, False, False)
    except ControllerNothingFoundException as error:
      return self._raise_nothing_found(error)
    except ControllerException as error:
      return self._raise_error('ControllerException', error=error)

  def view(self, uuid, **options):
    try:
      event = self.event_controller.get_by_uuid(uuid)
      owner = self._is_event_owner(event)
      if not owner:
        self._check_if_event_is_viewable(event)
      with_definition = options.get('fulldefinitions', False)
      return self.return_object(event, owner, True, with_definition)
    except ControllerNothingFoundException as error:
      return self._raise_nothing_found(error)
    except ControllerException as error:
      return self._raise_error('ControllerException', error=error)

  def update(self, uuid, **options):
    if not uuid:
      try:
        event = self.get_post_object('insert')
        user = self._get_user(False)
        # check if event is valid
        valid = event.validate()
        if valid:
          for obj in event.objects:
            valid = obj.validate(True)
            if valid:
              for attribute in obj.attributes:
                valid = attribute.validate(False)
                if not valid:
                  self._raise_invalid_error(attribute)
            else:
              # action when not valid
              self._raise_invalid_error(obj)
        else:
          # action when not valid
          self._raise_invalid_error(event)
        # ok the event is valid so continue
        event, valid = self.event_controller.insert_event(user, event)
        with_definition = options.get('fulldefinitions', False)
        event.maingroups = list()
        event.subgroups = list()
        event.objects = list()
        return self.return_object(event, True, False, with_definition)
      except ControllerException as error:
        return self._raise_error('ControllerException', error=error)

    else:
      return self._raise_error('Exception', msg='Not Implemented')

  # pylint: disable=R0201
  def get_function_name(self, parameter, action):
    if action == 'GET':
      return RestEventHandler.PARAMETER_MAPPER.get(parameter, None)
    return None
