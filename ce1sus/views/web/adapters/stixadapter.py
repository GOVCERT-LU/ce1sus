# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 28, 2015
"""
import base64
import cherrypy
from cherrypy._cperror import HTTPError
from lxml import etree

from ce1sus.controllers.base import ControllerException
from ce1sus.mappers.stix.stixmapper import StixMapper
from ce1sus.views.web.common.base import BaseView
from stix.core.stix_package import STIXPackage


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class STIXAdapter(BaseView):

  def __init__(self, config, session=None):
    BaseView.__init__(self, config)
    self.stix_mapper = StixMapper(config, session)

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  @cherrypy.tools.json_out()
  @cherrypy.tools.json_in()
  def upload_xml(self, *vpath, **params):
    try:
      user = self.user_controller.get_user_by_username(self.get_user().username)
      input_json = cherrypy.request.json
      filename = input_json['name']
      self.logger.info('Starting to import xml form file {0}'.format(filename))
      data = input_json['data']['data']
      complete = params.get('complete', False)
      inflated = params.get('inflated', False)
      xml_string = base64.b64decode(data)

      # STIX waants lxml instead of xml
      xml = etree.fromstring(xml_string)

      stix_package = STIXPackage.from_xml(xml)
      event = self.stix_mapper.map_stix_package(stix_package, user)
      self.event_controller.insert_event(user, event)
      event_permissions = self.event_controller.get_event_user_permissions(event, user)
      return event.to_dict(complete, inflated, event_permissions, user)
    except ControllerException as error:
      raise HTTPError(400, error)

  """
  @rest_method()
  @methods(allowed=['GET'])
  def stix_import(self, **args):
    stix_package = STIXPackage.from_xml('/home/jhemp/Downloads/CIMBL-150-CERTS.xml')
    user = self.user_broker.get_all()[0]
    event = self.stix_mapper.map_stix_package(stix_package, user)
    self.event_controller.insert_event(user, event)
    pass
  """
