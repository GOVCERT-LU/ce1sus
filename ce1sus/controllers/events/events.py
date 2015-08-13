# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.brokers.event.eventbroker import EventBroker
from ce1sus.db.common.broker import BrokerException
from ce1sus.common.checks import is_user_priviledged
from ce1sus.controllers.events.relations import RelationController


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventsController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    super(EventsController, self).__init__(config, session)
    self.event_broker = self.broker_factory(EventBroker)
    self.relation_controller = RelationController(config, session)

  def get_events(self, offset, limit, user, parameters=None):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      if offset:
        int_off = int(offset) - 1
      if limit:
        int_lim = int(limit)

      isadmin = is_user_priviledged(user)
      if isadmin:
        if offset and limit:
          events = self.event_broker.get_all_limited(int_lim, int_off, parameters)
          nbr_total_events = self.event_broker.get_total_events(parameters)
        else:
          events = self.event_broker.get_all()
          nbr_total_events = len(events)
        return (events, nbr_total_events)
      else:
        if offset and limit:
          events = self.event_broker.get_all_limited_for_user(int_lim, int_off, user, parameters)
          nbr_total_events = self.event_broker.get_total_events_for_user(user, parameters)
        else:
          events = self.event_broker.get_all_for_user(user)
          nbr_total_events = len(events)

        return (events, nbr_total_events)
    except (BrokerException, ValueError) as error:
      raise ControllerException(error)

  def get_unvalidated_events(self, offset, limit, user, parameters=None):
    try:
      int_lim = int(limit) - 1
      int_off = int(offset) - 1
      events = self.event_broker.get_all_unvalidated(int_lim, int_off, parameters)
      nbr_total_events = self.event_broker.get_all_unvalidated_total(parameters)
      return (events, nbr_total_events)
    except (BrokerException, ValueError) as error:
      raise ControllerException(error)
