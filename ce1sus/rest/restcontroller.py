# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy
from dagr.db.broker import BrokerException
from ce1sus.sanity import SantityChecker, SantityCheckerException
from ce1sus.rest.handlers.restevent import RestEventController
from ce1sus.rest.handlers.restevents import RestEventsController
from ce1sus.rest.handlers.restsearch import RestSearchController
from ce1sus.rest.restbase import RestControllerBase, RestAPIException
from cherrypy import request
import json
from dagr.helpers.validator.valuevalidator import ValueValidator
from dagr.helpers.validator.objectvalidator import ValidationException
from dagr.helpers.converters import ValueConverter
import re
from ce1sus.web.helpers.protection import Protector
from ce1sus.rest.handlers.restdefinition import RestDefinitionController
from ce1sus.rest.handlers.restdefinitions import RestDefinitionsController
import ast


class RestController(RestControllerBase):

  REST_mapper = {'DELETE': 'remove',
       'GET': 'view',
       'POST': 'update'}

  REST_Allowed_Parameters = ['metadata',
                             'attributes',
                             'events',
                             'objects',
                             'attribute',
                             'object']
  REST_Allowed_Options = ['fulldefinitions',
                          'page',
                          'limit',
                          'startdate',
                          'enddate',
                          'objecttype',
                          'objectattributes',
                          'attributes',
                          'key',
                          'uuids',
                          'chksum']

  def __init__(self, ce1susConfigFile):
    RestControllerBase.__init__(self)
    self.configFile = ce1susConfigFile

    self.instances = dict()
    # add instances known to rest
    self.instances['event'] = RestEventController()
    self.instances['events'] = RestEventsController()
    self.instances['search'] = RestSearchController()
    self.instances['definition'] = RestDefinitionController()
    self.instances['definitions'] = RestDefinitionsController()
    self.sanityChecker = SantityChecker(self.configFile)

  def __check_version(self, version):

    try:
      # self.sanityChecker.checkDB()
      # self.sanityChecker.checkRestAPI(version)
      pass
    except SantityCheckerException as e:
      self.raise_error('VersionMismatch', '{0}'.format(e))

  def __check_api_key(self, api_key):
    try:
      user = self.get_user(api_key)
      del user
      exists = True
    except BrokerException as e:
      self._get_logger().debug(e)
      exists = False

    if not exists:
      self._get_logger().debug('Key does not exists')
      Protector.clearRestSession()
      raise cherrypy.HTTPError(403)

    # store key in session
    Protector.setRestSession(api_key)

  def __get_controller(self, controller_name):
    if controller_name in self.instances:
      return self.instances[controller_name]
    else:
      self._get_logger().debug(
                        'No instance defined for {0}'.format(controller_name))
      Protector.clearRestSession()
      raise cherrypy.NotFound

  def __check_if_valid_uuid(self, string):
    regex = r'^[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$'

    result = ValueValidator.validateRegex(string,
                                        regex,
                                        'Not a valid UUID')
    if not result:
      # then it may be a checksum
      regex = r'^[0-9a-fA-F]{40}$'
      result = ValueValidator.validateRegex(string,
                                        regex,
                                        'Not a valid chksum')
    return result

  def __split_path(self, vpath):
    # path need at least 2 elements version/controller/....
    if not vpath:
      Protector.clearRestSession()
      raise cherrypy.HTTPError(400)
    controller_name = None
    parameter = None
    uuid = None

    path_elements = list(vpath)

    if (len(path_elements) > 0):
      self.__check_version(path_elements[0])

    if (len(path_elements) > 1) and (len(path_elements) < 5):
      controller_name = path_elements[1].strip()
      if (len(path_elements) > 2):
        possible_uuid = path_elements[2]
        if self.__check_if_valid_uuid(possible_uuid):
          uuid = possible_uuid.strip()
        else:
          parameter = possible_uuid
          try:
            int(parameter)
            Protector.clearRestSession()
            raise cherrypy.HTTPError(418)
          except ValueError:
            if parameter not in RestController.REST_Allowed_Parameters:
              Protector.clearRestSession()
              self.raise_error('InvalidParameter ',
                              'Parameter {0}'.format(parameter))
        if (len(path_elements) > 3):
          possible_uuid = path_elements[3]
          try:
            if self.__check_if_valid_uuid(possible_uuid):
              uuid = possible_uuid.strip()
            else:
              Protector.clearRestSession()
              raise cherrypy.HTTPError(418)
          except ValidationException:
            self.raise_error('InvalidParameter ',
                              'Parameter {0}'.format(parameter))
    else:
      Protector.clearRestSession()
      raise cherrypy.HTTPError(400)

    return controller_name, parameter, uuid

  def __get_header_value(self, key):
    value = request.headers.get(key, '').strip()
    if value:
      if value == 'True':
        return True
      if value == 'False':
        return False
      if value.isdigit():
        return ValueConverter.setInteger(value)
      # check if datetime
      if ValueValidator.validateDateTime(value):
        return ValueConverter.setDate(value)
      if (re.match(r'^\[.*\]$', value, re.MULTILINE) is not None or
        re.match(r'^\{.*\}$', value, re.MULTILINE) is not None):
        value = ast.literal_eval(value)
        return value
      else:
        return value
    else:
      return None

  def __process_headers(self):
    remote_addr = self.__get_header_value('Remote-Addr')
    self._get_logger().info('Connection from {0}'.format(remote_addr))

    api_key = self.__get_header_value('key')
    self.__check_api_key(api_key)

    # make custom parmeters
    options = dict()
    for key in RestController.REST_Allowed_Options:
      options[key] = self.__get_header_value(key)
    return api_key, options

  @cherrypy.expose
  def default(self, *vpath, **params):
    try:
      # check if the path is correct
      controller_name, parameter, uuid = self.__split_path(vpath)
      api_key, options = self.__process_headers()

      controller = self.__get_controller(controller_name)

      # getMethodToCall
      action = cherrypy.request.method
      if not action in RestController.REST_mapper:
        self._get_logger().debug(
                          'Action {0} is not defined in mapper'.format(action))
        Protector.clearRestSession()
        raise cherrypy.HTTPError(400)

      if parameter:
        method_name = controller.get_function_name(parameter, action)
      else:
        method_name = RestController.REST_mapper[action]

      if method_name:
      # call method if existing
        method = getattr(controller, method_name, None)
      else:
        Protector.clearRestSession()
        raise cherrypy.HTTPError(400)

      if method:
        try:
          result = method(uuid, api_key, **options)
          Protector.clearRestSession()
          # The rest handlers should always give json back!
          if not result:
            raise RestAPIException('Called function returned Noting')
          return result
        except RestAPIException as error:
          self._get_logger().debug(
                          'Error occured during {0} for {1} due to {2}'.format(
                                                                    action,
                                                                    controller,
                                                                    error))
          temp = dict(self._create_status('RestException', error.message))
          Protector.clearRestSession()
          return json.dumps(temp)
      else:
        self._get_logger().debug(
                          'Method {0} is not defined for {0}'.format(action,
                                                                  controller))
        # if nothing is found do default
        path = request.script_name + request.path_info
        temp = dict(self._create_status('RestException',
                                       "The path '%s' was not found." % path))
        Protector.clearRestSession()
        return json.dumps(temp)
    except RestAPIException as error:
      self._get_logger().debug(
                    'Error occured during {0}'.format(error))
      temp = dict(self._create_status('RestException', error.message))
      Protector.clearRestSession()
      return json.dumps(temp)
