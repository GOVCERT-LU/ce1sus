# -*- coding: utf-8 -*-

"""
module handing the filehandler

Created: Aug 22, 2013
"""
import base64
from ce1sus.helpers.common.config import ConfigException
import cherrypy
from cherrypy.lib.static import serve_file
from datetime import datetime
import magic
from os import makedirs
from os import remove
from os.path import isfile, getsize, basename, exists, dirname
from shutil import move, rmtree
import types
from uuid import uuid4
import zipfile

from ce1sus.common.utils import can_user_download
from ce1sus.db.classes.internal.common import ValueTable
from ce1sus.db.classes.internal.object import RelatedObject
from ce1sus.handlers.attributes.generichandler import GenericHandler
from ce1sus.handlers.base import HandlerException, HandlerNotFoundException
from ce1sus.helpers.common.hash import hashMD5
import ce1sus.helpers.common.hash as hasher
from types import StringType


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


UUID_FILE_NAME = '31346184-deba-4aa3-9560-210b56479830'
UUID_HASH_SHA1 = '93c7279b-d495-4773-bd73-cb79f88fa338'
UUID_HASH_SHA256 = '778c3f3d-a3bf-4813-b244-a99fe7f39425'
UUID_HASH_SHA384 = '55f2fccc-a3b5-4365-9c94-1e9596b7a038'
UUID_HASH_SHA512 = '3344991a-3bb9-4485-a481-f397879bd971'
UUID_SIZE_IN_BYTES = '96efbf59-2558-4bfc-9abf-1bdedc868d73'
UUID_MAGIC_NUMBER = '08862fef-6984-4035-8607-57ca13d94596'
UUID_MIME_TYPE = 'c8794d22-5ad5-4951-a4d4-4d4bcfaa21f8'
UUID_FILE_ID = 'b1adc377-52a1-4145-b416-cbe52d5118ed'
UUID_HASH_MD5 = '1f1d2bd9-2c58-47ac-8076-c6100cc407ab'
UUID_ARTEFACT = '24aeb5b0-a8fc-4d54-8c78-d33d8b442da1'


