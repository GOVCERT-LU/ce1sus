# -*- coding: utf-8 -*-

"""
module handing the filehandler

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.views.base import SESSION_USER
from cherrypy.lib.static import serve_file
from dagr.helpers.config import ConfigException
import cherrypy
from ce1sus.common.handlers.generichandler import GenericHandler
from dagr.helpers.datumzait import DatumZait
from os.path import isfile, getsize, basename, exists, dirname
import dagr.helpers.hash as hasher
from ce1sus.common.handlers.base import HandlerException
from shutil import move, rmtree
from os import makedirs
import magic
from ce1sus.common.checks import can_user_download
from dagr.web.views.classes import Link


CHK_SUM_FILE_NAME = '3cee6f0639b390eb6952496314f3551150a88ca4'
CHK_SUM_HASH_SHA1 = 'c5934731c516906196e46828817bc71f508f87f8'
CHK_SUM_HASH_SHA256 = '8634ac3d7ac1a262d27b537d8c6930e275a06acf'
CHK_SUM_HASH_SHA384 = '4bce656ce662f02504de215f0cc26cb808baefd3'
CHK_SUM_HASH_SHA512 = 'cdcb0d09007a2d4e74a3d363bf43c0dd989ac84b'
CHK_SUM_SIZE_IN_BYTES = 'e03dbcfce5cc727ed71e653b7960f9c7fa54cf21'
CHK_SUM_MAGIC_NUMBER = '8f461f462e17197751d242c0a0a827fda624d559'
CHK_SUM_MIME_TYPE = '86529a68c89c9f78be7120da9a5dd5f4a96abe85'
CHK_SUM_FILE_ID = 'e81cdce63d1c4fd020c929b2ff91da92f5ce14c3'
CHK_SUM_HASH_MD5 = 'fed503f9b506cf9636497f5423aef9e68a1bd107'


class FileHandler(GenericHandler):
  """Handler for handling files"""

  URLSTR = '/events/event/attribute/call_handler_get/{0}/{1}/{2}'

  def get_additinal_attribute_chksums(self):
    return [CHK_SUM_FILE_NAME, CHK_SUM_HASH_SHA1]

  @staticmethod
  def _get_dest_filename(file_hash, file_name):
    """
    Returns the file name of the destination
    """
    hashed_file_name = hasher.hashSHA256(file_name)
    key = '{0}{1}{2}'.format(file_hash,
                                     DatumZait.now(),
                                     hashed_file_name)
    return hasher.hashSHA256(key)

  @staticmethod
  def _create_attribute(value, obj, definition, user, ioc):
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
    params = dict()
    params['value'] = value
    params['ioc'] = ioc

    return GenericHandler.create_attribute(params,
                                           obj,
                                           definition,
                                           user)

  def render_gui_input(self, template_renderer, definition, default_share_value, share_enabled):
    return template_renderer('/common/handlers/file.html',
                             url='',
                             can_download=False,
                             event_id=0,
                             enabled=True,
                             default_share_value=default_share_value,
                             enable_share=share_enabled)

  def render_gui_get(self, template_renderer, action, attribute, user):
    rel_path = attribute.plain_value
    event = attribute.object.get_parent_event()
    user_can_download = can_user_download(event, user)
    if not user_can_download:
      raise cherrypy.HTTPError(403)
    base_path = self._get_base_path()
    if base_path and rel_path:
      filepath = base_path + '/' + rel_path
      if isfile(filepath):
        filename = FileHandler.__get_orig_filename(attribute)
        return serve_file(filepath, "application/x-download", "attachment", name=filename)
      else:
        raise  HandlerException('The was not found in "{0}"'.format(filepath))
    else:
      raise  HandlerException('There was an error getting the file')

  def render_gui_view(self, template_renderer, attribute, user):
    event = attribute.object.get_parent_event()
    user_can_download = can_user_download(event, user)
    if not user_can_download:
      raise cherrypy.HTTPError(403)
    url_str = '/events/event/attribute/call_handler_get/{0}/{1}/{2}'
    url = url_str.format('download',
                         event.identifier,
                         attribute.identifier)

    return template_renderer('/common/handlers/file.html',
                             url=url,
                             can_download=user_can_download,
                             event_id=event.identifier,
                             enabled=False,
                             default_share_value=0,
                             enable_share=False)

  def _get_base_path(self):
    try:
      return self.config.get('files')
    except ConfigException as error:
      raise HandlerException(error)

  def _get_tmp_folder(self):
    try:
      tmp_path = self._get_base_path() + '/tmp/' + hasher.hashSHA1('{0}'.format(DatumZait.now()))
      if not exists(tmp_path):
        makedirs(tmp_path)
      return tmp_path
    except TypeError as error:
      raise HandlerException(error)

  def _get_dest_folder(self, rel_folder):
    try:
      dest_path = self._get_base_path() + '/' + rel_folder
      if not exists(dest_path):
        makedirs(dest_path)
      return dest_path
    except TypeError as error:
      raise HandlerException(error)

  @staticmethod
  def _get_rel_folder():
    dest_path = '{0}/{1}/{2}'.format(DatumZait.now().year,
                                     DatumZait.now().month,
                                     DatumZait.now().day)
    return dest_path

  def _process_file_upload(self, uploaded_file):
    if uploaded_file:
      size = 0
      tmp_path = self._get_tmp_folder()
      file_path = tmp_path + '/' + uploaded_file.filename
      file_obj = open(file_path, 'a')
      while True:
        data = uploaded_file.file.read(8192)
        if not data:
          break
        file_obj.write(data)
        size += len(data)
      file_obj.close()
      if size == 0:
        raise HandlerException('Upload of the given file failed.')
      return file_path
    else:
      raise  HandlerException('No file selected. Please try again.')

  @staticmethod
  def _get_definition(chksum, definitions):
    return definitions.get(chksum)

  def insert(self, obj, definitions, user, params):
    main_definition = self._get_main_definition(definitions)
    uploaded_file_path = self._process_file_upload(params.get('value', None))

    attributes = list()
    attributes.append(FileHandler._create_attribute(basename(uploaded_file_path),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_FILE_NAME, definitions),
                                                   user,
                                                   '0'))
    sha1 = hasher.fileHashSHA1(uploaded_file_path)
    attributes.append(FileHandler._create_attribute(sha1,
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_HASH_SHA1, definitions),
                                                   user,
                                                   '0'))

    rel_folder = FileHandler._get_rel_folder()
    dest_path = self._get_dest_folder(rel_folder) + '/' + sha1
    move(uploaded_file_path, dest_path)

    # remove temp folder
    rmtree(dirname(uploaded_file_path))

    main_attribute = FileHandler._create_attribute(rel_folder + '/' + sha1,
                                                    obj,
                                                    main_definition,
                                                    user,
                                                    '0')
    attributes.append(main_attribute)

    # return attributes
    return main_attribute, attributes

  def process_gui_post(self, obj, definitions, user, params):
    action = params.get('action')
    if action == 'insert':
      return self.insert(obj, definitions, user, params)

  @staticmethod
  def __get_orig_filename(attribtue):
    for child in attribtue.children:
      if child.definition.chksum == CHK_SUM_FILE_NAME:
        return child.plain_value
    return None

  def convert_to_gui_value(self, attribute):
    # Note this is not as it should be !!
    session = getattr(cherrypy, 'session')
    user = session.get(SESSION_USER, None)
    if user:
      event = attribute.object.get_parent_event()
      can_download = can_user_download(event, user)
      if can_download:
        file_path = self._get_base_path() + '/' + attribute.plain_value
        if isfile(file_path):
          url = FileHandler.URLSTR.format('download',
                                          attribute.object.get_parent_event_id(),
                                          attribute.identifier)
          filename = FileHandler.__get_orig_filename(attribute)
          return Link(url, 'Download file "{0}"'.format(filename))
        else:
          return '(File is MIA or is corrupt)'
      else:
        return '(Not Provided)'
    else:
      return '(Not Provided)'


class FileWithHashesHandler(FileHandler):

  @staticmethod
  def get_additinal_attribute_chksums():
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

  def insert(self, obj, definitions, user, params):
    main_definition = self._get_main_definition(definitions)
    uploaded_file_path = self._process_file_upload(params.get('value', None))

    attributes = list()
    attributes.append(FileHandler._create_attribute(basename(uploaded_file_path),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_FILE_NAME, definitions),
                                                   user,
                                                   '0'))
    sha1 = hasher.fileHashSHA1(uploaded_file_path)
    attributes.append(FileHandler._create_attribute(sha1,
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_HASH_SHA1, definitions),
                                                   user,
                                                   '1'))

    attributes.append(FileHandler._create_attribute(hasher.fileHashMD5(uploaded_file_path),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_HASH_MD5, definitions),
                                                   user,
                                                   '1'))

    attributes.append(FileHandler._create_attribute(hasher.fileHashSHA256(uploaded_file_path),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_HASH_SHA256, definitions),
                                                   user,
                                                   '1'))

    attributes.append(FileHandler._create_attribute(hasher.fileHashSHA384(uploaded_file_path),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_HASH_SHA384, definitions),
                                                   user,
                                                   '1'))

    attributes.append(FileHandler._create_attribute(hasher.fileHashSHA512(uploaded_file_path),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_HASH_SHA512, definitions),
                                                   user,
                                                   '1'))

    attributes.append(FileHandler._create_attribute(getsize(uploaded_file_path),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_SIZE_IN_BYTES, definitions),
                                                   user,
                                                   '0'))
    mime_type = magic.from_file(uploaded_file_path, mime=True)
    if mime_type:
      attributes.append(FileHandler._create_attribute(mime_type,
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_MIME_TYPE, definitions),
                                                   user,
                                                   '0'))

    file_id = magic.from_file(uploaded_file_path)
    if file_id:
      attributes.append(FileHandler._create_attribute(file_id,
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_FILE_ID, definitions),
                                                   user,
                                                   '0'))

    rel_folder = FileHandler._get_rel_folder()
    dest_path = self._get_dest_folder(rel_folder) + '/' + sha1
    move(uploaded_file_path, dest_path)

    # remove temp folder
    rmtree(dirname(uploaded_file_path))

    main_attribute = self._create_attribute(rel_folder + '/' + sha1,
                                                    obj,
                                                    main_definition,
                                                    user,
                                                    '0')
    attributes.append(main_attribute)

    # return attributes
    return main_attribute, attributes
