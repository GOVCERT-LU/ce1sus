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
from ce1sus.api.restclasses import RestClass, populateClassNamebyDict, getObjectData
from importlib import import_module
import cherrypy
from dagr.web.controllers.base import BaseController
from ce1sus.brokers.event.attributebroker import Attribute
from ce1sus.brokers.event.eventclasses import Event
from ce1sus.brokers.definition.definitionclasses import AttributeDefinition, \
                                                        ObjectDefinition
from dagr.db.broker import NothingFoundException
from dagr.helpers.datumzait import datumzait
from dagr.helpers.converters import ObjectConverter
from ce1sus.helpers.bitdecoder import BitValue
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                                      AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
                                                        ObjectDefinitionBroker
from dagr.helpers.hash import fileHashSHA256, hashMD5, hashSHA256
from ce1sus.web.helpers.handlers.filehandler import FileHandler
import os
from dagr.db.session import SessionManager
from shutil import move
import re


class RestAPIException(Exception):
  """
  Exception base for handler exceptions
  """
  def __init__(self, message):
    Exception.__init__(self, message)


class RestControllerBase(BaseController):

  def __init__(self):
    BaseController.__init__(self)
    self.sessionManager = SessionManager.getInstance()
    self.userBroker = self.brokerFactory(UserBroker)
    self.attributeBroker = self.brokerFactory(AttributeBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)
    self.objectDefinitionBroker = self.brokerFactory(ObjectDefinitionBroker)
    self.attributeDefinitionBroker = self.brokerFactory(
                                                    AttributeDefinitionBroker
                                                       )



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
      Protector.clearRestSession()
      raise RestAPIException(('{0} does not implement '
                              + 'RestClass').format(className))
    return instance

  def _toRestObject(self, obj, isOwner=False):
    className = 'Rest' + obj.__class__.__name__
    instance = RestControllerBase.__instantiateClass(className)

    instance.populate(obj, isOwner)
    return instance

  def _objectToJSON(self, obj, isOwner=False, full=False, withDefinition=False):
    instance = self._toRestObject(obj, isOwner)

    result = dict(instance.toJSON(full=full,
                             withDefinition=withDefinition).items()
                 )
    return result

  def _returnMessage(self, dictionary):
    result = dict(dictionary.items()
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
    raise RestAPIException('{0}: {1}'.format(classname, message))

  def getPostObject(self):
    try:
      cl = cherrypy.request.headers['Content-Length']
      raw = cherrypy.request.body.read(int(cl))
      jsonData = json.loads(raw)
      key, value = getObjectData(jsonData)
      obj = populateClassNamebyDict(key, value, False)
      return obj
    except Exception as e:
      self.getLogger().error('An error occurred by getting the post object {0}', e)
      self.raiseError('UnRecoverableException',
                      'An unrecoverable error occurred')

  def _isEventOwner(self, event, apiKey):
    user = self.getUser(apiKey)
    if user.privileged == 1:
      return True
    else:
      if user.group_id == event.creatorGroup_id:
        return True
      else:
        return False

  def _checkIfViewable(self, event, user):
    """
    Checks if the page if viewable for the given group

    :param grous: A list of strings contrianing the group names
    :type groups: list

    :returns: Boolean
    """
    userDefaultGroup = user.defaultGroup
    # if the user has no default group he has no rights
    if userDefaultGroup is None or not event.published:
      Protector.clearRestSession()
      raise cherrypy.HTTPError(403)
    if (not event.bitValue.isValidated and not event.bitValue.isSharable):
      Protector.clearRestSession()
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
      Protector.clearRestSession()
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
        self.attributeDefinitionBroker.insert(attrDefinition, commit=False)

        # update objectRelations as the attribute was not set
        objectDefinition.attributes.append(attrDefinition)
        self.objectBroker.update(attrDefinition, commit=False)

        self.doCommit(commit)

      return attrDefinition

  def _createAttribute(self,
                        restAttribute,
                        attributeDefinition,
                        obj,
                        commit=False):

    user = obj.creator

    # create the actual attribute
    dbAttribute = Attribute()
    dbAttribute.identifier = None
    # collect definition and check if the handler uses is a filehandler...
    # TODO.
    if (re.match(r'^\{.*file.*:.*\}$', stringValue)):
      try:
        value = json.loads(restAttribute.value)
        jsonFile = value.get('file', None)
        if jsonFile:
          fileName = jsonFile[0]
          strData = jsonFile[1]
          value = strData.decode('base64')
          tmpFolder = '/tmp/' + hashMD5('{0}'.format(datumzait.now()))
          os.mkdir(tmpFolder)
          tmpFolder = tmpFolder + '/{0}'.format(fileName)

          fh = open(tmpFolder, "wb")
          fh.write(value)

          # filename
          destination = FileHandler.getDestination()
          fileHash = fileHashSHA256(tmpFolder)
          fileName = FileHandler.getFileName(fileHash, hashSHA256(fileName))
          destination = destination + '/' + fileName
          move(tmpFolder, destination)
          value = destination
      except:
        value = '(Corrupted File)'
    else:
      value = restAttribute.value
    dbAttribute.value = value
    dbAttribute.object = obj
    dbAttribute.object_id = obj.identifier
    dbAttribute.def_attribute_id = attributeDefinition.identifier
    dbAttribute.definition = attributeDefinition
    dbAttribute.created = datumzait.utcnow()
    dbAttribute.modified = datumzait.utcnow()
    dbAttribute.creator = user
    dbAttribute.creator_id = user.identifier
    dbAttribute.modifier_id = user.identifier
    dbAttribute.modifier = user
    dbAttribute.bitValue = BitValue('0', dbAttribute)
    dbAttribute.bitValue.isRestInsert = True
    dbAttribute.bitValue.isSharable = True
    ObjectConverter.setInteger(dbAttribute,
                               'ioc',
                               restAttribute.ioc)

    self.attributeBroker.insert(dbAttribute, commit=commit)


    return dbAttribute

  def _convertToAttribues(self, restAttributes, obj, commit=False):

    result = list()
    for attribute in restAttributes:
      if attribute.value != '(Not Provided)':
        attrDefinition = self._convertToAttributeDefinition(
                                                         attribute.definition,
                                                         obj.definition,
                                                         commit)
        dbAttribute = self._createAttribute(attribute,
                                           attrDefinition,
                                           obj,
                                           commit)
        result.append(dbAttribute)
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
      objDefinition.share = 1
      self.objectDefinitionBroker.insert(objDefinition, commit=commit)

    return objDefinition

  def _convertToObject(self, restObject, parent, event, commit=False):
    objectDefinition = self._convertToObjectDefinition(restObject.definition,
                                                        commit)

    user = parent.creator
    if isinstance(parent, Event):

      dbObject = self.objectBroker.buildObject(None,
                                               parent,
                                               objectDefinition,
                                               user,
                                               None)
    else:
      dbObject = self.objectBroker.buildObject(None,
                                               None,
                                               objectDefinition,
                                               user,
                                               parent.identifier)
      dbObject.parentEvent_id = event.identifier
    # flush to DB
    dbObject.bitValue.isRestInsert = True
    dbObject.bitValue.isSharable = True
    self.objectBroker.insert(dbObject, commit=commit)

    return dbObject
