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
from dagr.helpers.datumzait import DatumZait


class RestEventsController(RestControllerBase):

  MAX_LIMIT = 20

  def __init__(self):
    RestControllerBase.__init__(self)
    self.event_broker = self.broker_factory(EventBroker)

  def view(self, uuid, api_key, **options):
    try:
      uuids = options.get('uuids', list())
      with_definition = options.get('fulldefinitions', False)

      start_date = options.get('startdate', None)
      end_date = options.get('enddate', DatumZait.utcnow())

      offset = options.get('page', 0)
      limit = options.get('limit', 20)

      user = self.get_user(api_key)

      # limit has to be between 0 and maximum value
      if limit < 0 or limit > RestEventsController.MAX_LIMIT:
        self.raise_error('InvalidArgument',
                        'The limit value has to be between 0 and 20')

      # search only if something was specified
      if start_date or uuids:
        events = self.event_broker.get_events(uuids,
                                      start_date,
                                      end_date,
                                      offset,
                                      limit,
                                      user)
      else:
        events = self.event_broker.get_all_for_user(user=user,
                                                limit=limit,
                                                offset=offset)

      result = list()
      for event in events:
        try:
          self.checkIfViewable(event, self.get_user(api_key), False)
          result.append(self._object_to_json(event,
                                           self.is_event_owner(event,
                                                             self.getUserByAPIKey(api_key)),
                                           True,
                                           with_definition))
        except cherrypy.HTTPError:
          pass

      result_dict = {'Results': result}
      return self._return_message(result_dict)

    except NothingFoundException as error:
      return self.raise_error('NothingFoundException', error)
    except BrokerException as error:
      return self.raise_error('BrokerException', error)

  def get_function_name(self, parameter, action):
    return None