class FileHandler(GenericHandler):
  """Handler for handling files"""

  URLSTR = '/events/event/attribute/call_handler_get/{0}/{1}/{2}'

  @staticmethod
  def get_uuid():
    return '0be5e1a0-8dec-11e3-baa8-0800200c9a66'

  @staticmethod
  def get_allowed_types():
    return [ValueTable.STRING_VALUE]

  @staticmethod
  def get_additinal_attribute_uuids():
    return [UUID_FILE_NAME, UUID_HASH_SHA1]

  @staticmethod
  def get_additional_object_uuids():
    return [UUID_ARTEFACT]

  @staticmethod
  def get_description():
    return u'File handler with only one hash, used for the average file'

  @staticmethod
  def get_view_type():
    return 'file'

  @staticmethod
  def require_js():
    return False

  def get_base_path(self):
    """
    Returns the base path for files (as specified in the configuration)
    """
    try:
      config = self.get_config_value('files', None)
      if config:
        return config
      else:
        raise HandlerException(u'Value files in handler configuration for {0} is not set'.format(self.__class__.__name__))
    except ConfigException as error:
      raise HandlerException(error)

  def get_dest_folder(self, rel_folder):
    """
    Returns the destination folder, and creates it when not existing
    """
    try:
      dest_path = self.get_base_path() + '/' + rel_folder
      if not exists(dest_path):
        makedirs(dest_path)
      return dest_path
    except TypeError as error:
      raise HandlerException(error)

  def get_tmp_folder(self):
    """
    Returns the temporary folder, and creates it when not existing
    """
    try:
      tmp_path = self.get_base_path() + '/tmp/' + hasher.hashSHA1('{0}'.format(datetime.utcnow()))
      if not exists(tmp_path):
        makedirs(tmp_path)
      return tmp_path
    except TypeError as error:
      raise HandlerException(error)

  def create_attribute(self, obj, json, main=False):
    attribute = super(FileHandler, self).create_attribute(obj, json)
    if not main:
      attribute.uuid = uuid4()
    return attribute

  def assemble(self, obj, json):
    #check if it is only a file

    value = json.get('value', None)
    if isinstance(value, dict):
      
      filename = value.get('name', None)
      data = value.get('data', None)
      if isinstance(data, types.DictionaryType):
        # Workaround for the webfront end
        data = data.get('data', None)
      result = list()
      if filename and data:
        # save file to tmp folder
        tmp_filename = hashMD5(datetime.utcnow())
        binary_data = base64.b64decode(data)
        tmp_folder = self.get_tmp_folder()
        tmp_path = tmp_folder + '/' + tmp_filename
  
        # create file in tmp
        file_obj = open(tmp_path, "w")
        file_obj.write(binary_data)
        file_obj.close()
  
        sha1 = hasher.fileHashSHA1(tmp_path)
        rel_folder = self.get_rel_folder()
        dest_path = self.get_dest_folder(rel_folder) + '/' + sha1
  
        # move it to the correct place
        move(tmp_path, dest_path)
        # remove temp folder
        rmtree(dirname(tmp_path))
  
        # create attribtues
        internal_json = json
        # main
  
        internal_json['value'] = rel_folder + '/' + sha1
  
        main_attribute = self.create_attribute(obj, internal_json, True)
        # secondary
  
  
        internal_json['value'] = filename
        self.set_attribute_definition(internal_json, UUID_FILE_NAME)
        attribute = self.create_attribute(obj, internal_json)
        result.append(attribute)
  
        internal_json['value'] = sha1
        self.set_attribute_definition(internal_json, UUID_HASH_SHA1)
        attribute = self.create_attribute(obj, internal_json)
        result.append(attribute)
  
  
        self.set_object_definition(internal_json, UUID_ARTEFACT)
        childobj = self.create_object(obj.observable, internal_json)
  
        rel_obj = RelatedObject()
        rel_obj.parent = obj
        rel_obj.parent_id = obj.identifier
        rel_obj.object = childobj
        self.set_base(rel_obj, internal_json, childobj)
        
        main_attribute.object = childobj
        childobj.attributes.append(main_attribute)
        # attributes.append(main_attribute)
  
        result.append(rel_obj)
  
        return result
  
      else:
        raise HandlerException('Value is invalid format has to be {"name": <name>,"data": <base 64 encoded data> }')

    else:
      # is not a file but usable for update
      attribute = self.create_attribute(obj, json)
      return [attribute]

  def get_data(self, attribute, parameters):
    if attribute:
      rel_path = attribute.value
      event = attribute.object.event

      user_can_download = can_user_download(event, self.user)
      if not user_can_download:
        raise cherrypy.HTTPError(status=403, message='User is not permitted to download files')
      base_path = self.get_base_path()
      if base_path and rel_path:
        filepath = base_path + '/' + rel_path
        if isfile(filepath):
          filename = self.__get_orig_filename(attribute)
          # create zipfile
          tmp_path = self.get_base_path()
          if not filename:
            filename = basename(filepath)
          tmp_path += '/' + basename(filepath) + '.zip'
          # remove file if it should exist
          try:
            remove(tmp_path)
          except OSError:
            pass
          # create zip file
          zip_file = zipfile.ZipFile(tmp_path, mode='w')
          # TODO: set password for zip file
          zip_file.write(filepath, arcname=filename)
          zip_file.close()
          filename = u'{0}.zip'.format(filename)
          filename = filename.encode('utf-8')
          result = serve_file(tmp_path, "application/x-download", "attachment", name=filename)
          # clean up
          try:
            remove(tmp_path)
          except OSError:
            pass
          return result
        else:
          raise HandlerNotFoundException('The file was not found in "{0}"'.format(filepath))
      else:
        raise HandlerException('There was an error getting the file')
    else:
      return list()

  @staticmethod
  def _get_dest_filename(file_hash, file_name):
    """
    Returns the file name of the destination
    """
    hashed_file_name = hasher.hashSHA256(file_name)
    key = '{0}{1}{2}'.format(file_hash,
                             datetime.utcnow(),
                             hashed_file_name)
    return hasher.hashSHA256(key)

  @staticmethod
  def get_rel_folder():
    """
    Returns the string of the relative folder position
    """
    dest_path = '{0}/{1}/{2}'.format(datetime.utcnow().year,
                                     datetime.utcnow().month,
                                     datetime.utcnow().day)
    return dest_path

  def __get_orig_filename(self, attribtue):
    """
    Returns the original filename
    """
    # get parent object
    if attribtue.object.parent.parent:
      for attribtue in  attribtue.object.parent.parent.attributes:
        if attribtue.definition.uuid == UUID_FILE_NAME:
          return attribtue.value

      return None


