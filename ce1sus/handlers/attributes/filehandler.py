# -*- coding: utf-8 -*-

"""
module handing the filehandler

Created: Aug 22, 2013
"""
import base64
import cherrypy
from cherrypy.lib.static import serve_file
from datetime import datetime
from os import makedirs
from os import remove
from os.path import isfile, getsize, basename, exists, dirname
from shutil import move, rmtree
import types
import zipfile

from ce1sus.common.checks import can_user_download
from ce1sus.db.classes.common import ValueTable
from ce1sus.handlers.base import HandlerException
from ce1sus.handlers.attributes.generichandler import GenericHandler
from ce1sus.helpers.common.config import ConfigException
from ce1sus.helpers.common.datumzait import DatumZait
from ce1sus.helpers.common.hash import hashMD5
import ce1sus.helpers.common.hash as hasher
import magic


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


CHK_SUM_FILE_NAME = 'beba24a09fe92b09002616e6d703b3a14306fed1'
CHK_SUM_HASH_SHA1 = 'dc4e8dd46d60912abbfc3dd61c16ef1f91414032'
CHK_SUM_HASH_SHA256 = '1350a97f87dfb644437814905cded4a86e58a480'
CHK_SUM_HASH_SHA384 = '40c1ce5808fa21c6a90d27e4b08b7b7171a23b92'
CHK_SUM_HASH_SHA512 = '6d2cf7df2da95b6f878a9be2b754de1e6d1f6224'
CHK_SUM_SIZE_IN_BYTES = '9d99d7a9a888a8bfd0075090c33e6a707625673a'
CHK_SUM_MAGIC_NUMBER = '75f5ca9e1dcfd81cdd03751a7ee45a1ef716a05d'
CHK_SUM_MIME_TYPE = 'b7cc0982923b2a26f8665b44365b590400cff9bf'
CHK_SUM_FILE_ID = '745af7b7cf3bf4c5a0b2b04ad9cd2c9b8da39fc1'
CHK_SUM_HASH_MD5 = '8a3975c871c6df7ab9a890b8f0fd1fb6e4e6556e'


class FileHandler(GenericHandler):
  """Handler for handling files"""

  URLSTR = '/events/event/attribute/call_handler_get/{0}/{1}/{2}'

  @staticmethod
  def get_uuid():
    return '0be5e1a0-8dec-11e3-baa8-0800200c9a66'

  @staticmethod
  def get_allowed_types():
    return [ValueTable.STRING_VALUE]

  def get_additinal_attribute_chksums(self):
    return [CHK_SUM_FILE_NAME, CHK_SUM_HASH_SHA1]

  @staticmethod
  def get_description():
    return u'File handler with only one hash, used for the average file'

  def get_view_type(self):
    return 'file'

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
      tmp_path = self.get_base_path() + '/tmp/' + hasher.hashSHA1('{0}'.format(DatumZait.now()))
      if not exists(tmp_path):
        makedirs(tmp_path)
      return tmp_path
    except TypeError as error:
      raise HandlerException(error)

  def insert(self, obj, user, json):
    value = json.get('value', None)
    filename = value.get('name', None)
    data = value.get('data', None)
    if isinstance(data, types.DictionaryType):
      # Workaround for the webfront end
      data = data.get('data', None)

    if filename and data:
      # save file to tmp folder
      tmp_filename = hashMD5(datetime.utcnow())
      binary_data = base64.b64decode(data)
      tmp_folder = self.get_tmp_folder()
      tmp_path = tmp_folder + '/' + tmp_filename

      # create file in tmp
      file_obj = open(tmp_path, "w")
      file_obj.write(binary_data)
      file_obj.close

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
      main_definition = self.get_main_definition()

      internal_json['value'] = rel_folder + '/' + sha1

      attributes = list()

      main_attribute = self.create_attribute(obj, main_definition, user, internal_json)

      # secondary

      filename_definition = self.get_attriute_definition(CHK_SUM_FILE_NAME)
      internal_json['value'] = filename
      attribute = self.create_attribute(obj, filename_definition, user, internal_json)
      attributes.append(attribute)

      sha1_definition = self.get_attriute_definition(CHK_SUM_HASH_SHA1)
      internal_json['value'] = sha1
      attribute = self.create_attribute(obj, sha1_definition, user, internal_json)
      attributes.append(attribute)

      # set parent
      for attribtue in attributes:
        attribtue.parent = main_attribute

      attributes.append(main_attribute)
      return attributes, None

    else:
      raise HandlerException('Value is invalid format has to be {"name": <name>,"data": <base 64 encoded data> }')

  def update(self, attribute, user, json):
    raise HandlerException('FileHandler does not support updates')

  def get_data(self, attribute, definition, parameters):
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
          raise HandlerException('The file was not found in "{0}"'.format(filepath))
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

  def get_rel_folder(self):
    """
    Returns the string of the relative folder position
    """
    dest_path = '{0}/{1}/{2}'.format(DatumZait.now().year,
                                     DatumZait.now().month,
                                     DatumZait.now().day)
    return dest_path

  def __get_orig_filename(self, attribtue):
    """
    Returns the original filename
    """
    if attribtue.children:
      for child in attribtue.children:
        if child.definition.chksum == CHK_SUM_FILE_NAME:
          return child.plain_value
      # ok no filename has been found using the one from the attribute value
      return basename(attribtue.value)
    else:
      return None


