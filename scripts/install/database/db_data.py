# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 13, 2014
"""
from datetime import datetime

from ce1sus.db.classes.mailtemplate import MailTemplate
from ce1sus.db.classes.user import User
from ce1sus.db.classes.types import AttributeType
from ce1sus.db.classes.attribute import Condition
from ce1sus.helpers.common.hash import hashSHA1


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def get_users(config):
  salt = config.get('ce1sus', 'salt')

  result = list()
  # Add admin user
  user = User()
  user.identifier = 1
  user.uuid = 'f49eb0ed-438d-49ef-aa19-1d615a3ba01d'
  user.name = 'Root'
  user.sirname = 'Administrator'
  user.username = 'admin'
  user.password = hashSHA1('admin' + salt)
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
  mail.identifier = 1
  mail.uuid = 'fa6ac2c1-f504-4820-affe-d724f4817af9'
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
  mail.identifier = 2
  mail.name = 'Update'
  mail.uuid = '36f5e3f9-7b54-4191-8f07-a20b8cf2fcb0'
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
  mail.identifier = 3
  mail.name = 'Activation'
  mail.uuid = '5c0cf7a9-7337-47f9-bb48-ff291a1ee1c6'
  mail.body = 'Welcome to the Ce1sus community. Your user account has been created and has to be activated over the following link:\n\n'
  mail.body = mail.body + '${activation_link}\n\nNote: The activation is valid for 24 hours.\n\nThe normal page of the system you can by accessed at the following URL:\n\n'
  mail.body = mail.body + '${ce1sus_url}\n\nYour login credentials are as follow:\n\nUsername: ${username}\n\nPassword: ${password}\n\nTo activate your account please visit the following link\n\n'
  mail.body = mail.body + 'We hope that you find the information contained in our database useful and we\'re looking forward to all the valuable information that you\'ll be able to share with us.\n\n'
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
  attribute_type.identifier = 1
  attribute_type.name = 'None'
  attribute_type.uuid = 'a47fef10-298c-4731-8480-320cb34989c1'
  attribute_type.description = 'This type is used when no type has been specified'
  attribute_type.table_id = None

  return {attribute_type.uuid: attribute_type}


def get_conditions():
  result = dict()
  condition = Condition()
  condition.identifier = 1
  condition.uuid = '00dba852-7e1f-48b5-834b-5722c7d13190'
  condition.value = 'Equals'
  condition.description = 'The value matches 1:1'
  result[condition.uuid] = condition

  condition = Condition()
  condition.value = 'FitsPattern'
  condition.identifier = 2
  condition.uuid = '0d34e1d1-d716-4bbd-bda5-9a611d798cdc'
  condition.description = 'The value matches the pattern'
  result[condition.uuid] = condition
  return result