class FileWithHashesHandler(FileHandler):
  """
  Extends the filehandler with additional hashes
  """
  @staticmethod
  def get_uuid():
    return 'e8b47b60-8deb-11e3-baa8-0800200c9a66'

  @staticmethod
  def get_additinal_attribute_uuids():
    return [UUID_FILE_NAME,
            UUID_HASH_SHA1,
            UUID_HASH_SHA256,
            UUID_HASH_SHA384,
            UUID_HASH_SHA512,
            UUID_SIZE_IN_BYTES,
            UUID_MAGIC_NUMBER,
            UUID_MIME_TYPE,
            UUID_FILE_ID,
            UUID_HASH_MD5]

  def assemble(self, obj, json):
    result = super(FileWithHashesHandler, self).assemble(obj, json)
    if len(result) == 1:
      return result

    internal_json = json
    for item in result:
      if isinstance(item, RelatedObject):
        main_attribute = item.object.attributes[0]
        break

    filepath = self.get_base_path() + '/' + main_attribute.value

    # create the remaining attributes
    internal_json['value'] = hasher.fileHashMD5(filepath)
    self.set_attribute_definition(internal_json, UUID_HASH_MD5)
    attribute = self.create_attribute(obj, internal_json)
    attribute.is_ioc = True
    result.append(attribute)

    internal_json['value'] = hasher.fileHashSHA256(filepath)
    self.set_attribute_definition(internal_json, UUID_HASH_SHA256)
    attribute = self.create_attribute(obj, internal_json)
    attribute.is_ioc = True
    result.append(attribute)

    internal_json['value'] = hasher.fileHashSHA384(filepath)
    self.set_attribute_definition(internal_json, UUID_HASH_SHA384)
    attribute = self.create_attribute(obj, internal_json)
    attribute.is_ioc = True
    result.append(attribute)


    internal_json['value'] = hasher.fileHashSHA512(filepath)
    self.set_attribute_definition(internal_json, UUID_HASH_SHA512)
    attribute = self.create_attribute(obj, internal_json)
    attribute.is_ioc = True
    result.append(attribute)

    internal_json['value'] = getsize(filepath)
    self.set_attribute_definition(internal_json, UUID_SIZE_IN_BYTES)
    attribute = self.create_attribute(obj, internal_json)
    result.append(attribute)

    internal_json['value'] = magic.from_file(filepath, mime=True)
    self.set_attribute_definition(internal_json, UUID_MIME_TYPE)
    attribute = self.create_attribute(obj, internal_json)
    result.append(attribute)

    internal_json['value'] = magic.from_file(filepath)
    self.set_attribute_definition(internal_json, UUID_FILE_ID)
    attribute = self.create_attribute(obj, internal_json)
    result.append(attribute)

    return result

  @staticmethod
  def require_js():
    return False