class FileWithHashesHandler(FileHandler):
  """
  Extends the filehandler with additional hashes
  """
  @staticmethod
  def get_uuid():
    return 'e8b47b60-8deb-11e3-baa8-0800200c9a66'

  def get_additinal_attribute_chksums(self):
    return [CHK_SUM_FILE_NAME,
            CHK_SUM_HASH_SHA1,
            CHK_SUM_HASH_SHA256,
            CHK_SUM_HASH_SHA384,
            CHK_SUM_HASH_SHA512,
            CHK_SUM_SIZE_IN_BYTES,
            CHK_SUM_MAGIC_NUMBER,
            CHK_SUM_MIME_TYPE,
            CHK_SUM_FILE_ID,
            CHK_SUM_HASH_MD5]

  def insert(self, obj, user, json):
    attributes, sub_objects = FileHandler(self, obj, user, json)

    internal_json = json
    main_attribute = self.get_main_attribute(attributes)

    filepath = self.get_base_path() + '/' + main_attribute.value

    # create the remaining attributes
    internal_json['value'] = hasher.fileHashMD5(filepath)
    attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_HASH_MD5), user, internal_json)
    attributes.append(attribute)

    internal_json['value'] = hasher.fileHashSHA256(filepath)
    attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_HASH_SHA256), user, internal_json)
    attributes.append(attribute)

    internal_json['value'] = hasher.fileHashSHA384(filepath)
    attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_HASH_SHA384), user, internal_json)
    attributes.append(attribute)

    internal_json['value'] = hasher.fileHashSHA512(filepath)
    attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_HASH_SHA512), user, internal_json)
    attributes.append(attribute)

    internal_json['value'] = getsize(filepath)
    attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_SIZE_IN_BYTES), user, internal_json)
    attributes.append(attribute)

    internal_json['value'] = magic.from_file(filepath, mime=True)
    attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_MIME_TYPE), user, internal_json)
    attributes.append(attribute)

    internal_json['value'] = magic.from_file(filepath)
    attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_FILE_ID), user, internal_json)
    attributes.append(attribute)

    internal_json['value'] = magic.from_file(filepath)
    attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_FILE_ID), user, internal_json)
    attributes.append(attribute)

    # set parent
    for attribtue in attributes:
      attribtue.parent = main_attribute

    return attributes, sub_objects

  def require_js(self):
    return False
