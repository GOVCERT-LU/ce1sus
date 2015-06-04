# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 30, 2015
"""

import base64
import cherrypy
from cherrypy._cperror import HTTPError
from datetime import datetime
import json
from os import makedirs
from os.path import exists
from shutil import rmtree
from tempfile import gettempdir

from ce1sus.controllers.base import ControllerException, ControllerIntegrityException
from ce1sus.controllers.common.merger import Merger
from ce1sus.mappers.stix.stixmapper import StixMapper
from ce1sus.views.web.common.base import BaseView
from ce1sus.views.web.common.decorators import require
from cybox.core import Observables
import openioc  # OpenIOC Bindings
import openioc_to_cybox  # OpenIOC to CybOX Script
from stix.core import STIXPackage, STIXHeader
from stix.indicator import Indicator
import stix.utils


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

__VERSION__ = 0.13


class OpenIOCException(Exception):
  pass


class OpenIOCAdapter(BaseView):

  def __init__(self, config, session=None):
    BaseView.__init__(self, config)
    self.stix_mapper = StixMapper(config, session)
    self.merger = Merger(config, session)
    self.base = self.config.get('OpenIOCAdapter', 'file', None)
    self.dump = self.config.get('OpenIOCAdapter', 'dump', False)
    if self.base is None:
      self.dump = False
      self.base = gettempdir()

  def get_dest_folder(self):
    """
    Returns the destination folder, and creates it when not existing
    """
    try:
      dest_path = '{0}/{1}/{2}'.format(datetime.utcnow().year,
                                       datetime.utcnow().month,
                                       datetime.utcnow().day)
      dest_path = self.base + '/' + dest_path
      if not exists(dest_path):
        makedirs(dest_path)
      return dest_path
    except TypeError as error:
      raise OpenIOCException(error)

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
    open_ioc_xml_string = base64.b64decode(data)

    base_dir, stix_file_path = self.__make_stix_xml_string(filename, open_ioc_xml_string)

    stix_package = STIXPackage.from_xml(stix_file_path)

    if not self.dump:
      rmtree(base_dir)

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

  def __make_stix_xml_string(self, filename, open_ioc_xml):
    # This is actually an adapted version of the openioc_to_stix.py to be compatible with ce1sus
    try:

      # save the file
      base_dir = self.get_dest_folder()
      open_ioc_filename = base_dir + '/' + filename
      open_stix_filename = base_dir + '/STIX_of_' + filename
      open_ioc_file = open(open_ioc_filename, 'w+')
      open_ioc_file.write(open_ioc_xml)
      open_ioc_file.close()

      openioc_indicators = openioc.parse(open_ioc_filename)
      observables_obj = openioc_to_cybox.generate_cybox(openioc_indicators, open_ioc_filename, True)
      observables_cls = Observables.from_obj(observables_obj)
      stix.utils.set_id_namespace({"https://github.com/STIXProject/openioc-to-stix": "openiocToSTIX"})
      stix_package = STIXPackage()
      input_namespaces = {"openioc": "http://openioc.org/"}

      stix_package.__input_namespaces__ = input_namespaces

      for observable in observables_cls.observables:
        indicator_dict = {}
        producer_dict = {}
        producer_dict['tools'] = [{'name': 'OpenIOC to STIX Utility', 'version': str(__VERSION__)}]
        indicator_dict['producer'] = producer_dict
        indicator_dict['title'] = "CybOX-represented Indicator Created from OpenIOC File"
        indicator = Indicator.from_dict(indicator_dict)
        indicator.add_observable(observables_cls.observables[0])
        stix_package.add_indicator(indicator)

      stix_header = STIXHeader()
      stix_header.package_intent = "Indicators - Malware Artifacts"
      stix_header.description = "CybOX-represented Indicators Translated from OpenIOC File"
      stix_package.stix_header = stix_header

      # Write the generated STIX Package as XML to the output file
      outfile = open(open_stix_filename, 'w')
      # Ignore any warnings - temporary fix for no schemaLocation w/ namespace
      with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        outfile.write(stix_package.to_xml())
        warnings.resetwarnings()
      outfile.flush()
      outfile.close()
      return base_dir, open_stix_filename
    except Exception as error:
      self.logger.error(error)
      raise cherrypy.HTTPError(500, error.message)
