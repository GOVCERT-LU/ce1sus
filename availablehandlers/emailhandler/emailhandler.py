# -*- coding: utf-8 -*-

"""
(Description)

Created on Sep 5, 2014
"""
from eml_parser import decode_email
from os.path import dirname
from os import remove
from shutil import rmtree

from ce1sus.common.handlers.base import HandlerException, UndefinedException
from ce1sus.common.handlers.filehandler import FileWithHashesHandler, CHK_SUM_FILE_NAME
from ce1sus.common.handlers.generichandler import GenericHandler
import dagr.helpers.hash as hasher


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


CHK_SUM_EMAIL_CC = 'cdb410fab4a9bb160da0e266e185a8d9109310ff'
CHK_SUM_EMAIL_FROM = '59cf7eefc377bdc51683521b5f340c40a55c9086'
CHK_SUM_EMAIL_SUBJECT = '2ce464780bd3f8c2215849fd883bf236003d2778'
CHK_SUM_EMAIL_SEND_DATE = '3555502fb6a76e5951da4a8fdc3a90173c4da587'
CHK_SUM_GENERIC_FILE = '7a6272431a4546b99081d50797201ddc25a38f4c'
CHK_SUM_RAW_FILE = '03c710c3265fe4488f559ebda358beb63525bda3'
CHK_SUM_EMAIL_MESSAGE_ID = '08d3555ef4c29fe2ad8e5e916dc20fadd2b1a963'


class EmailHandler(GenericHandler):

  def __init__(self, config):
    GenericHandler.__init__(self, config)
    self.file_handler = FileWithHashesHandler(config)

  @staticmethod
  def get_allowed_types():
    return [1]

  @staticmethod
  def get_uuid():
    return '5665bf50-34d3-11e4-8c21-0800200c9a66'

  def render_gui_view(self, template_renderer, attribute, user):
    return self.file_handler.render_gui_view(template_renderer, attribute, user)

  def render_gui_edit(self, template_renderer, attribute, additional_attributes, share_enabled):
    return self.file_handler.render_gui_edit(template_renderer, attribute, additional_attributes, share_enabled)

  def process_gui_post(self, obj, definitions, user, params):
    action = params.get('action', None)
    if action == 'insert':
      uploaded_file_path, filename = self.file_handler._process_file_upload(params.get('value', None))
      del filename
      mail = decode_email(uploaded_file_path, include_attachment_data=True)

      # eml file attribute
      main_definition = self._get_main_definition(definitions)

      # remvoe file
      remove(uploaded_file_path)
      # remove temp folder
      rmtree(dirname(uploaded_file_path))

      attributes = list()
      cc_value = mail.get('cc', None)
      fields = (mail.get('from', None), mail.get('subject', None), cc_value, mail.get('date', None), mail.get('message_id', None))

      # create Email attributes
      if fields[0]:
        main_attribute = FileWithHashesHandler._create_attribute(fields[0],
                                                                 obj,
                                                                 FileWithHashesHandler._get_definition(CHK_SUM_EMAIL_FROM, definitions),
                                                                 user,
                                                                 None,
                                                                 '0')
      if fields[1]:
        attributes.append(FileWithHashesHandler._create_attribute(fields[1],
                                                                  obj,
                                                                  FileWithHashesHandler._get_definition(CHK_SUM_EMAIL_SUBJECT, definitions),
                                                                  user,
                                                                  None,
                                                                  '0'))

      if fields[2]:
        attributes.append(FileWithHashesHandler._create_attribute(fields[2],
                                                                  obj,
                                                                  FileWithHashesHandler._get_definition(CHK_SUM_EMAIL_CC, definitions),
                                                                  user,
                                                                  None,
                                                                  '0'))
      if fields[3]:
        attributes.append(FileWithHashesHandler._create_attribute(fields[3],
                                                                  obj,
                                                                  FileWithHashesHandler._get_definition(CHK_SUM_EMAIL_SEND_DATE, definitions),
                                                                  user,
                                                                  None,
                                                                  '0'))
      if fields[4]:
        attributes.append(FileWithHashesHandler._create_attribute(fields[4],
                                                                  obj,
                                                                  FileWithHashesHandler._get_definition(CHK_SUM_EMAIL_MESSAGE_ID, definitions),
                                                                  user,
                                                                  None,
                                                                  '0'))
      if not (fields[0] and fields[1] and fields[3]):
        raise HandlerException('Invalid eml file, eml file must contain FROM, SUBJECT and DATE')

      obj_def = FileWithHashesHandler._get_definition(CHK_SUM_GENERIC_FILE, definitions)

      """
      Remark:
      The filehandler is used so the definitions required from this one should be removed.
      """
      del definitions[CHK_SUM_EMAIL_CC]
      del definitions[CHK_SUM_EMAIL_FROM]
      del definitions[CHK_SUM_EMAIL_SUBJECT]
      del definitions[CHK_SUM_EMAIL_SEND_DATE]
      del definitions[CHK_SUM_GENERIC_FILE]
      del definitions[CHK_SUM_EMAIL_MESSAGE_ID]
      del definitions[main_definition.chksum]

      # Process attachments
      for attachment_key in mail['attachments']:
        attachment = mail['attachments'].get(attachment_key)
        filename = attachment.get('filename')
        raw_base64 = attachment.get('raw')
        sha1 = attachment.get('hashes').get('sha1')

        # tmp folder
        tmp_folder = self.file_handler._get_tmp_folder()
        file_path = u'{0}/{1}'.format(tmp_folder, sha1)
        file_obj = open(file_path, 'wb')
        file_obj.write(raw_base64.decode('base64'))
        file_obj.close()

        # create New object for this attachment
        child_object = GenericHandler.create_object(obj, obj_def, user, None, '1')
        mainattr, attribs = self.file_handler.insert(child_object, definitions, user, None, params, (filename, file_path))
        mainattr.children = attribs
        child_object.attributes.append(mainattr)
        child_object.attributes = child_object.attributes + attribs

        obj.children.append(child_object)

      return main_attribute, attributes
    elif action == 'update':
      attribute = params.get('attribute', None)
      if attribute:
        raise HandlerException('Not implemented')
      else:
        raise UndefinedException(u'Attribute is not defined')
    else:
      raise UndefinedException(u'Action {0} is not defined'.format(action))

  def convert_to_gui_value(self, attribute):
    return self.file_handler.convert_to_gui_value(attribute)

  def render_gui_get(self, template_renderer, action, attribute, user):
    return self.file_handler.render_gui_get(template_renderer, action, attribute, user)

  def get_additional_object_chksums(self):
    return [CHK_SUM_GENERIC_FILE]

  def get_additinal_attribute_chksums(self):
    return [CHK_SUM_EMAIL_CC,
            CHK_SUM_EMAIL_MESSAGE_ID,
            CHK_SUM_EMAIL_FROM,
            CHK_SUM_EMAIL_SUBJECT,
            CHK_SUM_EMAIL_SEND_DATE,
            CHK_SUM_RAW_FILE] + self.file_handler.get_additinal_attribute_chksums()

  def render_gui_input(self, template_renderer, definition, default_share_value, share_enabled):
    return self.file_handler.render_gui_input(template_renderer, definition, default_share_value, share_enabled)

  def process_rest_post(self, obj, definitions, user, group, dictionary):
    raise HandlerException('Rest part of Emailhandler is not implemented')

  def convert_to_rest_value(self, attribute):
    return self.file_handler.convert_to_rest_value(attribute)
