# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 13, 2014
"""
from datetime import datetime

from ce1sus.db.classes.mailtemplate import MailTemplate
from ce1sus.db.classes.user import User
from ce1sus.db.classes.definitions import ObjectDefinition


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


def get_object_definitions():
  result = list()

  object_def = ObjectDefinition()
  object_def.chksum = 'a88b7dcd1a9e3e17770bbaa6d7515b31a2d7e85d'
  object.name = 'email'
  object.description = 'email'
  result.append()

  return result
