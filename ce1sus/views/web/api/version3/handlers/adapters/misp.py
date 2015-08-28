# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 26, 2015
"""
from base64 import b64decode
from ce1sus.helpers.common.config import Configuration, ConfigSectionNotFoundException
from datetime import datetime
from os import makedirs, remove
from os.path import dirname, abspath, isdir, isfile

from ce1sus.common.classes.cacheobject import MergerCache
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.common.merger.merger import Merger
from ce1sus.db.classes.internal.usrmgt.group import EventPermissions
from ce1sus.handlers.base import HandlerException
from ce1sus.mappers.misp.mispce1sus import MispConverter
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, RestHandlerNotFoundException, RestHandlerException
from ce1sus.controllers.admin.group import GroupController
from ce1sus.mappers.misp.ce1susmisp import Ce1susMISP


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MISPHandler(RestBaseHandler):

  def __init__(self, config):
    super(MISPHandler, self).__init__(config)
    self.misp_converter = MispConverter(config)
    self.ce1sus_converter = Ce1susMISP(config)
    self.merger = Merger(config)
    try:
      basePath = dirname(abspath(__file__))
      misp_config = Configuration(basePath + '/../../../../../../../config/mappers.conf')
    except ConfigSectionNotFoundException as error:
      raise ControllerException(error)
    self.dump = misp_config.get('MISPMapper', 'dump', False)
    self.dump_location = misp_config.get('MISPMapper', 'path', False)
    self.group_controller = GroupController(config)
    self.group_uuid = misp_config.get('MISPMapper', 'transformergroup', None)

  @rest_method(default=True)
  @methods(allowed=['POST'])
  def upload_xml(self, **args):
    try:
      cache_object = self.get_cache_object(args)
      cache_object.event_permissions = EventPermissions('0')
      cache_object.event_permissions.set_all()
      json = args.get('json')

      # check if the json is as expected
      filename = json.get('name', None)
      if filename:
        if 'XML' in filename or 'xml' in filename:
          data = json.get('data', None)
          if data:
            if data.get('data', None):
              data = data['data']
          else:
            raise HandlerException('Provided json does not have a data attribute')
        else:
          raise HandlerException('File does not end in xml or XML')
      else:
        raise HandlerException('Provided json does not have a file attribute')

      # start conversion
      xml_string = b64decode(data)
      if self.dump:
        self.__dump_file(filename, data)
      
      if self.group_uuid:
        group = self.group_controller.get_group_by_uuid(self.group_uuid)
      else:
        group = None

      event = self.misp_converter.convert_misp_xml_string(xml_string, cache_object, group)
      
      try:

        db_event = self.event_controller.get_event_by_uuid(event.uuid)
        self.logger.debug('Event {0} is in db'.format(event.uuid))
        # present in db merge it
        cache_object.reset()
        merger_cache = MergerCache(cache_object)
        self.merger.merge(db_event, event, merger_cache)
        return db_event.to_dict(cache_object)

      except ControllerNothingFoundException:
        self.logger.debug('Event {0} is not in db'.format(event.uuid))
        # not present in db add it
        self.event_controller.insert_event(event, True, True)
        return event.to_dict(cache_object)

    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)


  def __get_dump_path(self):
    sub_path = '{0}/{1}/{2}'.format(datetime.now().year,
                                    datetime.now().month,
                                    datetime.now().day)
    if self.dump_location:
      path = '{0}/{1}/{2}'.format(self.dump_location, sub_path, dirname)
      if not isdir(path):
        makedirs(path)
      return path
    else:
      message = 'Dumping of files was activated but no file location was specified'
      self.logger.error(message)
      raise HandlerException(message)

  def __dump_file(self, filename, data):
    path = self.__get_dump_path()

    full_path = '{0}/{1}'.format(path, filename)
    if isfile(full_path):
      remove(full_path)
    f = open(full_path, 'w+')
    f.write(data)
    f.close()

  @rest_method()
  @methods(allowed=['GET'])
  def export_xml(self, **args):
    try:
      cache_object = self.get_cache_object(args)
      method = args.get('method', None)
      path = args.get('path')
      requested_object = self.parse_path(path, method)
      event_id = requested_object.get('event_id', None)
      if event_id:
        event = self.event_controller.get_event_by_uuid(event_id)
        xml_str = self.ce1sus_converter.create_event_xml(event, cache_object)
        return xml_str
      else:
        raise RestHandlerException('Cannot be called witout a valid uuid')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  @rest_method()

  def shadow_attributes(self, *vpath, **params):
    # this is called from the misp server to see it his know events have new proposals
    # TODO: Proposal for misp
    raise RestHandlerNotFoundException('Not supported')
