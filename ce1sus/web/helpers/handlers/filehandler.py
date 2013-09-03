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
from ce1sus.brokers.eventbroker import Attribute
from datetime import datetime
from os.path import isfile, basename, getsize, exists
import c17Works.helpers.hash as hasher
from urllib import pathname2url
from mimetypes import MimeTypes
from ce1sus.web.helpers.handlers.base import HandlerException
from ce1sus.brokers.definitionbroker import AttributeDefinitionBroker
from c17Works.web.helpers.config import WebConfig
from shutil import move
from os import makedirs

class FileNotFoundException(HandlerException):
  """File not found Exception"""
  def __init__(self, message):
    HandlerException.__init__(self, message)

class FileHandler(GenericHandler):
  """Handler for handling files"""

  def __init__(self):
    GenericHandler.__init__(self)
    self.def_attributesBroker = self.brokerFactory(AttributeDefinitionBroker)

  def populateAttributes(self, params, obj, definition, user):
    filepath = params.get('value', None)
    if isfile(filepath):
      # getNeededAttributeDefinition
      attributes = list()
      attributes.append(self.__createAttribute(basename(filepath),
                                               obj,
                                               'filename',
                                               user))
      attributes.append(self.__createAttribute(hasher.fileHashMD5(filepath),
                                               obj,
                                               'md5',
                                               user))
      sha1 = self.__createAttribute(hasher.fileHashSHA1(filepath),
                                    obj,
                                    'sha1',
                                    user)
      attributes.append(sha1)
      attributes.append(self.__createAttribute(hasher.fileHashSHA256(filepath),
                                               obj,
                                               'sha256',
                                               user))
      attributes.append(self.__createAttribute(hasher.fileHashSHA384(filepath),
                                               obj,
                                               'sha384',
                                               user))
      attributes.append(self.__createAttribute(hasher.fileHashSHA384(filepath),
                                               obj,
                                               'sha384',
                                               user))
      attributes.append(self.__createAttribute(hasher.fileHashSHA512(filepath),
                                               obj,
                                               'sha512',
                                               user))
      attributes.append(self.__createAttribute('{0} Bytes'.
                                               format(getsize(filepath)),
                                               obj,
                                               'size',
                                               user))
      url = pathname2url(filepath)
      mime = MimeTypes()
      attributes.append(self.__createAttribute(unicode(mime.
                                                       guess_type(url)[0]),
                                               obj,
                                               'mimeType',
                                               user))
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
      attributes.append(self.__createAttribute(destination,
                                               obj,
                                               'location',
                                               user))
      # return attributes
      return attributes
    else:
      raise FileNotFoundException('Could not find file {0}'.format(filepath))

  def __createAttribute(self, value, obj, definitionName, user):
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
    attribute.value = value
    return attribute


  def render(self, enabled, attribute=None):
    template = self.getTemplate('/events/event/attributes/handlers/file.html')
    string = template.render(attribute=attribute, enabled=enabled)
    return string



