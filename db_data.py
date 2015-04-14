# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 13, 2014
"""
from datetime import datetime

from ce1sus.db.classes.definitions import ObjectDefinition, AttributeDefinition
from ce1sus.db.classes.mailtemplate import MailTemplate
from ce1sus.db.classes.user import User
from ce1sus.db.classes.types import AttributeType
from ce1sus.controllers.admin.attributedefinitions import gen_attr_chksum
from ce1sus.db.classes.common import ValueTable
from ce1sus.handlers.attributes.texthandler import TextHandler
from ce1sus.handlers.attributes.multiplegenerichandler import MultipleGenericHandler
from ce1sus.handlers.attributes.emailhandler import EmailHandler
from ce1sus.handlers.attributes.generichandler import GenericHandler
from ce1sus.db.classes.attribute import Condition
from ce1sus.handlers.attributes.datehandler import DateHandler
from ce1sus.handlers.attributes.cbvaluehandler import CBValueHandler
from ce1sus.handlers.attributes.filehandler import FileHandler
from ce1sus.controllers.admin.objectdefinitions import gen_obj_chksum


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def get_users():
  result = list()
  # Add admin user
  user = User()
  user.name = 'Root'
  user.sirname = 'Administrator'
  user.username = 'admin'
  user.password = 'dd94709528bb1c83d08f3088d4043f4742891f4f'
  user.last_login = None
  user.email = 'admin@example.com'
  user.api_key = None
  user.gpg_key = None
  user.activated = datetime.now()
  user.dbcode = 31
  user.activation_sent = None
  user.activation_str = None

  result.append(user)
  return result


def get_mail_templates(user):
  result = list()
  mail = MailTemplate()
  mail.name = 'Publication'
  mail.body = '==============================================\nURL : ${event_url}\nEvent : ${event_uuid}\n==============================================\n'
  mail.body = mail.body + 'Title : ${event_title}\nDate : ${event_created}\nReported by : ${event_reporter}\nRisk : ${event_risk}\nAnalysis : ${event_analysis}\n'
  mail.body = mail.body + 'Description :\n${event_description}\n==============================================\nRelated to :\n${event_relations}\n'
  mail.body = mail.body + '==============================================\nEvent Objects :\n\n\n${event_objects}\n============================================== '
  mail.subject = 'Event[${event_id}] ${event_uuid} Published - ${event_tlp} - ${event_risk} - ${event_title}'
  mail.creator = user
  mail.modifier = user
  result.append(mail)

  mail = MailTemplate()
  mail.name = 'Update'
  mail.body = '==============================================\nURL : ${event_url}\nEvent : ${event_uuid}\n==============================================\n'
  mail.body = mail.body + 'Title : ${event_title}\nDate : ${event_created}\nReported by : ${event_reporter}\nRisk : ${event_risk}\nAnalysis : ${event_analysis}\n'
  mail.body = mail.body + 'Description :\n${event_description}\n==============================================\nRelated to :\n${event_relations}\n'
  mail.body = mail.body + '==============================================\nEvent Objects :\n\n\n${event_objects}\n==============================================\n'
  mail.body = mail.body + '==============================================\nUpdated Relations :\n\${event_updated_relations}\n==============================================\n'
  mail.body = mail.body + 'Updated Objects :\n${event_updated_objects}\n==============================================\nUpdated Objects :\n${event_updated_objects}\n==============================================\n'
  mail.subject = 'Event[${event_id}] ${event_uuid} Updated - ${event_tlp} - ${event_risk} - ${event_title}'
  mail.creator = user
  mail.modifier = user
  result.append(mail)

  mail = MailTemplate()
  mail.name = 'Activation'
  mail.body = 'Welcome to the Ce1sus community. Your user account has been created and has to be activated over the following link:\n\n'
  mail.body = mail.body + '${activation_lin\n\nn\Note: The activation is valid for 24 hours.\n\nThe normal page of the system you can by accessed at the following URL:\n\n'
  mail.body = mail.body + '${ce1sus_url}\n\nYour login credentials are as follow:\n\nUsername: ${username}\n\nPassword: ${password}\n\nTo activate your account please visit the following link\n\n'
  mail.body = mail.body + 'We hope that you find the information contained in our database useful and we’re looking forward to all the valuable information that you’ll be able to share with us.\n\n'
  mail.body = mail.body + 'Please keep in mind that all users and organisations have to conform to the Terms of Use, they are there to make sure that this community works based on trust and that there is fair contribution of validated and valuable data into Ce1sus.\n\n'
  mail.body = mail.body + 'If you run into any issues or have any feedback regarding Ce1sus, don\'t hesitate to contact us at ce1sus@ce1sus.lan\n\n'
  mail.body = mail.body + 'Looking forward to fostering the collaboration between our organisations through your active participation in this information sharing program.\n\n'
  mail.body = mail.body + 'Best Regards,\n\n'
  mail.subject = 'Event[${event_id}] ${event_uuid} Published - ${event_tlp} - ${event_risk} - ${event_title}'
  mail.creator = user
  mail.modifier = user

  result.append(mail)

  return result


def get_attribute_type_definitions():
  attribute_type = AttributeType()
  attribute_type.name = 'None'
  attribute_type.description = 'This type is used when no type has been specified'
  attribute_type.table_id = None

  return {'None': attribute_type}


def get_conditions():
  result = dict()
  condition = Condition()
  condition.value = 'Equals'
  condition.description = 'The value matches 1:1'
  result[condition.value] = condition

  condition = Condition()
  condition.value = 'Like'
  condition.description = 'The value matches the pattern'
  result[condition.value] = condition
  return result


def get_attribute_definitions(user, type_definitions, conditions):
  result = dict()

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'analysis_free_text'
  attribute.description = 'A free text analysis for the object.'
  attribute.table_id = ValueTable.TEXT_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = TextHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'antivirus_record'
  attribute.description = 'The results of one or many antivirus scans for an object. This is a multiline csv value (datetime, engine, result, threat name). '
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'asn'
  attribute.description = 'The asn value specifies an identifier for an autonomous system number.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'ce1sus eml file handler'
  attribute.description = 'EML File handler. This attribute lets you upload an eml file and all the attributes which can be extracted from this file are beeing generated. Note also child objects will be created ofr the attachments.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = EmailHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'code_language'
  attribute.description = 'The code_language field refers to the code language used in the code characterized in this field.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'comment'
  attribute.description = 'Holds free text for comments about objects and event. '
  attribute.table_id = ValueTable.TEXT_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = TextHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'description'
  attribute.description = 'Contains free text description for an object.'
  attribute.table_id = ValueTable.TEXT_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = TextHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'digital_signature'
  attribute.description = 'The Digital_Signatures field is optional and captures one or more digital signatures for the file.'
  attribute.table_id = ValueTable.TEXT_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = TextHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'domain'
  attribute.description = 'Contains a fully qualified domain name'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^(\.|\*\.)?(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_attachment_file_name'
  attribute.description = 'The Attachments field specifies any files that were attached to the email message. It imports and uses the CybOX FileObjectType from the File_Object to do so.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_bcc'
  attribute.description = 'The BCC field specifies the email addresses of any recipients that were included in the blind carbon copy header of the email message.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_cc'
  attribute.description = 'The CC field specifies the email addresses of any recipients that were included in the carbon copy header of the email message.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_content_type'
  attribute.description = 'The Content-Type field specifies the internet media, or MIME, type of the email message content.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_errors_to'
  attribute.description = 'The Errors_To field specifies the entry in the (deprecated) errors_to header of the email message.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_from'
  attribute.description = 'The From field specifies the email address of the sender of the email message. '
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_in_reply_to'
  attribute.description = 'The In_Reply_To field specifies the message ID of the message that this email is a reply to.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_message_id'
  attribute.description = 'The Message_ID field specifies the automatically generated ID of the email message. '
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_mime_version'
  attribute.description = 'The MIME-Version field specifies the version of the MIME formatting used in the email message. '
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_raw_body'
  attribute.description = 'The Raw_Body field specifies the complete (raw) body of the email message.'
  attribute.table_id = ValueTable.TEXT_VALUE
  attribute.regex = '^.+$ '
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = TextHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_raw_header'
  attribute.description = 'The Raw_Header field specifies the complete (raw) headers of the email message.'
  attribute.table_id = ValueTable.TEXT_VALUE
  attribute.regex = '^.+$ '
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = TextHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'email_relay_ip'
  attribute.description = 'This attribute hold the IP address of an MTA used to deliver the mail.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = TextHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_reply_to'
  attribute.description = 'The Reply_To field specifies the email address that should be used when replying to the email message. '
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'email_sender'
  attribute.description = 'The Sender field specifies the email address of the sender who is acting on behalf of the author listed in the From: field '
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_subject'
  attribute.description = 'The Subject field specifies the subject (a brief summary of the message topic) of the email message. '
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_to'
  attribute.description = 'The To field specifies the email addresses of the recipients of the email message. '
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_x_mailer'
  attribute.description = 'The X-Mailer field specifies the software used to send the email message. This field is non-standard.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'email_x_originating_ip'
  attribute.description = 'The X-Originating-IP field specifies the originating IP Address of the email sender, in terms of their connection to the mail server used to send the email message. This field is non-standard.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'encryption_key'
  attribute.description = 'Clear text stings used along with an encryption algorithm in order to cypher data'
  attribute.table_id = ValueTable.TEXT_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = TextHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'encryption_mechanism'
  attribute.description = 'The encryption_mechanism field is optional and specifies the protection/encryption algorithm utilized to protect the Raw_Artifact content.'
  attribute.table_id = ValueTable.TEXT_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = TextHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'encryption_mechanism'
  attribute.description = 'The encryption_mechanism field is optional and specifies the protection/encryption algorithm utilized to protect the Raw_Artifact content.'
  attribute.table_id = ValueTable.TEXT_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = TextHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'file_accessed_datetime'
  attribute.description = 'The Accessed_Time field specifies the date/time the file was last accessed. '
  attribute.table_id = ValueTable.DATE_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = DateHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'file_created_datetime'
  attribute.description = 'The Created_Time field specifies the date/time the file was created.'
  attribute.table_id = ValueTable.DATE_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = DateHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'file_modified_datetime'
  attribute.description = 'The Created_Time field specifies the date/time the file was created.'
  attribute.table_id = ValueTable.DATE_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = DateHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'file_extension'
  attribute.description = 'The File_Extension field specifies the file extension of the file.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'file_format'
  attribute.description = 'The File_Format field specifies the particular file format of the file, most typically specified by a tool such as the UNIX file command.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'file_full_path'
  attribute.description = 'The File path including the file name.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'file_id'
  attribute.description = 'File description as returned by unix "file" command'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'file_modified_time'
  attribute.description = 'The Modified_Time field specifies the date/time the file was last modified.'
  attribute.table_id = ValueTable.DATE_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = DateHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'file_name'
  attribute.description = 'The file_name field specifies the name of the file.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'hash_md5'
  attribute.description = 'md5 hash of a file'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[0-9a-fA-F]{32}'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'hash_sha1'
  attribute.description = 'sha1 hash of a file'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[0-9a-fA-F]{40}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'hash_sha256'
  attribute.description = 'sha256 hash of a file'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[0-9a-fA-F]{64}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'hash_sha384'
  attribute.description = 'sha384 hash of a file'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[0-9a-fA-F]{96}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'hash_sha512'
  attribute.description = 'sha512 hash of a file'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^[0-9a-fA-F]{128}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'hash_ssdeep'
  attribute.description = 'ssdeep hash of a file'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^\d+:[a-zA-Z0-9+]+:[a-zA-Z0-9+]+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'hostname'
  attribute.description = 'Fully qualified domain name'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^(\.|\*\.)?(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,6}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'http_method'
  attribute.description = 'The Hypertext Transfer Protocol (HTTP) identifies the client software originating the request, using a "User-Agent" header, even when the client is not operated by a user.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^GET$|^HEAD$|^POST$|^PUT$|^DELETE$|^TRACE$|^OPTIONS$|^CONNECT$|^PATCH$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = CBValueHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'http_user_agent'
  attribute.description = 'HTTP defines methods (sometimes referred to as verbs) to indicate the desired action to be performed on the identified resource. What this resource represents, whether pre-existing data or data that is generated dynamically, depends on the implementation of the server. Often, the resource corresponds to a file or the output of an executable residing on the server.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'http_version'
  attribute.description = 'HTTP uses a "<major>.<minor>" numbering scheme to indicate versions of the protocol.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^\d+\.\d+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'ip_port'
  attribute.description = 'Port'
  attribute.table_id = ValueTable.NUMBER_VALUE
  attribute.regex = '^[\d]{1,}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'ip_protocol'
  attribute.description = 'IP protocol'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^tcp$|^udp$|^icmp$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = CBValueHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'ipv4_addr'
  attribute.description = 'The IPv4-addr value specifies an IPV4 address.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'ipv4_net'
  attribute.description = 'The IPv4-addr value specifies an IPV4 address.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'ipv6_addr'
  attribute.description = 'The IPv6-addr value specifies an IPv6 address.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'ipv6_net'
  attribute.description = 'IPv6 sub-network'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'magic_number'
  attribute.description = 'The magic_number specifies the particular magic number (typically a hexadecimal constant used to identify a file format) corresponding to the file, if applicable.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'mime_type'
  attribute.description = 'mime_type'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'mutex'
  attribute.description = 'The Mutex object is intended to characterize generic mutual exclusion (mutex) objects.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'named_pipe'
  attribute.description = 'Specifies a named pipe handle.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = True
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'Raw_Artifact'
  attribute.description = 'The raw file data '
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = FileHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = False
  attribute.name = 'raw_document'
  attribute.description = 'The raw document (non malicious file)'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = FileHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'size_in_bytes'
  attribute.description = 'The size_in_bytes field specifies the size of the file, in bytes. '
  attribute.table_id = ValueTable.NUMBER_VALUE
  attribute.regex = '^\d+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'uri'
  attribute.description = 'Holds a complete URL'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'uri_path'
  attribute.description = 'Holds only the path part of an URL. (e.g. /en/index.html)'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = MultipleGenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'targeted_platforms'
  attribute.description = ''
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'processor_family'
  attribute.description = ''
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'discovery_method'
  attribute.description = ''
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'start_address'
  attribute.description = ''
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'username'
  attribute.description = ''
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'password'
  attribute.description = ''
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'full_name'
  attribute.description = ''
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute

  attribute = AttributeDefinition()
  attribute.cybox_std = True
  attribute.name = 'win_registry_key'
  attribute.description = 'The WindowsRegistryObjectType type is intended to characterize Windows registry objects, including Keys and Key/Value pairs.'
  attribute.table_id = ValueTable.STRING_VALUE
  attribute.regex = '^.+$'
  attribute.value_type_id = type_definitions.get('None').identifier
  attribute.relation = False
  attribute.share = False
  attribute.attributehandler_id = GenericHandler.get_uuid()
  attribute.creator = user
  attribute.modifier = user
  attribute.chksum = gen_attr_chksum(attribute)
  attribute.default_condition_id = conditions.get('Equals').identifier

  result[attribute.name] = attribute
  return result


def get_object_definitions(user, attribute_definitions):
  result = dict()

  object_def = ObjectDefinition()
  object_def.name = 'email'
  object_def.description = 'The email object is intended to characterize an individual email message.'
  object_def.default_share = True
  object_def.creator = user
  object_def.modifier = user
  object_def.chksum = gen_obj_chksum(object_def)

  object_def.attributes.append(attribute_definitions['analysis_free_text'])
  object_def.attributes.append(attribute_definitions['comment'])
  object_def.attributes.append(attribute_definitions['email_attachment_file_name'])
  object_def.attributes.append(attribute_definitions['email_bcc'])
  object_def.attributes.append(attribute_definitions['email_cc'])
  object_def.attributes.append(attribute_definitions['email_content_type'])
  object_def.attributes.append(attribute_definitions['email_errors_to'])
  object_def.attributes.append(attribute_definitions['email_from'])
  object_def.attributes.append(attribute_definitions['email_in_reply_to'])
  object_def.attributes.append(attribute_definitions['email_message_id'])
  object_def.attributes.append(attribute_definitions['email_mime_version'])
  object_def.attributes.append(attribute_definitions['email_raw_body'])
  object_def.attributes.append(attribute_definitions['email_raw_header'])
  object_def.attributes.append(attribute_definitions['email_relay_ip'])
  object_def.attributes.append(attribute_definitions['email_sender'])
  object_def.attributes.append(attribute_definitions['email_subject'])
  object_def.attributes.append(attribute_definitions['email_to'])
  object_def.attributes.append(attribute_definitions['email_x_mailer'])
  object_def.attributes.append(attribute_definitions['email_x_originating_ip'])
  object_def.attributes.append(attribute_definitions['hash_md5'])
  object_def.attributes.append(attribute_definitions['hash_sha1'])
  object_def.attributes.append(attribute_definitions['hash_sha256'])
  object_def.attributes.append(attribute_definitions['hash_sha384'])
  object_def.attributes.append(attribute_definitions['hash_sha512'])

  result[object_def.name] = object_def

  object_def = ObjectDefinition()
  object_def.name = 'File'
  object_def.description = 'The File object is intended to characterize generic files.'
  object_def.default_share = True
  object_def.creator = user
  object_def.modifier = user
  object_def.chksum = gen_obj_chksum(object_def)

  object_def.attributes.append(attribute_definitions['analysis_free_text'])
  object_def.attributes.append(attribute_definitions['description'])
  object_def.attributes.append(attribute_definitions['comment'])
  object_def.attributes.append(attribute_definitions['hash_md5'])
  object_def.attributes.append(attribute_definitions['hash_sha1'])
  object_def.attributes.append(attribute_definitions['hash_sha256'])
  object_def.attributes.append(attribute_definitions['hash_sha384'])
  object_def.attributes.append(attribute_definitions['hash_sha512'])
  object_def.attributes.append(attribute_definitions['file_accessed_datetime'])
  object_def.attributes.append(attribute_definitions['file_created_datetime'])
  object_def.attributes.append(attribute_definitions['file_extension'])
  object_def.attributes.append(attribute_definitions['file_format'])
  object_def.attributes.append(attribute_definitions['file_full_path'])
  object_def.attributes.append(attribute_definitions['file_extension'])
  object_def.attributes.append(attribute_definitions['file_id'])
  object_def.attributes.append(attribute_definitions['file_modified_datetime'])
  object_def.attributes.append(attribute_definitions['file_name'])
  object_def.attributes.append(attribute_definitions['magic_number'])
  object_def.attributes.append(attribute_definitions['mime_type'])
  object_def.attributes.append(attribute_definitions['Raw_Artifact'])
  object_def.attributes.append(attribute_definitions['raw_document'])
  object_def.attributes.append(attribute_definitions['size_in_bytes'])

  result[object_def.name] = object_def

  object_def = ObjectDefinition()
  object_def.name = 'File'
  object_def.description = 'The File object is intended to characterize generic files.'
  object_def.default_share = True
  object_def.creator = user
  object_def.modifier = user
  object_def.chksum = gen_obj_chksum(object_def)

  object_def.attributes.append(attribute_definitions['analysis_free_text'])
  object_def.attributes.append(attribute_definitions['description'])
  object_def.attributes.append(attribute_definitions['comment'])
  object_def.attributes.append(attribute_definitions['hash_md5'])
  object_def.attributes.append(attribute_definitions['hash_sha1'])
  object_def.attributes.append(attribute_definitions['hash_sha256'])
  object_def.attributes.append(attribute_definitions['hash_sha384'])
  object_def.attributes.append(attribute_definitions['hash_sha512'])
  object_def.attributes.append(attribute_definitions['file_accessed_datetime'])
  object_def.attributes.append(attribute_definitions['file_created_datetime'])
  object_def.attributes.append(attribute_definitions['file_extension'])
  object_def.attributes.append(attribute_definitions['file_format'])
  object_def.attributes.append(attribute_definitions['file_full_path'])
  object_def.attributes.append(attribute_definitions['file_extension'])
  object_def.attributes.append(attribute_definitions['file_id'])
  object_def.attributes.append(attribute_definitions['file_modified_datetime'])
  object_def.attributes.append(attribute_definitions['file_name'])
  object_def.attributes.append(attribute_definitions['magic_number'])
  object_def.attributes.append(attribute_definitions['mime_type'])
  object_def.attributes.append(attribute_definitions['Raw_Artifact'])
  object_def.attributes.append(attribute_definitions['raw_document'])
  object_def.attributes.append(attribute_definitions['size_in_bytes'])

  result[object_def.name] = object_def

  object_def = ObjectDefinition()
  object_def.name = 'Code'
  object_def.description = 'The Code is intended to characterize a body of computer code.'
  object_def.default_share = True
  object_def.creator = user
  object_def.modifier = user
  object_def.chksum = gen_obj_chksum(object_def)
  object_def.attributes.append(attribute_definitions['code_language'])
  object_def.attributes.append(attribute_definitions['description'])
  object_def.attributes.append(attribute_definitions['targeted_platforms'])
  object_def.attributes.append(attribute_definitions['processor_family'])
  object_def.attributes.append(attribute_definitions['discovery_method'])
  object_def.attributes.append(attribute_definitions['start_address'])

  result[object_def.name] = object_def

  object_def = ObjectDefinition()
  object_def.name = 'UserAccount'
  object_def.description = 'The Code is intended to characterize a body of computer code.'
  object_def.default_share = True
  object_def.creator = user
  object_def.modifier = user
  object_def.chksum = gen_obj_chksum(object_def)
  object_def.attributes.append(attribute_definitions['description'])
  object_def.attributes.append(attribute_definitions['domain'])
  object_def.attributes.append(attribute_definitions['username'])
  object_def.attributes.append(attribute_definitions['password'])
  object_def.attributes.append(attribute_definitions['full_name'])

  result[object_def.name] = object_def

  return result
