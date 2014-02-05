# -*- codin g: utf-8 -*-

"""
(Description)

Created on Feb 5, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy
from ce1sus.web.views.base import Ce1susBaseView
from dagr.helpers.debug import Log
from ce1sus.web.rest.handlers.restbase import RestAPIException, create_status
from ce1sus.common.system import System, SantityCheckerException
from dagr.helpers.validator.valuevalidator import ValueValidator
from dagr.helpers.validator.objectvalidator import ValidationException
from cherrypy import request
from dagr.helpers.converters import ValueConverter
import re
import ast
import json
from dagr.db.broker import BrokerException


class RestController(Ce1susBaseView):

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

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.__logger = Log(config)
    self.instances = dict()
    # add instances known to rest
    # self.instances['event'] = RestEventController(config)
    # self.instances['events'] = RestEventsController(config)
    # self.instances['search'] = RestSearchController(config)
    # self.instances['definition'] = RestDefinitionController(config)
    # self.instances['definitions'] = RestDefinitionsController(config)

  def _get_logger(self):
    """returns the class logger"""
    return self.__logger.get_logger(self.__class__.__name__)

  def _raise_fatal_error(self, error=None, msg=None):
    """generates a fatal error"""
    if error:
      self._get_logger.fatal(error)
      message = error.message
    else:
      self._get_logger.fatal(msg)
      message = msg
    raise cherrypy.HTTPError(418, message)

  def _raise_error(self, errorclass, error=None, msg=None):
    """generates an error"""
    if msg:
      message = msg
    else:
      if error:
        message = error.message
      else:
        self._get_logger().fatal('Error message was not defined')
        raise cherrypy.HTTPError(418)
    self._get_logger().error(message)
    raise RestAPIException('{0}: {1}'.format(errorclass, message))

  def __check_version(self, version):
    """checks if the requested version is compatible with this version"""
    try:
      System.check_rest_api(version)
    except SantityCheckerException as error:
      self._raise_error('VersionMismatch', msg='{0}'.format(error))

  def __get_controller_name(self, path_elements):
    # the controller name has to be on the second position of the url
    if (len(path_elements) > 1):
      return path_elements[1].strip()
    else:
      self._raise_error('SystemError', msg='Controller name was not specified')

  def __check_if_valid_uuid(self, string):
    try:
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
    except ValidationException as error:
      self._raise_error('SystemError', error=error)

  def __get_parameter(self, path_elements):
    # needs to check if its a uuid or chksum else it is a parameter
    if (len(path_elements) > 2):
      possible_uuid = path_elements[2]
      if self.__check_if_valid_uuid(possible_uuid):
        return None
      else:
        return possible_uuid
    else:
      return None

  def __get_uuid(self, path_elements, position):
    """returns the uuid if any"""
    if (len(path_elements) > position):
      uuid = path_elements[position]
      if self.__check_if_valid_uuid(uuid):
        return uuid
      else:
        self._raise_error('SystemError', msg='The given uuid/chksim "{0}" is invalid').format(uuid)
    else:
      return None

  def __split_path(self, vpath):
    # path need at least 2 elements version/controller/....
    if not vpath:
      self._destroy_session()
      raise cherrypy.HTTPError(400)

    path_elements = list(vpath)
    if (len(path_elements) > 0):
      self.__check_version(path_elements[0])

    controller_name = self.__get_controller_name(path_elements)
    parameter = self.__get_parameter(path_elements)
    if parameter:
      # then there is a possible uuid on the next position
      uuid = self.__get_uuid(path_elements, 3)
      # check if allowed parameter
      if parameter.isdigit():
        self._raise_error('SystemError', msg='Unspecified')
      else:
        # check if the parameter is allowed
        if not parameter in RestController.REST_Allowed_Parameters:
          self._raise_error('InvalidParameter ',
                            msg='Parameter {0}'.format(parameter))
    else:
      # then the second else it is on the second position
      uuid = self.__get_uuid(path_elements, 2)

    return controller_name, parameter, uuid

  def __get_header_value(self, key):
    value = request.headers.get(key, '').strip()
    if value:
      if value == 'True':
        return True
      if value == 'False':
        return False
      if value.isdigit():
        return ValueConverter.set_integer(value)
      # check if datetime
      if ValueValidator.validateDateTime(value):
        return ValueConverter.set_date(value)
      # TODO: user JSON instead
      if (re.match(r'^\[.*\]$', value, re.MULTILINE) is not None or
        re.match(r'^\{.*\}$', value, re.MULTILINE) is not None):
        value = ast.literal_eval(value)
        return value
      else:
        return value
    else:
      return None

  def __get_controller(self, controller_name):
    if controller_name in self.instances:
      return self.instances[controller_name]
    else:
      self._get_logger().fatal('No instance defined for {0}'.format(controller_name))
      self._destroy_session()
      raise cherrypy.NotFound

  def __get_action(self):
    action = cherrypy.request.method
    if not action in RestController.REST_mapper:
      self._raise_fatal_error(msg='Action {0} is not defined in mapper'.format(action))

  def __handle_restapiexceptions(self, error):
    self._get_logger().fatal(error)
    # prepare api error
    # path = request.script_name + request.path_info
    temp = dict(create_status('RestException',
                               error.message))
    self._destroy_session()
    return json.dumps(temp)

  def __get_user(self, api_key):
    try:
      user = self.get_user(api_key)
      self._create_session()
      return user
    except BrokerException as error:
      self._get_logger().debug(error)
      self._destroy_session()
      raise cherrypy.HTTPError(403)

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
      user = self.__get_user(api_key)
      controller = self.__get_controller(controller_name)

      action = self.__get_action()

      # determine method to call
      if parameter:
        method_name = controller.get_function_name(parameter, action)
      else:
        method_name = RestController.REST_mapper[action]

      if method_name:
        # call method if existing
        method = getattr(controller, method_name, None)
      else:
        self._raise_error('SystemError', msg='Method {0} is undefined'.format(method))

      if method:
        # TODO: put uuid in options?!?
        result = method(uuid, user, **options)
        self._destroy_session()
        # The rest handlers should always give json back!
        if result:
          return result
        else:
          self._raise_fatal_error(msg='Called function returned Noting')
      else:
        self._raise_error('SystemError', msg='Method {0} is not defined for {0}'.format(action,
                                                                  controller))
    except RestAPIException as error:
      self.__handle_restapiexceptions(error)
