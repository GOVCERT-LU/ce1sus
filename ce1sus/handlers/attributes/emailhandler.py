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


CHK_SUM_EMAIL_CC = 'bb55aa952f379f3daf010d4d8c7851fd85c6a6b1'
CHK_SUM_EMAIL_FROM = '7bbf788e418b7857406d7d0678cc78f1cbb73c44'
CHK_SUM_EMAIL_SUBJECT = '68f982e660ec08a6a909c195fe2cc320a887a43f'
CHK_SUM_EMAIL_SEND_DATE = '23f2d3c8648bc526b911c618bc539c36cc14cb71'
CHK_SUM_EMAIL_MESSAGE_ID = 'a40a6a928e3a5b8b1965d9de1c90c09e325a2a87'
CHK_SUM_EMAIL_SENDER = '9b05b345fdd81de5cdacab1e17b8a9ec746bab78'


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
