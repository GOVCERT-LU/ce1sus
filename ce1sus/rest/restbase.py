# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.brokers.permission.userbroker import UserBroker
import json
from ce1sus.api.restclasses import RestClass
from importlib import import_module
import cherrypy
from ce1sus.api.ce1susapi import Ce1susAPI
from dagr.web.controllers.base import BaseController
from ce1sus.brokers.event.attributebroker import Attribute
from ce1sus.brokers.event.eventclasses import Object, Event
from ce1sus.brokers.definition.definitionclasses import AttributeDefinition, \
                                                        ObjectDefinition
from dagr.db.broker import BrokerException, NothingFoundException
from datetime import datetime
from dagr.helpers.converters import ObjectConverter


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

  def _objectToJSON(self, obj, full=False, withDefinition=False):
    className = 'Rest' + obj.__class__.__name__
    instance = RestControllerBase.__instantiateClass(className)

    instance.populate(obj)

    result = dict(instance.toJSON(full=full,
                             withDefinition=withDefinition).items()
                  + self._createStatus().items())
    return json.dumps(result)

  def _createStatus(self, classname=None, message=None):
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
    temp = dict(self._createStatus(classname, message))
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

  def _checkIfViewable(self, event, user):
    """
    Checks if the page if viewable for the given group

    :param grous: A list of strings contrianing the group names
    :type groups: list

    :returns: Boolean
    """
    userDefaultGroup = user.defaultGroup
    # if the user has no default group he has no rights
    if userDefaultGroup is None:
      raise cherrypy.HTTPError(403)
    self.getLogger().debug("Checked if it is viewable for user {0}".format(
                                                                  user.username
                                                                  )
                           )
    # check is the group of the user is the creation group
    result = event.creatorGroup.identifier == userDefaultGroup.identifier
    if not result:
      # check tlp
      result = event.tlp.identifier >= userDefaultGroup.tlpLvl
      # check if the user belong to one of the common maingroups
      if not result:
          result = userDefaultGroup in event.maingroups
      # check if the user belong to one of the common groups
      if not result:
        groups = user.defaultGroup.subgroups
        for group in event.groups:
          if group in groups:
              result = True
              break
    if not result:
      raise cherrypy.HTTPError(403)

    return result

  def _convertToAttributeDefinition(self,
                                   restAttributeDefinition,
                                   objectDefinition,
                                   commit=False):
    # get definition if existing
      try:
        attrDefinition = self.attributeDefinitionBroker.getDefintionByCHKSUM(
                                                restAttributeDefinition.chksum
                                                                            )
      except NothingFoundException:
        # definition does not exist create one
        attrDefinition = AttributeDefinition()
        attrDefinition.name = restAttributeDefinition.name
        attrDefinition.description = restAttributeDefinition.description
        attrDefinition.regex = restAttributeDefinition.regex
        attrDefinition.classIndex = restAttributeDefinition.classIndex
        attrDefinition.handlerIndex = 0
        attrDefinition.deletable = 1
        attrDefinition.share = 1
        attrDefinition.relation = restAttributeDefinition.relation
        self.attributeDefinitionBroker.insert(attrDefinition, commit=False)

        # update objectRelations as the attribute was not set
        objectDefinition.attributes.append(attrDefinition)
        self.objectBroker.update(attrDefinition, commit=False)

        self.doCommit(commit)

      return attrDefinition

  def _createAttribute(self,
                        restAttribute,
                        attributeDefinition,
                        object,
                        commit=False):

    user = object.creator

    # create the actual attribute
    dbAttribute = Attribute()
    dbAttribute.identifier = None
    dbAttribute.value = restAttribute.value
    dbAttribute.object = object
    dbAttribute.object_id = object.identifier
    dbAttribute.def_attribute_id = attributeDefinition.identifier
    dbAttribute.definition = attributeDefinition
    dbAttribute.created = datetime.now()
    dbAttribute.modified = datetime.now()
    dbAttribute.creator = user
    dbAttribute.creator_id = user.identifier
    dbAttribute.modifier_id = user.identifier
    dbAttribute.modifier = user
    ObjectConverter.setInteger(dbAttribute,
                               'ioc',
                               restAttribute.ioc)

    self.attributeBroker.insert(dbAttribute, commit=False)

    return dbAttribute

  def _convertToAttribues(self, restAttributes, obj, commit=False):

    result = list()
    for attribute in restAttributes:
      if attribute.value != '(Not Provided)':
        attrDefinition = self._convertToAttributeDefinition(
                                                         attribute.definition,
                                                         obj.definition,
                                                         False)
        dbAttribute = self._createAttribute(attribute,
                                           attrDefinition,
                                           obj,
                                           False)
        result.append(dbAttribute)
    self.attributeBroker.doCommit(commit)
    return result

  def _convertToObjectDefinition(self, restObjectDefinition, commit=False):
    # create object

    # get definition if existing
    try:
      objDefinition = self.objectDefinitionBroker.getDefintionByCHKSUM(
                                                    restObjectDefinition.chksum
                                                                      )
    except NothingFoundException:
      objDefinition = ObjectDefinition()
      objDefinition.name = restObjectDefinition.name
      objDefinition.description = restObjectDefinition.description
      self.objectDefinitionBroker.insert(objDefinition, commit=commit)

    return objDefinition

  def _convertToObject(self, restObject, event, commit=False):
    objectDefinition = self._convertToObjectDefinition(restObject.definition,
                                                        commit)
    user = event.creator

    if restObject.parentObject_id is None:
      dbObject = self.objectBroker.buildObject(None,
                                               event,
                                               objectDefinition,
                                               user,
                                               None)
    else:
      dbObject = self.objectBroker.buildObject(None,
                                               None,
                                               objectDefinition,
                                               user,
                                               restObject.parentObject_id)
    # flush to DB
    self.objectBroker.insert(dbObject, commit=False)

    return dbObject