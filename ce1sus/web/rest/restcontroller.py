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
from ce1sus.web.rest.handlers.restbase import RestBaseHandler, RestHandlerException
from dagr.helpers.converters import convert_string_to_value
from ce1sus.common.system import System, SantityCheckerException
from dagr.helpers.validator.valuevalidator import ValueValidator
from dagr.helpers.validator.objectvalidator import ValidationException
from cherrypy import request
import json
from ce1sus.controllers.login import LoginController
from ce1sus.web.rest.handlers.restevent import RestEventHandler
from ce1sus.web.rest.handlers.restevents import RestEventsHandler
from ce1sus.web.rest.handlers.restdefinitions import RestDefinitionsHanldler
from ce1sus.web.rest.handlers.restdefinition import RestDefinitionHanldler
from dagr.controllers.base import ControllerException
from ce1sus.web.rest.handlers.restsearch import RestSearchHandler


class RestController(RestBaseHandler):
  """ Main class for REST calls"""

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
    RestBaseHandler.__init__(self, config)
    self.login_controller = LoginController(config)
    self.instances = dict()
    # add instances known to rest
    self.instances['event'] = RestEventHandler(config)
    self.instances['events'] = RestEventsHandler(config)
    self.instances['search'] = RestSearchHandler(config)
    self.instances['definition'] = RestDefinitionHanldler(config)
    self.instances['definitions'] = RestDefinitionsHanldler(config)

  def __check_version(self, version):
    """checks if the requested version is compatible with this version"""
    try:
      System.check_rest_api(version)
    except SantityCheckerException as error:
      self._raise_error('VersionMismatch', msg='{0}'.format(error))

  def __get_controller_name(self, path_elements):
    """Returns the requested controller name"""

    # the controller name has to be on the second position of the url
    if (len(path_elements) > 1):
      return path_elements[1].strip()
    else:
      self._raise_error('SystemError', msg='Controller name was not specified')

  def __check_if_valid_uuid(self, string):
    """Checks if the uuid is valid"""
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
    """Returns the requested parameter"""
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
    """Returns controller name, parameter and uuid from the path"""
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
    """Returns the header value with the given key"""
    value = request.headers.get(key, '').strip()
    return_value = convert_string_to_value(value)
    self._get_logger().debug('Found value {0} for key {1}'.format(return_value, key))
    return return_value

  def __get_controller(self, controller_name):
    """Returns the requested controller instance """
    if controller_name in self.instances:
      return self.instances[controller_name]
    else:
      self._get_logger().fatal('No instance defined for {0}'.format(controller_name))
      self._destroy_session()
      raise cherrypy.NotFound

  # pylint: disable=R0201
  def __get_action(self):
    """Returns the request action"""
    return cherrypy.request.method

  def __handle_handler_exceptions(self, error):
    """Generates the return message for hanlder exceptions"""
    self._get_logger().fatal(error)
    # prepare api error
    # path = request.script_name + request.path_info
    temp = dict(self.create_status('RestException',
                               error.message))
    self._destroy_session()
    return json.dumps(temp)

  def __get_user(self, api_key):
    """Returns the user if existing else raises a 403"""
    user = None
    try:
      user = self.login_controller.get_user_by_apikey(api_key)
    except ControllerException as error:
      self._get_logger().debug(error)
    if user:
      return user
    else:
      self._destroy_session()
      raise cherrypy.HTTPError(403)

  def __process_headers(self):
    """converts the header to option values"""
    remote_addr = self.__get_header_value('Remote-Addr')
    self._get_logger().info('Connection from {0}'.format(remote_addr))
    api_key = self.__get_header_value('key')
    # make custom parmeters
    options = dict()
    for key in RestController.REST_Allowed_Options:
      options[key] = self.__get_header_value(key)
    return api_key, options

  @cherrypy.expose
  def default(self, *vpath, **params):
    """Main REST function"""
    try:
      # check if the path is correct
      controller_name, parameter, uuid = self.__split_path(vpath)
      api_key, options = self.__process_headers()
      user = self.__get_user(api_key)
      if user:
        self._get_logger().info('User "{0}" logged in by key'.format(user.username))
        self._create_session()
        self._put_user_to_session(user)

      controller = self.__get_controller(controller_name)

      action = self.__get_action()

      # determine method to call
      if parameter:
        method_name = controller.get_function_name(parameter, action)
      else:
        if action in RestController.REST_mapper:
          method_name = RestController.REST_mapper[action]
        else:
          self._raise_fatal_error(msg='Action {0} is not defined in mapper'.format(action))

      method = None
      if method_name:
        # call method if existing
        method = getattr(controller, method_name, None)
      else:
        self._raise_fatal_error(msg='No method defined for {0} with parameter {1}'.format(action, parameter))

      if method:
          # TODO: put uuid in options?!?
          # pylint: disable=W0142
          result = method(uuid, **options)
          self._destroy_session()
          # The rest handlers should always give json back!
          if result:
            return result
          else:
            self._raise_fatal_error(msg='Called function returned Noting')
      else:
        self._raise_error('SystemError', msg='Method {0} is not defined for {1}'.format(method_name,
                                                                  controller))
    except RestHandlerException as error:
      return self.__handle_handler_exceptions(error)
