# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 28, 2015
"""
import base64
import cherrypy
from cherrypy._cperror import HTTPError
import json
from lxml import etree

from ce1sus.controllers.base import ControllerException, ControllerIntegrityException
from ce1sus.mappers.stix.stixmapper import StixMapper
from ce1sus.views.web.common.base import BaseView
from stix.core.stix_package import STIXPackage
from ce1sus.controllers.common.merger import Merger


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class STIXAdapter(BaseView):

  def __init__(self, config, session=None):
    BaseView.__init__(self, config)
    self.stix_mapper = StixMapper(config, session)
    self.merger = Merger(config, session)

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def upload_xml(self, *vpath, **params):
    user = None
    try:
      user = self.user_controller.get_user_by_username(self.get_user().username)
    except ControllerException as error:
      self.logger.error(error)
      raise HTTPError(400, error.message)

    input_json = self.get_json()
    filename = input_json['name']
    self.logger.info('Starting to import xml form file {0}'.format(filename))
    data = input_json['data']['data']
    complete = params.get('complete', False)
    inflated = params.get('inflated', False)
    xml_string = base64.b64decode(data)

    # STIX waants lxml instead of xml
    xml = etree.fromstring(xml_string)

    stix_package = STIXPackage.from_xml(xml)

    try:
      event = self.stix_mapper.map_stix_package(stix_package, user)
      self.event_controller.insert_event(user, event)
      event_permissions = self.event_controller.get_event_user_permissions(event, user)
      cherrypy.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
      return json.dumps(event.to_dict(complete, inflated, event_permissions, user))
    except ControllerIntegrityException as error:
      # TODO: merge
      event = self.stix_mapper.map_stix_package(stix_package, user, False, True)
      local_event = self.event_controller.get_event_by_uuid(event.uuid)
      event_permissions = self.event_controller.get_event_user_permissions(event, user)
      merged_event = self.merger.merge_event(local_event, event, user, event_permissions)
      self.event_controller.update_event(user, merged_event, True, True)
      cherrypy.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
      return json.dumps(merged_event.to_dict(complete, inflated, event_permissions, user))
    except ControllerException as error:
      self.logger.error(error)
      raise HTTPError(400, error.message)
