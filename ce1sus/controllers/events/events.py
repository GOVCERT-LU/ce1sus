# -*- coding: utf-8 -*-

"""
module handing the events pages

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from ce1sus.brokers.event.eventbroker import EventBroker
from dagr.db.broker import BrokerException


class EventsController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.event_broker = self.broker_factory(EventBroker)

  def get_user_events(self, user, limit=200, offset=0):
    """
    Returns a list of events viewable by the user
    """
    try:
      return self.event_broker.get_all_for_user(user, limit, offset)
    except BrokerException as error:
      self._raise_exception(error)

  def get_events(self, uuids, start_date, end_date, offset, limit, user):
    try:
      return self.event_broker.get_events(uuids,
                                      start_date,
                                      end_date,
                                      offset,
                                      limit,
                                      user)
    except BrokerException as error:
      self._raise_exception(error)
