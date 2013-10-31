# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.helpers.debug import Log
from ce1sus.brokers.permission.userbroker import UserBroker
import json
from ce1sus.api.restclasses import RestClass
from importlib import import_module
import cherrypy
from ce1sus.api.ce1susapi import Ce1susAPI
from dagr.db.session import SessionManager
from dagr.web.controllers.base import BaseController

class RestAPIException(Exception):
  """
  Exception base for handler exceptions
  """
  def __init__(self, message):
    Exception.__init__(self, message)



class RestControllerBase(BaseController):

  def __init__(self):
    BaseController.__init__(self)
    self.userBroker = self.brokerFactory(UserBroker)

  def brokerFactory(self, clazz):
    """
    Instantiates a broker.

    Note: In short sets up the broker in a correct manner with all the
    required settings

    :param clazz: The BrokerClass to be instantiated
    :type clazz: Extension of brokerbase

    :returns: Instance of a broker
    """
    self.logger.debug('Create broker for {0}'.format(clazz))
    return self.sessionManager.brokerFactory(clazz)

  def getUser(self, apiKey):
    """
    Returns the api user

    :returns: User
    """
    if self.userBroker is None:
      self.userBroker = self.brokerFactory(UserBroker)
    user = self.userBroker.getUserByApiKey(apiKey)
    self.getLogger().debug("Returned user")
    return user

  @staticmethod
  def __instantiateClass(className):
    module = import_module('.restclasses', 'ce1sus.api')
    clazz = getattr(module, className)
    # instantiate
    instance = clazz()
    # check if handler base is implemented
    if not isinstance(instance, RestClass):
      raise RestAPIException(('{0} does not implement '
                              + 'RestClass').format(className))
    return instance

  def objectToJSON(self, obj, full=False, withDefinition=False):
    className = 'Rest' + obj.__class__.__name__
    instance = RestControllerBase.__instantiateClass(className)

    instance.populate(obj)

    result = dict(instance.toJSON(full=full,
                             withDefinition=withDefinition).items()
                  + self.createStatus().items())
    return json.dumps(result)

  def createStatus(self, classname=None, message=None):
    result = dict()
    result['response'] = dict()
    result['response']['errors'] = list()
    if (classname is None and message is None):
      result['response']['status'] = 'OK'
    else:
      result['response']['status'] = 'ERROR'
      result['response']['errors'].append({classname: '{0}'.format(message)})
    return result

  def raiseError(self, classname, message):
    temp = dict(self.createStatus(classname, message))
    return json.dumps(temp)

  def getPostObject(self):
    try:
      cl = cherrypy.request.headers['Content-Length']
      raw = cherrypy.request.body.read(int(cl))
      jsonData = json.loads(raw)
      key, value = Ce1susAPI.getObjectData(jsonData)
      obj = Ce1susAPI.populateClassNamebyDict(key, value)
    except Exception as e:
      print e
    return obj
