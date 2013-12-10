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
from dagr.helpers.converters import ValueConverter
import re


class RestController(RestControllerBase):

  REST_mapper = {'DELETE': 'remove',
       'GET': 'view',
       'POST': 'update'}

  REST_Allowed_Parameters = ['metadata', 'attributes', 'events']
  REST_Allowed_Options = ['Full-Definitions',
                          'page',
                          'limit',
                          'startdate',
                          'enddate',
                          'Object-Type',
                          'Object-Attributes',
                          'attributes',
                          'key',
                          'UUID']
  def __init__(self, ce1susConfigFile):
    RestControllerBase.__init__(self)
    self.configFile = ce1susConfigFile

    self.instances = dict()
    # add instances known to rest
    self.instances['event'] = RestEventController()
    self.instances['events'] = RestEventsController()
    self.instances['search'] = RestSearchController()
    self.sanityChecker = SantityChecker(self.configFile)

  def __checkVersion(self, version):

    try:
      self.sanityChecker.checkDB()
      self.sanityChecker.checkRestAPI(version)
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
      raise cherrypy.HTTPError(403)

  def __getController(self, controllerName):
    if controllerName in self.instances:
      return self.instances[controllerName]
    else:
      self.getLogger().debug(
                        'No instance defined for {0}'.format(controllerName))
      raise cherrypy.NotFound

  def __checkIfValidUIID(self, string):
    regex = r'^[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$'
    return ValueValidator.validateRegex(string,
                                        regex,
                                        'Not a valid UUID')

  def __splitPath(self, vpath):
    # path need at least 2 elements version/controller/....
    if not vpath:
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
            raise cherrypy.HTTPError(418)
          except ValueError:
            if parameter not in RestController.REST_Allowed_Parameters:
              raise cherrypy.HTTPError(418)
        if (len(pathElements) > 3):
          if self.__checkIfValidUIID(pathElements[3]):
            uuid = possibleUUID.strip()
          else:
            raise cherrypy.HTTPError(418)
    else:
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
      if re.match(r'^\[.*\]', value, re.MULTILINE) is not None:
        return eval(value)
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
        raise cherrypy.HTTPError(400)

      if parameter:
        methodName = controller.getFunctionName(parameter, action)
      else:
        methodName = RestController.REST_mapper[action]

      if methodName:
      # call method if existing
        method = getattr(controller, methodName, None)
      else:
        raise cherrypy.HTTPError(400)

      if method:
        try:
          result = method(uuid, apiKey, **options)
          return result
        except RestAPIException as e:
          self.getLogger().debug(
                          'Error occured during {0} for {1} due to {2}'.format(
                                                                     action,
                                                                     controller,
                                                                     e))
          temp = dict(self._createStatus('RestException', e.message))
          return json.dumps(temp)
      else:
        self.getLogger().debug(
                          'Method {0} is not defined for {0}'.format(action,
                                                                     controller))
        # if nothing is found do default
        path = request.script_name + request.path_info
        temp = dict(self._createStatus('RestException',
                                       "The path '%s' was not found." % path))
        return json.dumps(temp)
    except RestAPIException as e:
          self.getLogger().debug(
                          'Error occured during {0}'.format(e))
          temp = dict(self._createStatus('RestException', e.message))
          return json.dumps(temp)
