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
from os import makedirs
from os import remove
from os.path import isfile, basename, exists, dirname
from shutil import move, rmtree
import types
import zipfile

from ce1sus.common.checks import can_user_download
from ce1sus.db.classes.internal.common import ValueTable
from ce1sus.handlers.base import HandlerException
from ce1sus.handlers.references.generichandler import GenericHandler
from ce1sus.helpers.common.hash import hashMD5
import ce1sus.helpers.common.hash as hasher


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


CHK_SUM_FILE_NAME = '2234969e-1e72-4dfb-9f8e-fe08d02bef1d'


class FileReferenceHandler(GenericHandler):
  """Handler for handling files"""

  URLSTR = '/events/event/attribute/call_handler_get/{0}/{1}/{2}'

  @staticmethod
  def get_uuid():
    return '0be5e1a0-8dec-11e3-baa8-0800200c9a66'

  @staticmethod
  def get_allowed_types():
    return [ValueTable.STRING_VALUE]

  @staticmethod
  def get_description():
    return u'File handler with only one hash, used for the average file'

  @staticmethod
  def get_view_type():
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
      tmp_path = self.get_base_path() + '/tmp/' + hasher.hashSHA1('{0}'.format(datetime.utcnow()))
      if not exists(tmp_path):
        makedirs(tmp_path)
      return tmp_path
    except TypeError as error:
      raise HandlerException(error)

  def assemble(self, report, json):
    value = json.get('value', None)
    filename = value.get('filename', None)
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

      internal_json['value'] = rel_folder + '/' + sha1 + '|' + filename
      main_attribute = self.create_reference(report, internal_json)

      return [main_attribute]

    else:
      raise HandlerException('Value is invalid format has to be {"filename": <filename>,"data": <base 64 encoded data> } but was ' + '{0}'.format(value))

  def get_data(self, reference, definition, parameters):
    if reference:
      splitted = reference.value.split('|')

      rel_path = splitted[0]
      filename = splitted[1]
      event = reference.report.event

      user_can_download = can_user_download(event, self.user)
      if not user_can_download:
        raise cherrypy.HTTPError(status=403, message='User is not permitted to download files')
      base_path = self.get_base_path()
      if base_path and rel_path:
        filepath = base_path + '/' + rel_path
        if isfile(filepath):
                    # create zipfile
          tmp_path = self.get_base_path()

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

  @staticmethod
  def get_rel_folder():
    """
    Returns the string of the relative folder position
    """
    dest_path = '{0}/{1}/{2}'.format(datetime.utcnow().year,
                                     datetime.utcnow().month,
                                     datetime.utcnow().day)
    return dest_path

  @staticmethod
  def require_js():
    return False
