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
from ce1sus.rest.restbase import RestControllerBase
from ce1sus.rest.handlers.restobject import RestObjectController
from ce1sus.rest.handlers.restattribute import RestAttributeController
from cherrypy import request


class RestController(RestControllerBase):

  REST_mapper = {'DELETE': 'remove',
       'GET': 'view',
       'POST': 'update',
       'PUT': 'add'}

  def __init__(self, ce1susConfigFile):
    self.instances = dict()
    self.configFile = ce1susConfigFile
    # add instances known to rest
    self.instances['event'] = RestEventController()
    self.instances['object'] = RestObjectController()
    self.instances['attribute'] = RestAttributeController()

  def __checkVersion(self, version):
    sanityChecker = SantityChecker(self.configFile)
    try:
      sanityChecker.checkDB()
      sanityChecker.checkRestAPI(version)
    except SantityCheckerException as e:
      raise cherrypy.HTTPError(500, 'Exception occurred {0}'.format(e))
    finally:
      sanityChecker.close()
      sanityChecker = None

  def __checkApiKey(self, apiKey):
    try:
      user = self.getUser(apiKey)
      del user
      exists = True
    except BrokerException:
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

  @cherrypy.expose
  def default(self, *vpath, **params):
    if not vpath:
      raise cherrypy.HTTPError(500)
    vpath = list(vpath)
    self.__checkVersion(vpath.pop(0))
    apikey = vpath.pop(0)
    self.__checkApiKey(apikey)

    instance = self.__getController(vpath.pop(0))
    identifier = vpath.pop(0)
    action = cherrypy.request.method
    if not action in RestController.REST_mapper:
      self.getLogger().debug(
                        'Action {0} is not defined in mapper'.format(action))
      self.raiseError('Exception',
                      'Action {0} is not defined in mapper'.format(action))
    # call method
    method = getattr(instance, RestController.REST_mapper[action], None)
    if method and getattr(method, "exposed"):
      try:
        return method(identifier, apikey, **params)
      except TypeError as e:
        self.getLogger().debug(
                        'Method {0} is not callable for {1} with {2}'.format(
                                                                        action,
                                                                   instance, e)
                               )
        return self.raiseError('Exception',
                          'Method {0} is not callable for {1} with {2}'.format(
                                                                        action,
                                                                   instance, e)
                               )
    else:
      self.getLogger().debug(
                        'Method {0} is not defined for {0}'.format(action,
                                                                   instance))
      # if nothing is found do default
      path = request.script_name + request.path_info
      self.raiseError('Exception',
                          "The path '%s' was not found." % path)
