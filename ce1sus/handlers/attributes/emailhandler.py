# -*- coding: utf-8 -*-

"""
(Description)

Created on Sep 5, 2014
"""
import base64
from datetime import datetime
from eml_parser.eml_parser import decode_email
from os import remove
from os.path import dirname
from shutil import rmtree
import types

from ce1sus.db.classes.object import Object
from ce1sus.handlers.base import HandlerException
from ce1sus.handlers.attributes.filehandler import FileWithHashesHandler
from ce1sus.helpers.common.hash import hashMD5


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


class EmailHandler(FileWithHashesHandler):

  @staticmethod
  def get_uuid():
    return '5665bf50-34d3-11e4-8c21-0800200c9a66'

  @staticmethod
  def get_description():
    return u'File handler with only one hash, used for the average file'

  def get_view_type(self):
    return 'file'

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

      mail = decode_email(tmp_path, include_attachment_data=True)
      # remove unused files
      remove(tmp_path)
      rmtree(dirname(tmp_path))

      attributes = list()
      cc_value = mail.get('cc', None)
      fields = (mail.get('from', None),
                mail.get('subject', None),
                cc_value,
                mail.get('date', None),
                mail.get('message_id', None)
                )

      attributes = list()
      internal_json = json

      if not (fields[0] and fields[1] and fields[3]):
        raise HandlerException('Invalid eml file, eml file must contain FROM, SUBJECT and DATE')

      # create Email attributes
      if fields[0]:
        internal_json['value'] = fields[0]
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_EMAIL_FROM), self.user, internal_json)
        attributes.append(attribute)

      if fields[1]:
        internal_json['value'] = fields[1]
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_EMAIL_SUBJECT), self.user, internal_json)
        attributes.append(attribute)

      if fields[2]:
        internal_json['value'] = fields[2]
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_EMAIL_CC), self.user, internal_json)
        attributes.append(attribute)

      if fields[3]:
        internal_json['value'] = fields[3]
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_EMAIL_SEND_DATE), self.user, internal_json)
        attributes.append(attribute)

      if fields[4]:
        internal_json['value'] = fields[4]
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_EMAIL_MESSAGE_ID), self.user, internal_json)
        attributes.append(attribute)

      obj_definition = self.get_object_definition(CHK_SUM_GENERIC_FILE)

      child_objects = list()
      # Process attachments
      for attachment_key in mail['attachments']:
        attachment = mail['attachments'].get(attachment_key)
        filename = attachment.get('filename')
        raw_base64 = attachment.get('raw')

        # create New object for this attachment
        child_object = Object()
        child_object.definition = obj_definition
        child_object.definition_id = obj_definition.identifier

        value_dict = {'name': filename, 'data': raw_base64}
        internal_json['value'] = value_dict

        file_attributes, sub_objects = FileWithHashesHandler.insert(self, obj, self.user, internal_json)

        file_main_attribute = self.get_main_attribute(file_attributes)

        file_main_attribute.children = file_attributes

        child_object.attributes.append(file_main_attribute)
        child_object.attributes = child_object.attributes + file_attributes

        child_objects.append(child_object)

      return attributes, child_objects

  def get_additional_object_chksums(self):
    return [CHK_SUM_GENERIC_FILE]

  def get_additinal_attribute_chksums(self):
    return [CHK_SUM_EMAIL_CC,
            CHK_SUM_EMAIL_MESSAGE_ID,
            CHK_SUM_EMAIL_FROM,
            CHK_SUM_EMAIL_SUBJECT,
            CHK_SUM_EMAIL_SEND_DATE,
            CHK_SUM_RAW_FILE] + self.file_handler.get_additinal_attribute_chksums()
