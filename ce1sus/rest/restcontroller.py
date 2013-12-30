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
  REST_Allowed_Options = ['Full-Definitions',
                          'page',
                          'limit',
                          'startdate',
                          'enddate',
                          'Object-Type',
                          'Object-Attributes',
                          'attributes',
                          'key',
                          'UUID',
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

  def __checkVersion(self, version):

    try:
      # self.sanityChecker.checkDB()
      # self.sanityChecker.checkRestAPI(version)
      pass
    except SantityCheckerException as e:
      self.raiseError('VersionMismatch', '{0}'.format(e))

  def __checkApiKey(self, apiKey):
    try:
      user = self.getUser(apiKey)
      del user
      exists = True
    except BrokerException as e:
      self.getLogger().debug(e)
      exists = False

    if not exists:
      self.getLogger().debug('Key does not exists')
      Protector.clearRestSession()
      raise cherrypy.HTTPError(403)

    # store key in session
    Protector.setRestSession(apiKey)

  def __getController(self, controllerName):
    if controllerName in self.instances:
      return self.instances[controllerName]
    else:
      self.getLogger().debug(
                        'No instance defined for {0}'.format(controllerName))
      Protector.clearRestSession()
      raise cherrypy.NotFound

  def __checkIfValidUIID(self, string):
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

  def __splitPath(self, vpath):
    # path need at least 2 elements version/controller/....
    if not vpath:
      Protector.clearRestSession()
      raise cherrypy.HTTPError(400)
    controllerName = None
    parameter = None
    uuid = None

    pathElements = list(vpath)

    if (len(pathElements) > 0):
      self.__checkVersion(pathElements[0])

    if (len(pathElements) > 1) and (len(pathElements) < 5):
      controllerName = pathElements[1].strip()
      if (len(pathElements) > 2):
        possibleUUID = pathElements[2]
        if self.__checkIfValidUIID(possibleUUID):
          uuid = possibleUUID.strip()
        else:
          parameter = possibleUUID
          try:
            int(parameter)
            Protector.clearRestSession()
            raise cherrypy.HTTPError(418)
          except ValueError:
            if parameter not in RestController.REST_Allowed_Parameters:
              Protector.clearRestSession()
              self.raiseError('InvalidParameter ',
                              'Parameter {0}'.format(parameter))
        if (len(pathElements) > 3):
          possibleUUID = pathElements[3]
          try:
            if self.__checkIfValidUIID(possibleUUID):
              uuid = possibleUUID.strip()
            else:
              Protector.clearRestSession()
              raise cherrypy.HTTPError(418)
          except ValidationException:
            self.raiseError('InvalidParameter ',
                              'Parameter {0}'.format(parameter))
    else:
      Protector.clearRestSession()
      raise cherrypy.HTTPError(400)

    return controllerName, parameter, uuid

  def __getHeaderValue(self, key):
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

  def __processHeaders(self):
    remoteAddr = self.__getHeaderValue('Remote-Addr')
    self.getLogger().info('Connection from {0}'.format(remoteAddr))

    apiKey = self.__getHeaderValue('key')
    self.__checkApiKey(apiKey)

    # make custom parmeters
    options = dict()
    for key in RestController.REST_Allowed_Options:
      options[key] = self.__getHeaderValue(key)
    return apiKey, options

  @cherrypy.expose
  def default(self, *vpath, **params):
    try:
      # check if the path is correct
      controllerName, parameter, uuid = self.__splitPath(vpath)
      apiKey, options = self.__processHeaders()

      controller = self.__getController(controllerName)

      # getMethodToCall
      action = cherrypy.request.method
      if not action in RestController.REST_mapper:
        self.getLogger().debug(
                          'Action {0} is not defined in mapper'.format(action))
        Protector.clearRestSession()
        raise cherrypy.HTTPError(400)

      if parameter:
        methodName = controller.getFunctionName(parameter, action)
      else:
        methodName = RestController.REST_mapper[action]

      if methodName:
      # call method if existing
        method = getattr(controller, methodName, None)
      else:
        Protector.clearRestSession()
        raise cherrypy.HTTPError(400)

      if method:
        try:
          result = method(uuid, apiKey, **options)
          Protector.clearRestSession()
          # The rest handlers should always give json back!
          if not result:
            raise RestAPIException('Called function returned Noting')
          return result
        except RestAPIException as e:
          self.getLogger().debug(
                          'Error occured during {0} for {1} due to {2}'.format(
                                                                    action,
                                                                    controller,
                                                                    e))
          temp = dict(self._createStatus('RestException', e.message))
          Protector.clearRestSession()
          return json.dumps(temp)
      else:
        self.getLogger().debug(
                          'Method {0} is not defined for {0}'.format(action,
                                                                  controller))
        # if nothing is found do default
        path = request.script_name + request.path_info
        temp = dict(self._createStatus('RestException',
                                       "The path '%s' was not found." % path))
        Protector.clearRestSession()
        return json.dumps(temp)
    except RestAPIException as e:
      self.getLogger().debug(
                    'Error occured during {0}'.format(e))
      temp = dict(self._createStatus('RestException', e.message))
      Protector.clearRestSession()
      return json.dumps(temp)
