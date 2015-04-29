# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 12, 2014
"""
from ce1sus.controllers.base import BaseController
from ce1sus.mappers.stix.helpers.stixce1sus import StixCelsusMapper, set_extended_logging
import cybox.utils.idgen
from cybox.utils.nsparser import Namespace
import stix.utils.idgen
from ce1sus.controllers.events.event import EventController


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class StixMapperException(Exception):
  pass


class StixMapper(BaseController):

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.config = config
    ce1sus_url = config.get('ce1sus', 'baseurl', None)
    self.event_controller = EventController(config, session)
    self.stix_ce1sus_mapper = StixCelsusMapper(config, session)
    if ce1sus_url:
      # Set the namespaces
      cybox.utils.idgen.set_id_namespace(Namespace(ce1sus_url, 'ce1sus'))
      stix.utils.idgen.set_id_namespace({ce1sus_url: 'ce1sus'})

    else:
      raise StixMapperException(u'the base url was not specified in configuration')

  def map_stix_package(self, stix_package, user):
    event = self.stix_ce1sus_mapper.create_event(stix_package, user)
    set_extended_logging(event, user, user.group)
    self.event_controller.insert_event(user, event, False, False)

    return event

  def map_ce1sus_event(self, event):
    raise StixMapperException(u'Not implemented')
