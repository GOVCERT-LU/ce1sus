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
from uuid import UUID

from ce1sus.controllers.base import ControllerException, ControllerIntegrityException, ControllerNothingFoundException
from ce1sus.controllers.common.merger import Merger
from ce1sus.mappers.stix.stixmapper import StixMapper
from ce1sus.views.web.common.base import BaseView
from ce1sus.views.web.common.decorators import require
from stix.core.stix_package import STIXPackage


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
  @require()
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

    # STIX wants lxml instead of xml
    xml = etree.fromstring(xml_string)

    stix_package = STIXPackage.from_xml(xml)

    try:
      event = self.stix_mapper.map_stix_package(stix_package, user)
      event.properties.is_validated = False
      self.event_controller.insert_event(user, event, True, True)
      event_permissions = self.event_controller.get_event_user_permissions(event, user)
      cherrypy.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
      return json.dumps(event.to_dict(complete, inflated, event_permissions, user))
    except ControllerIntegrityException as error:
      self.logger.debug(error)
      event = self.stix_mapper.map_stix_package(stix_package, user, False, True)
      local_event = self.event_controller.get_event_by_uuid(event.uuid)
      event_permissions = self.event_controller.get_event_user_permissions(event, user)
      merged_event = self.merger.merge_event(local_event, event, user, event_permissions)
      self.event_controller.update_event(user, merged_event, True, True)
      cherrypy.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
      return json.dumps(merged_event.to_dict(complete, inflated, event_permissions, user))
    except ControllerNothingFoundException as error:
      self.logger.error(error)
      raise HTTPError(404, '{0}'.format(error.message))
    except ControllerException as error:
      self.logger.error(error)
      raise HTTPError(400, '{0}'.format(error.message))

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  @require()
  def event(self, *vpath, **params):
    if len(vpath) > 0:
      uuid_string = vpath[0]
      # check if it is a uuid
      # check the mode
      make_file = params.get('file', None)
      if make_file == '':
        cherrypy.response.headers['Content-Type'] = 'application/x-download'
        cherrypy.response.headers["Content-Disposition"] = 'attachment; filename=Event_{0}_STIX.xml'.format(uuid_string)
      try:
        UUID(uuid_string, version=4)
      except ValueError as error:
        print error
        raise HTTPError(400, 'The provided uuid "{0}" is not valid'.format(uuid_string))
      try:
        event = self.event_controller.get_event_by_uuid(uuid_string)
        return self.stix_mapper.map_ce1sus_event(event, self.get_user())
      except ControllerNothingFoundException as error:
        raise  HTTPError(404, '{0}'.format(error.message))
    else:
      raise HTTPError(400, 'Cannot be called without a uuid')
