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

from ce1sus.db.classes.internal.object import Object, RelatedObject
from ce1sus.handlers.attributes.filehandler import FileWithHashesHandler
from ce1sus.handlers.base import HandlerException
from ce1sus.helpers.common.hash import hashMD5, fileHashSHA1


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


UUID_EMAIL_CC = '691fa435-8a36-4e44-b7b9-4d039124357a'
UUID_EMAIL_FROM = 'c46a1da5-02bb-4c7f-9193-21b42b4e8503'
UUID_EMAIL_SUBJECT = 'b552af60-63e8-451d-b449-6c4ca443494e'
UUID_EMAIL_SEND_DATE = '23fe3143-f485-4a6e-8ebc-97a2bacb1502'
UUID_EMAIL_MESSAGE_ID = '6d3bdd28-3f65-49a0-a457-679fed08ea53'
UUID_EMAIL_SENDER = 'e8159f74f788076ee14d9614108b1b25654cdaac'
UUID_IN_REPLY_TO = 'fc91cdb4-2aeb-46f2-93ff-fe2b72801df4'
UUID_EMAIL_RAW_BODY = 'd109a7a3-b5e9-4115-834e-927d49d812cf'
UUID_EMAIL_RAW_HEADER = '3c2fe4a0-89d2-4dc4-ad83-0c5581c294aa'
UUID_URL = '8402c5e6-15a6-41c8-b5cc-1a5b1d65ce1c'

UUID_URI = '5fedac23-4915-400c-9179-831ffe0aea2e'



class EmailHandler(FileWithHashesHandler):

  @staticmethod
  def get_uuid():
    return '5665bf50-34d3-11e4-8c21-0800200c9a66'

  @staticmethod
  def get_description():
    return u'File handler with only one hash, used for the average file'

  @staticmethod
  def get_view_type():
    return 'file'

  def attach_attribute(self, obj, definition_uuid, value, json, result):
    if value:
      json['value'] = value
      self.set_attribute_definition(json, definition_uuid)
      attribute = self.create_attribute(obj, json)
      attribute.is_ioc = True
      result.append(attribute)

  def assemble(self, obj, json):
    value = json.get('value', None)
    filename = value.get('name', None)
    data = value.get('data', None)
    if isinstance(data, types.DictionaryType):
      # Workaround for the webfront end
      data = data.get('data', None)

    if filename and data:
      result = list()
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
        self.attach_attribute(obj, UUID_EMAIL_RAW_BODY, raw_body, json, result)

      header = mail.get('header', None)
      send_date = header.get('date', None)
      self.attach_attribute(obj, UUID_EMAIL_SEND_DATE, send_date, json, result)

      from_ = header.get('from', None)
      self.attach_attribute(obj, UUID_EMAIL_FROM, from_, json, result)

      in_reply_to = header.get('in-reply-to', None)
      self.attach_attribute(obj, UUID_IN_REPLY_TO, in_reply_to[1:-1], json, result)

      message_id = header.get('message-id', None)
      self.attach_attribute(obj, UUID_EMAIL_MESSAGE_ID, message_id, json, result)

      subject = header.get('subject', None)
      self.attach_attribute(obj, UUID_EMAIL_SUBJECT, subject, json, result)




      # list
      urls = mail.get('urls')
      for url in urls:
        rel_obj = RelatedObject()
        rel_obj.parent = obj
        rel_obj.parent_id = obj.identifier
        self.set_base(rel_obj, json, obj)

        self.set_object_definition(json, UUID_URI)
        childobj = self.create_object(obj.observable, json)

        rel_obj.object = childobj

        self.attach_attribute(childobj, UUID_URL, url, json, childobj.attributes)
        related_objects.append(rel_obj)
      return result

  @staticmethod
  def get_additional_object_uuids():
    return [UUID_URI] + FileWithHashesHandler.get_additional_object_uuids()

  @staticmethod
  def get_additinal_attribute_uuids():
    return [UUID_EMAIL_CC,
            UUID_EMAIL_FROM,
            UUID_EMAIL_MESSAGE_ID,
            UUID_EMAIL_RAW_BODY,
            UUID_EMAIL_RAW_HEADER,
            UUID_EMAIL_SEND_DATE,
            UUID_EMAIL_SENDER,
            UUID_EMAIL_SUBJECT,
            UUID_IN_REPLY_TO,
            UUID_URL] + FileWithHashesHandler.get_additinal_attribute_uuids()
