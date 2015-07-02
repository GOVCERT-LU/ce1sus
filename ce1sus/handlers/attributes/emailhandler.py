# -*- coding: utf-8 -*-

"""
(Description)

Created on Sep 5, 2014
"""
import base64
from datetime import datetime
from eml_parser.eml_parser import decode_email_s
from os import remove
from os.path import dirname
from shutil import rmtree, move
import types

from ce1sus.db.classes.object import Object, RelatedObject
from ce1sus.handlers.attributes.filehandler import FileWithHashesHandler
from ce1sus.handlers.base import HandlerException
from ce1sus.helpers.common.hash import hashMD5, fileHashSHA1


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


CHK_SUM_EMAIL_CC = 'bb55aa952f379f3daf010d4d8c7851fd85c6a6b1'
CHK_SUM_EMAIL_FROM = '7bbf788e418b7857406d7d0678cc78f1cbb73c44'
CHK_SUM_EMAIL_SUBJECT = 'bb65140f07b14cdd1d0f9221bd4b1a2cad604023'
CHK_SUM_EMAIL_SEND_DATE = 'b17e97d7b9493b35d072c2a17971d748820dc42b'
CHK_SUM_EMAIL_MESSAGE_ID = '42a435968231e7e9f0ba276b4b4171b75499c3fa'
CHK_SUM_EMAIL_SENDER = 'e59877cca12082bdddcfd6298e7e8ec1a32266d0'
CHK_SUM_IN_REPLY_TO = '93925e3261f71a019a75c6b4479d3e984863d5d2'
CHK_SUM_EMAIL_RAW_BODY = 'aaddf3ade1a4448b1128a3098da3aebdd7eeef8c'
CHK_SUM_EMAIL_RAW_HEADER = '750f9e8c90f16e5fd72d38e58282fa26422e6259'
CHK_SUM_URL = 'd326821620e517e9c68b12aa74ce56417e46516d'

CHK_SUM_URI = 'cb371c93c5aa0e62198efd303ae2c17474416d1a'



class EmailHandler(FileWithHashesHandler):

  @staticmethod
  def get_uuid():
    return '5665bf50-34d3-11e4-8c21-0800200c9a66'

  @staticmethod
  def get_description():
    return u'File handler with only one hash, used for the average file'

  def get_view_type(self):
    return 'file'

  def attach_attribute(self, obj, user, definition_chksum, value, json, attributes):
    if value:
      definition = self.get_attriute_definition(definition_chksum)
      json['value'] = value
      attribute = self.create_attribute(obj, definition, user, json)
      attributes.append(attribute)


  def insert(self, obj, user, json):
    value = json.get('value', None)
    filename = value.get('name', None)
    data = value.get('data', None)
    if isinstance(data, types.DictionaryType):
      # Workaround for the webfront end
      data = data.get('data', None)

    if filename and data:
      attributes = list()
      related_objects = list()
      binary_data = base64.b64decode(data)
      # The eml file will not be saved
      mail = decode_email_s(binary_data, include_raw_body=True, include_attachment_data=True)
      # list
      recieved = mail.get('received', None)

      attachments = mail.get('attachments', None)

      raw_body = mail.get('raw_body', None)
      if raw_body:
        raw_body = raw_body[0][1]
        self.attach_attribute(obj, user, CHK_SUM_EMAIL_RAW_BODY, raw_body, json, attributes)

      header = mail.get('header', None)
      send_date = header.get('date', None)
      self.attach_attribute(obj, user, CHK_SUM_EMAIL_SEND_DATE, send_date, json, attributes)

      from_ = header.get('from', None)
      self.attach_attribute(obj, user, CHK_SUM_EMAIL_FROM, from_, json, attributes)

      in_reply_to = header.get('in-reply-to', None)
      self.attach_attribute(obj, user, CHK_SUM_IN_REPLY_TO, in_reply_to[1:-1], json, attributes)

      message_id = header.get('message-id', None)
      self.attach_attribute(obj, user, CHK_SUM_EMAIL_MESSAGE_ID, message_id, json, attributes)

      subject = header.get('subject', None)
      self.attach_attribute(obj, user, CHK_SUM_EMAIL_SUBJECT, subject, json, attributes)

      # list
      urls = mail.get('urls')
      for url in urls:
        rel_obj = RelatedObject()
        rel_obj.parent = obj
        rel_obj.parent_id = obj.identifier
        childobj = self.create_object(obj.observable, self.get_object_definition(CHK_SUM_URI), user, {}, False)
        rel_obj.object = childobj

        self.attach_attribute(childobj, user, CHK_SUM_URL, url, json, childobj.attributes)
        related_objects.append(rel_obj)
      return attributes, related_objects



  def get_additional_object_chksums(self):
    return [CHK_SUM_URI] + FileWithHashesHandler.get_additional_object_chksums(self)

  def get_additinal_attribute_chksums(self):
    return [CHK_SUM_EMAIL_CC,
            CHK_SUM_EMAIL_FROM,
            CHK_SUM_EMAIL_MESSAGE_ID,
            CHK_SUM_EMAIL_RAW_BODY,
            CHK_SUM_EMAIL_RAW_HEADER,
            CHK_SUM_EMAIL_SEND_DATE,
            CHK_SUM_EMAIL_SENDER,
            CHK_SUM_EMAIL_SUBJECT,
            CHK_SUM_IN_REPLY_TO,
            CHK_SUM_URL] + FileWithHashesHandler.get_additinal_attribute_chksums(self)
