# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.brokers.event.eventbroker import EventBroker
from ce1sus.db.common.broker import BrokerException
from ce1sus.common.checks import is_user_priviledged


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventsController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    BaseController.__init__(self, config)
    self.event_broker = self.broker_factory(EventBroker)

  def get_events(self, offset, limit, user):
    try:
      int_lim = int(limit) - 1
      int_off = int(offset) - 1
      isadmin = is_user_priviledged(user)
      if isadmin:
        events = self.event_broker.get_all_limited(int_lim, int_off)
        nbr_total_events = self.event_broker.get_total_events()
      else:
        events = self.event_broker.get_all_limited_for_user(int_lim, int_off, user)
        nbr_total_events = self.event_broker.get_total_events_for_user()
      return (events, nbr_total_events)
    except (BrokerException, ValueError) as error:
      raise ControllerException(error)
