# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
from ce1sus.controllers.events.event import EventController
from ce1sus.db.brokers.permissions.user import UserBroker
from ce1sus.mappers.stix.stixmapper import StixMapper
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods
from stix.core.stix_package import STIXPackage


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.stix_mapper = StixMapper(config)
    self.event_controller = EventController(config)
    self.user_broker = self.event_controller.broker_factory(UserBroker)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  def stix_import(self, **args):
    stix_package = STIXPackage.from_xml('/home/jhemp/Downloads/CIMBL-150-CERTS.xml')
    user = self.user_broker.get_all()[0]
    event = self.stix_mapper.map_stix_package(stix_package, user)

    self.event_controller.insert_event(user, event)
