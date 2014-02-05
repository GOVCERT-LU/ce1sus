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
import cherrypy

from dagr.helpers.datumzait import DatumZait
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk


class EventsController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.event_broker = self.broker_factory(EventBroker)

  def get_user_events(self, user, limit=200, offset=0):
    """
    Returns a list of events viewable by the user
    """
    return self.event_broker.get_all_for_user(user, limit, offset)
