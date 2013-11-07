# -*- coding: utf-8 -*-

"""
module handing the filehandler

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.web.helpers.handlers.generichandler import GenericHandler
from ce1sus.brokers.event.attributebroker import Attribute
from datetime import datetime
from os.path import isfile, basename, getsize, exists
import dagr.helpers.hash as hasher
from urllib import pathname2url
from mimetypes import MimeTypes
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

  # pylint: disable=W0211
  @staticmethod
  def getAttributesNameList(self):
    return ('filename',
            'md5',
            'sha1',
            'sha256',
            'sha384',
            'sha512',
            'size',
            'mimeType',
            'location')

  def populateAttributes(self, params, obj, definition, user):
    filepath = params.get('value', None)
    if isfile(filepath):
      # getNeededAttributeDefinition
      attributes = list()
      attributes.append(self._createAttribute(basename(filepath),
                                               obj,
                                               'filename',
                                               user,
                                               '1'))
      sha1 = self._createAttribute(hasher.fileHashSHA1(filepath),
                                    obj,
                                    'sha1',
                                    user,
                                    '1')
      # move file to destination
      destination = '{0}/{1}/{2}/{3}/'.format(WebConfig.
                                              getInstance().get('files'),
                                                 datetime.now().year,
                                                 datetime.now().month,
                                                 datetime.now().day)
      # in case the directories doesn't exist
      if not exists(destination):
        makedirs(destination)
      # add the name to the file
      destination += sha1.value
      move(filepath, destination)
      attributes.append(self._createAttribute(destination,
                                               obj,
                                               'File (UnMalicious)',
                                               user,
                                               '0'))
      # return attributes
      return attributes
    else:
      raise FileNotFoundException('Could not find file {0}'.format(filepath))

  def _createAttribute(self, value, obj, definitionName, user, ioc):
    """
    Creates an attribue object

    :param value: The value of the object
    :type value: an atomic value
    :param obj: The object the attribute belongs to
    :type obj: Object
    :param definitionName: The name of the definition
    :type definitionName: String
    :param user: the user creating the attribute
    :type user: User

    :returns: Attribute
    """
    attribute = Attribute()
    attribute.identifier = None
    attribute.definition = (self.def_attributesBroker.
                                      getDefintionByName(definitionName))
    attribute.def_attribute_id = attribute.definition.identifier
    attribute.created = datetime.now()
    attribute.modified = datetime.now()
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
    canDownload = False
    if user.privileged:
      return True
    try:
      event = self.eventBroker.getByID(eventID)

      if event.creator.identifier == user.identifier:
        canDownload = True
      else:
        if user.defaultgroup in event.maingroups:
          return True
        for group in event.groups:
          if group in user.groups:
            if group.canDownload:
              canDownload = True
              break

    except BrokerException as e:
      self.getLogger().debug(e)
      canDownload = False
    return canDownload

  def render(self, enabled, eventID, user, attribute=None):

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

    string = template.render(url=url,
                             enabled=enabled,
                             canDownload=canDownload,
                             eventID=eventID
                             )
    return string

  def convertToAttributeValue(self, value):
    attribute = value.attribute
    user = Protector.getUser()
    if user is None:
      return '(Not Provided)'
    else:
      eventID = attribute.object.event_id
      if eventID is None:
        eventID = attribute.object.parentEvent_id
      userInGroups = self.__canUserDownload(eventID, user)
      userIsOwner = attribute.creator_id == user.identifier
      if userInGroups or userIsOwner:
        link = Link(FileHandler.URLSTR.format(
                                              attribute.object.identifier,
                                              attribute.identifier,
                                              ''),
                    'Download')
        return link
      else:
        return '(Not Accessible)'


class FileWithHashesHandler(FileHandler):

  def __init__(self):
    FileHandler.__init__(self)

  def populateAttributes(self, params, obj, definition, user):
    filepath = params.get('value', None)
    if isfile(filepath):
      # getNeededAttributeDefinition
      attributes = list()
      # TODO: Use IDs instead of names as the attributes are fixed due to
      # the beginning
      attributes.append(self._createAttribute(basename(filepath),
                                               obj,
                                               'filename',
                                               user,
                                               '1'))
      attributes.append(self._createAttribute(hasher.fileHashMD5(filepath),
                                               obj,
                                               'md5',
                                               user,
                                               '1'))
      sha1 = self._createAttribute(hasher.fileHashSHA1(filepath),
                                    obj,
                                    'sha1',
                                    user,
                                    '1')
      attributes.append(sha1)
      attributes.append(self._createAttribute(hasher.fileHashSHA256(filepath),
                                               obj,
                                               'sha256',
                                               user,
                                               '1'))
      attributes.append(self._createAttribute(hasher.fileHashSHA384(filepath),
                                               obj,
                                               'sha384',
                                               user,
                                               '1'))
      attributes.append(self._createAttribute(hasher.fileHashSHA512(filepath),
                                               obj,
                                               'sha512',
                                               user,
                                               '1'))
      attributes.append(self._createAttribute('{0}'.
                                               format(getsize(filepath)),
                                               obj,
                                               'size',
                                               user,
                                               '0'))
      url = pathname2url(filepath)
      mime = MimeTypes()
      attributes.append(self._createAttribute(unicode(mime.
                                                       guess_type(url)[0]),
                                               obj,
                                               'mimeType',
                                               user,
                                               '0'))
      # move file to destination
      destination = '{0}/{1}/{2}/{3}/'.format(WebConfig.
                                              getInstance().get('files'),
                                                 datetime.now().year,
                                                 datetime.now().month,
                                                 datetime.now().day)
      # in case the directories doesn't exist
      if not exists(destination):
        makedirs(destination)
      # add the name to the file
      destination += sha1.value
      move(filepath, destination)
      attributes.append(self._createAttribute(destination,
                                               obj,
                                               'File (Malicious)',
                                               user,
                                               '0'))
      # return attributes
      return attributes
    else:
      raise FileNotFoundException('Could not find file {0}'.format(filepath))

