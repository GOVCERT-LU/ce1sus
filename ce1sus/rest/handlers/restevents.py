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


class RestEventsController(RestControllerBase):

  MAX_LIMIT = 20

  def __init__(self):
    RestControllerBase.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)

  def view(self, uuid, apiKey, **options):
    try:
      uuids = options.get('UUID', list())
      withDefinition = options.get('Full-Definitions', False)

      startDate = options.get('startdate', None)
      endDate = options.get('enddate', datumzait.utcnow())

      offset = options.get('page', 0)
      limit = options.get('limit', 20)

      # limit has to be between 0 and maximum value
      if limit < 0 or limit > RestEventsController.MAX_LIMIT:
        self.raiseError('InvalidArgument',
                        'The limit value has to be between 0 and 20')

      # search only if something was specified
      if startDate or uuids:
        events = self.eventBroker.getEvents(uuids,
                                      startDate,
                                      endDate,
                                      offset,
                                      limit)
        result = list()
        for event in events:
          try:
            self._checkIfViewable(event, self.getUser(apiKey))
            result.append(self._objectToJSON(event,
                                             self._isEventOwner(event, apiKey),
                                             True,
                                             withDefinition))
          except cherrypy.HTTPError:
            pass

        resultDict = {'Results': result}
        return self._returnMessage(resultDict)
      else:
        self.raiseError('InvalidArgument',
                         'At least one argument has to be specified')
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def getFunctionName(self, parameter, action):
    return None
