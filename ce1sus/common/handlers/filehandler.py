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
import base64
import zipfile
from os import remove
import hashlib
from dagr.helpers.strings import convert_to_value

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

  # pylint: disable=R0913
  @staticmethod
  def _create_attribute(value, obj, definition, user, ioc, share=None):
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
    if share:
      params['shared'] = share

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
        # create zipfile
        tmp_path = self._get_base_path()
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
        print type(filename)
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
    """
    Returns the base path for files (as specified in the configuration)
    """
    try:
      return self.config.get('files')
    except ConfigException as error:
      raise HandlerException(error)

  def _get_tmp_folder(self):
    """
    Returns the temporary folder, and creates it when not existing
    """
    try:
      tmp_path = self._get_base_path() + '/tmp/' + hasher.hashSHA1('{0}'.format(DatumZait.now()))
      if not exists(tmp_path):
        makedirs(tmp_path)
      return tmp_path
    except TypeError as error:
      raise HandlerException(error)

  def _get_dest_folder(self, rel_folder):
    """
    Returns the destination folder, and creates it when not existing
    """
    try:
      dest_path = self._get_base_path() + '/' + rel_folder
      if not exists(dest_path):
        makedirs(dest_path)
      return dest_path
    except TypeError as error:
      raise HandlerException(error)

  @staticmethod
  def _get_rel_folder():
    """
    Returns the string of the relative folder position
    """
    dest_path = '{0}/{1}/{2}'.format(DatumZait.now().year,
                                     DatumZait.now().month,
                                     DatumZait.now().day)
    return dest_path

  def _process_file_upload(self, uploaded_file):
    """
    Uploads the file (only used by the GUI)
    """

    filename = uploaded_file.filename.encode('ISO-8859-1')
    if uploaded_file:
      size = 0
      tmp_path = self._get_tmp_folder()
      # TODO: save with sha1
      block_size = 2 ** 20
      hasher = hashlib.sha1()
      while True:
          data = uploaded_file.read(block_size)
          if not data:
              break
          hasher.update(data)
      sha1_str = hasher.hexdigest()

      file_path = u'{0}/{1}'.format(tmp_path, sha1_str)
      file_obj = open(file_path, 'a')
      while True:
        data = uploaded_file.file.read(8192)
        if not data:
          break
        file_obj.write(data)
        size += len(data)
      file_obj.close()
      if size == 0:
        raise HandlerException(u'Upload of the given file failed.')

      return (file_path, filename)
    else:
      raise  HandlerException(u'No file selected. Please try again.')

  @staticmethod
  def _get_definition(chksum, definitions):
    """
    Returns the given definition for the given chksum
    """
    return definitions.get(chksum)

  def insert(self, obj, definitions, user, params):
    """
    Creates ans inserts the file and its attributes (only used by the GUI)
    """
    main_definition = self._get_main_definition(definitions)
    uploaded_file_path, filename = self._process_file_upload(params.get('value', None))

    attributes = list()
    # TODO encode filename
    attributes.append(FileHandler._create_attribute(filename.encode('utf8'),
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

    # return attributes
    return main_attribute, attributes

  def process_gui_post(self, obj, definitions, user, params):
    action = params.get('action')
    if action == 'insert':
      return self.insert(obj, definitions, user, params)

  @staticmethod
  def __get_orig_filename(attribtue):
    """
    Returns the original filename
    """
    for child in attribtue.children:
      if child.definition.chksum == CHK_SUM_FILE_NAME:
        return child.plain_value
    return None

  # pylint: disable=R0201
  def _get_user(self):
    """
    Returns the session user
    """
    # Note this is not as it should be !!
    session = getattr(cherrypy, 'session')
    return session.get(SESSION_USER, None)

  def convert_to_gui_value(self, attribute):
    user = self._get_user()
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
          if not filename:
            filename = basename(file_path)
          return Link(url, u'Download file "{0}"'.format(filename))
        else:
          return '(File is MIA or is corrupt)'
      else:
        return '(Not Provided)'
    else:
      return '(Not Provided)'

  def convert_to_rest_value(self, attribute):
    user = self._get_user()
    if user:
      event = attribute.object.get_parent_event()
      can_download = can_user_download(event, user)
      if can_download:
        file_path = self._get_base_path() + '/' + attribute.plain_value
        if isfile(file_path):
          filename = FileHandler.__get_orig_filename(attribute)
          file_obj = open(file_path, "rb")
          binary_data = file_obj.read()
          file_obj.close()
          b64_encoded = base64.b64encode(binary_data)
          return (filename, b64_encoded)
        else:
          return '(File is MIA or is corrupt)'
      else:
        return '(Not Provided)'
    else:
      return '(Not Provided)'

  # pylint:disable=R0914,W0104
  def process_rest_post(self, obj, definitions, user, dictionary):
    definition = self._get_main_definition(definitions)
    # check if value is valid
    value = dictionary.get('value', list())
    if value:
      value = convert_to_value(value)
    share = dictionary.get('share', '0')
    ioc = dictionary.get('ioc', '0')
    if len(value) != 2:
      raise HandlerException('Value is invalid format has to be ("filename","{base64 encoded file}")')

    # create Params
    params = dict()
    # create and store file
    filename = value[0]
    binary_data = base64.b64decode(value[1])
    tmp_path = self._get_tmp_folder() + '/' + filename
    # create file in tmp
    file_obj = open(tmp_path, "w")
    file_obj.write(binary_data)
    file_obj.close

    sha1 = hasher.fileHashSHA1(tmp_path)
    rel_folder = FileHandler._get_rel_folder()
    dest_path = self._get_dest_folder(rel_folder) + '/' + sha1

    # move it to the correct place
    move(tmp_path, dest_path)
    # remove temp folder
    rmtree(dirname(tmp_path))
    # TODO: do as for the GUI and create all attributes
    params['value'] = rel_folder + '/' + sha1
    params['ioc'] = ioc
    params['shared'] = '{0}'.format(share)

    attribute = self.create_attribute(params, obj, definition, user)
    attributes = list()
    attributes.append(FileHandler._create_attribute(filename,
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_FILE_NAME, definitions),
                                                   user,
                                                   '0'))

    return attribute, attributes


class FileWithHashesHandler(FileHandler):
  """
  Extends the filehandler with additional hashes
  """

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

  def insert(self, obj, definitions, user, params):
    attribute, attributes = FileHandler.insert(self, obj, definitions, user, params)
    filepath = self._get_base_path() + '/' + attribute.plain_value
    attributes.append(FileHandler._create_attribute(hasher.fileHashMD5(filepath),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_HASH_MD5, definitions),
                                                   user,
                                                   '1'))

    attributes.append(FileHandler._create_attribute(hasher.fileHashSHA256(filepath),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_HASH_SHA256, definitions),
                                                   user,
                                                   '1'))

    attributes.append(FileHandler._create_attribute(hasher.fileHashSHA384(filepath),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_HASH_SHA384, definitions),
                                                   user,
                                                   '1'))

    attributes.append(FileHandler._create_attribute(hasher.fileHashSHA512(filepath),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_HASH_SHA512, definitions),
                                                   user,
                                                   '1'))

    attributes.append(FileHandler._create_attribute(getsize(filepath),
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_SIZE_IN_BYTES, definitions),
                                                   user,
                                                   '0'))
    mime_type = magic.from_file(filepath, mime=True)
    if mime_type:
      attributes.append(FileHandler._create_attribute(mime_type,
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_MIME_TYPE, definitions),
                                                   user,
                                                   '0'))

    file_id = magic.from_file(filepath)
    if file_id:
      attributes.append(FileHandler._create_attribute(file_id,
                                                   obj,
                                                   FileHandler._get_definition(CHK_SUM_FILE_ID, definitions),
                                                   user,
                                                   '0'))

    definition = self._get_main_definition(definitions)
    main_attribute = self._create_attribute(attribute.plain_value,
                                                    obj,
                                                    definition,
                                                    user,
                                                    '0')

    # return attributes
    return main_attribute, attributes
