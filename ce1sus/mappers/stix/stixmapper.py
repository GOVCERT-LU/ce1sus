# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 12, 2014
"""
from ce1sus.controllers.base import BaseController
from ce1sus.controllers.events.event import EventController
from ce1sus.mappers.stix.helpers.ce1susstix import Ce1susStixMapper
from ce1sus.mappers.stix.helpers.stixce1sus import StixCelsusMapper, set_extended_logging
import cybox.utils.idgen
from cybox.utils.nsparser import Namespace
import stix.utils.idgen


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class StixMapperException(Exception):
  pass


class StixMapper(BaseController):

  def __init__(self, config, session=None):
    super(BaseController, self).__init__(config, session)
    self.config = config
    ce1sus_url = config.get('ce1sus', 'baseurl', None)
    self.event_controller = EventController(config, session)
    self.stix_ce1sus_mapper = StixCelsusMapper(config, session)
    self.ce1sus_stix_mapper = Ce1susStixMapper(config, session)
    if ce1sus_url:
            # Set the namespaces
      cybox.utils.idgen.set_id_namespace(Namespace(ce1sus_url, 'ce1sus'))
      stix.utils.idgen.set_id_namespace({ce1sus_url: 'ce1sus'})

    else:
      raise StixMapperException(u'the base url was not specified in configuration')

  def map_stix_package(self, stix_package, user, make_insert=True, ignore_id=False):
    event = self.stix_ce1sus_mapper.create_event(stix_package, user, ignore_id)
    set_extended_logging(event, user, user.group)
    if make_insert:
      self.event_controller.insert_event(user, event, True, False)

    return event

  def map_ce1sus_event(self, event, user):
    stix_package = self.ce1sus_stix_mapper.create_stix(event, user)


    return stix_package.to_xml()
