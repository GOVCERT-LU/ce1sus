# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.session import SessionManager
from dagr.helpers.debug import Log
from ce1sus.brokers.permission.userbroker import UserBroker
import json


class RestControllerBase:

  def brokerFactory(self, clazz):
    return SessionManager.brokerFactory(clazz)

  def getLogger(self):
    return Log.getLogger(self.__class__.__name__)

  def getUser(self, apiKey):
    """
    Returns the api user

    :returns: User
    """
    userBroker = self.brokerFactory(UserBroker)
    user = userBroker.getUserByApiKey(apiKey)
    self.getLogger().debug("Returned user")
    return user

  def objectToJSON(self, obj, full=False):
    result = dict(obj.toDict(full).items() + self.createStatus().items())
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
    temp = self.createStatus(classname, message)
    return json.dumps(temp)
