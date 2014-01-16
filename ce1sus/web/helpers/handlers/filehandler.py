# -*- coding: utf-8 -*-

"""
module handing the filehandler

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


import json
from ce1sus.web.helpers.handlers.generichandler import GenericHandler
from dagr.helpers.datumzait import datumzait
from os.path import isfile, getsize, basename, exists
import dagr.helpers.hash as hasher
from ce1sus.web.helpers.handlers.base import HandlerException
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                              AttributeDefinitionBroker
from dagr.web.helpers.config import WebConfig
from shutil import move
from os import makedirs
from dagr.web.helpers.pagination import Link
from ce1sus.brokers.event.eventbroker import EventBroker
from dagr.db.broker import BrokerException
from ce1sus.web.helpers.protection import Protector
from dagr.helpers.converters import ObjectConverter
from ce1sus.helpers.bitdecoder import BitValue
from ce1sus.brokers.permission.userbroker import UserBroker
import magic
from ce1sus.brokers.event.eventclasses import Attribute
from os.path import isfile
from dagr.web.helpers.config import WebConfig


class FileNotFoundException(HandlerException):
  """File not found Exception"""
  def __init__(self, message):
    HandlerException.__init__(self, message)


class FileHandler(GenericHandler):
  """Handler for handling files"""

  URLSTR = '/events/event/attribute/file/{0}/{1}/{2}'

  def __init__(self):
    GenericHandler.__init__(self)
    self.def_attributesBroker = self.brokerFactory(AttributeDefinitionBroker)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.userBroker = self.brokerFactory(UserBroker)
    self.basePath = WebConfig.getInstance().get('files')

  # pylint: disable=W0211
  @staticmethod
  def getAttributesIDList(self):
    return ('file_name',
            'hash_sha1')

  @staticmethod
  def getFileName(fileHash, fileName):
    hashedFileName = hasher.hashSHA256(fileName)
    svrFileName = '{0}{1}{2}'.format(fileHash,
                                       datumzait.now(),
                                       hashedFileName)
    return hasher.hashSHA256(svrFileName)

  @staticmethod
  def getDestination():
    # move file to destination
    destination = '{0}/{1}/{2}/'.format(datumzait.now().year,
                                                 datumzait.now().month,
                                                 datumzait.now().day)
    return destination

  def populateAttributes(self, params, obj, definition, user):
    filepath = params.get('value', None)
    if isfile(filepath):
      # getNeededAttributeDefinition
      attributes = list()
      attributes.append(self._createAttribute(basename(filepath),
                                               obj,
                                               7,
                                               user,
                                               '1'))
      sha1 = self._createAttribute(hasher.fileHashSHA1(filepath),
                                    obj,
                                    2,
                                    user,
                                    '1')
      # move file to destination
      destination = FileHandler.getDestination()
      # in case the directories doesn't exist
      if not exists(self.basePath + '/' + destination):
        makedirs(self.basePath + '/' + destination)
      # add the name to the file
      destination += sha1.value

      move(filepath, self.basePath + '/' + destination)
      attributes.append(self._createAttribute(destination,
                                               obj,
                                               13,
                                               user,
                                               '0'))
      # return attributes
      return attributes
    else:
      raise FileNotFoundException('Could not find file {0}'.format(filepath))

  # pylint: disable=R0913
  def _createAttribute(self, value, obj, definitionID, user, ioc):
    """
    Creates an attribue obj

    :param value: The value of the obj
    :type value: an atomic value
    :param obj: The obj the attribute belongs to
    :type obj: Object
    :param definitionName: The name of the definition
    :type definitionName: String
    :param user: the user creating the attribute
    :type user: User

    :returns: Attribute
    """
    attribute = Attribute()
    attribute.identifier = None
    attribute.definition = (self.def_attributesBroker.getByID(definitionID))
    attribute.def_attribute_id = attribute.definition.identifier
    attribute.created = datumzait.utcnow()
    attribute.modified = datumzait.utcnow()
    attribute.creator = user
    attribute.creator_id = attribute.creator.identifier
    attribute.modifier = user
    attribute.modifier_id = attribute.modifier.identifier
    attribute.object = obj
    attribute.object_id = attribute.object.identifier
    attribute.value = value.strip()
    ObjectConverter.setInteger(attribute,
                               'ioc',
                               ioc.strip())
    attribute.bitValue = BitValue('0', attribute)
    attribute.bitValue.isWebInsert = True
    attribute.bitValue.isValidated = True
    if attribute.definition.share == 1:
      attribute.bitValue.isSharable = True
    else:
      attribute.bitValue.isSharable = False
    return attribute

  def __canUserDownload(self, eventID, user):
    """
    Checks if the user can download files for the given eventID

    :param eventID: ID of the event
    :type eventID: Intger
    :param user: User
    :type user: User

    :returns: Boolean
    """
    if user.privileged:
      return True
    try:
      event = self.eventBroker.getByID(eventID)

      if event.creatorGroup_id == user.defaultGroup.identifier:
        return True
      else:
        ids = list()
        for group in event.maingroups:
          ids.append(group.identifier)
        if user.defaultGroup.identifier in ids:
          if user.defaultGroup.canDownload:
            return True
        ids = list()
        for group in user.defaultGroup.subgroups:
          ids.append(group.identifier)
        for group in event.groups:
          if group.identifier in ids:
            if group.canDownload:
              return True

    except BrokerException as e:
      self.getLogger().debug(e)

  def render(self, enabled, eventID, user, definition, attribute=None):

    template = self.getTemplate('/events/event/attributes/handlers/file.html')
    try:
      attrID = attribute.identifier
    except  AttributeError:
      attrID = ''
    url = FileHandler.URLSTR.format(eventID,
                                      attrID,
                                      'Download')
    canDownload = False
    if not enabled:
      canDownload = self.__canUserDownload(eventID, user)

    if definition.share:
      defaultShareValue = 1
    else:
      defaultShareValue = 0

    string = template.render(url=url,
                             enabled=enabled,
                             canDownload=canDownload,
                             eventID=eventID,
                             defaultShareValue=defaultShareValue)
    return string

  def convertToAttributeValue(self, value):
    attribute = value.attribute
    user = Protector.getUser()
    restUser = False
    if user is None:
      # check if not a rest user
      apiKey = Protector.getRestAPIKey()
      # if there is a key in the session then the user has logged in via REST
      if apiKey:
        try:
          user = self.userBroker.getUserByApiKey(apiKey)
          restUser = True
        except BrokerException:
          return '(Not Provided)'
      else:
        return '(Not Provided)'

    if not user is None and not restUser:
      eventID = attribute.object.event_id
      if eventID is None:
        eventID = attribute.object.parentEvent_id
      userInGroups = self.__canUserDownload(eventID, user)
      userIsOwner = attribute.creator_id == user.identifier
      filename = self.basePath + '/' + value.value
      if userInGroups or userIsOwner:
        if exists(filename):
          link = Link(FileHandler.URLSTR.format(
                                              attribute.object.identifier,
                                              attribute.identifier,
                                              ''),
                    'Download')
        else:
          return '(File vanished or is corrupt)'
        return link
      else:
        return '(Not Accessible)'
    else:
      if restUser:
        filename = self.basePath + '/' + value.value
        if isfile(filename):
          with open(filename, "rb") as binaryFile:
            data = binaryFile.read()
            binaryASCII = '{0}'.format(data.encode("base64"))
          fileName = basename(filename)
          value = {'file': (fileName, binaryASCII)}
          return json.dumps(value)
        else:
          return '(Not Found)'
      else:
        return '(Not Provided)'


class FileWithHashesHandler(FileHandler):

  def __init__(self):
    FileHandler.__init__(self)

  # pylint: disable=W0211
  @staticmethod
  def getAttributesIDList(self):
    return (7, 1, 2, 3, 4, 5, 8, 9, 88, 111)

  def populateAttributes(self, params, obj, definition, user):
    filepath = params.get('value', None)
    if filepath is None:
      raise FileNotFoundException('No file Uploaded. Upload '
                                  + 'the file before saving')
    if isfile(filepath):
      # getNeededAttributeDefinition
      attributes = list()
      # the beginning
      fileName = basename(filepath)
      attributes.append(self._createAttribute(fileName,
                                               obj,
                                               7,
                                               user,
                                               '1'))
      attributes.append(self._createAttribute(hasher.fileHashMD5(filepath),
                                               obj,
                                               1,
                                               user,
                                               '1'))
      attributes.append(self._createAttribute(hasher.fileHashSHA1(filepath),
                                    obj,
                                    2,
                                    user,
                                    '1'))

      sha256 = self._createAttribute(hasher.fileHashSHA256(filepath),
                                               obj,
                                               3,
                                               user,
                                               '1')
      attributes.append(sha256)
      attributes.append(self._createAttribute(hasher.fileHashSHA384(filepath),
                                               obj,
                                               4,
                                               user,
                                               '1'))
      attributes.append(self._createAttribute(hasher.fileHashSHA512(filepath),
                                               obj,
                                               5,
                                               user,
                                               '1'))
      attributes.append(self._createAttribute('{0}'.
                                               format(getsize(filepath)),
                                               obj,
                                               8,
                                               user,
                                               '0'))

      mimeType = magic.from_file(filepath, mime=True)
      if mimeType:
        attributes.append(self._createAttribute(mimeType,
                                               obj,
                                               88,
                                               user,
                                               '0'))

      fileID = magic.from_file(filepath)
      if fileID:
        attributes.append(self._createAttribute(fileID,
                                               obj,
                                               111,
                                               user,
                                               '0'))

      destination = FileHandler.getDestination()
      if not exists(self.basePath + '/' + destination):
        makedirs(self.basePath + '/' + destination)
      # add the name to the file
      hashedFileName = hasher.hashSHA256(fileName)
      destination += FileHandler.getFileName(sha256.value, hashedFileName)
      move(filepath, self.basePath + '/' + destination)
      attributes.append(self._createAttribute(destination,
                                               obj,
                                               12,
                                               user,
                                               '0'))
      # return attributes
      return attributes
    else:
      raise FileNotFoundException('Could not find file {0}'.format(filepath))
