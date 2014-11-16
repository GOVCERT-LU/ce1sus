# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 13, 2014
"""
from datetime import datetime

from ce1sus.db.classes.definitions import ObjectDefinition, AttributeDefinition
from ce1sus.db.classes.mailtemplate import MailTemplate
from ce1sus.db.classes.user import User


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


def get_object_definitions(user):
  result = list()

  object_def = ObjectDefinition()
  object_def.identifier = '0f19ec49-7014-466b-908f-0647e403f054'
  object_def.chksum = 'a88b7dcd1a9e3e17770bbaa6d7515b31a2d7e85d'
  object_def.name = 'email'
  object_def.description = 'email'
  object_def.creator = user
  object_def.modifier = user

  attribute = AttributeDefinition()
  attribute.identifier = 'caba989d-b213-48a2-8363-2fbf005cd8a1'
  attribute.name = 'email'
  attribute.chksum = 'd0f5ee98489d940fbc41a178f2b3d0ded011d360'
  attribute.description = 'email'
  attribute.cybox_std = True
  attribute.table_id = 1
  attribute.regex = '^.+$'
  attribute.value_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.view_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = 'dea62bf0-8deb-11e3-baa8-0800200c9a66'
  attribute.creator = user
  attribute.modifier = user
  object_def.attributes.append(attribute)
  result.append(object_def)

  object_def = ObjectDefinition()
  object_def.identifier = 'cebb031f-f7a4-4cc6-95c9-b0cf39fede98'
  object_def.chksum = '971c419dd609331343dee105fffd0f4608dc0bf2'
  object_def.name = 'file'
  object_def.description = 'file'
  object_def.creator = user
  object_def.modifier = user

  attribute = AttributeDefinition()
  attribute.identifier = 'a0a6c5ec-8d97-44dd-84e0-cd86d8f533cc'
  attribute.name = 'hash_md5'
  attribute.chksum = '6426c35c25e2853e161c29b40bb9359d6368f5ac'
  attribute.description = 'hash_md5'
  attribute.cybox_std = True
  attribute.table_id = 'caba989d-b213-48a2-8363-2fbf005cd8a1'
  attribute.regex = '^.+$'
  attribute.value_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.view_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = 'dea62bf0-8deb-11e3-baa8-0800200c9a66'
  attribute.creator = user
  attribute.modifier = user
  object_def.attributes.append(attribute)

  attribute = AttributeDefinition()
  attribute.identifier = '105de9a1-64d8-4f2f-a2f4-3cd5c0118ece'
  attribute.name = 'hash_sha1'
  attribute.chksum = '750e67e8b7813b868e8f59d2b909b1773465493a'
  attribute.description = 'hash_md5'
  attribute.cybox_std = True
  attribute.table_id = 1
  attribute.regex = '^.+$'
  attribute.value_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.view_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = 'dea62bf0-8deb-11e3-baa8-0800200c9a66'
  attribute.creator = user
  attribute.modifier = user
  object_def.attributes.append(attribute)

  attribute = AttributeDefinition()
  attribute.identifier = '1a5b25fe-e427-4647-bf87-d406c97ed57a'
  attribute.name = 'hash_sha256'
  attribute.chksum = '507e3aaf4fda10e106dc3746e68e1a7e1ae05f51'
  attribute.description = 'hash_md5'
  attribute.cybox_std = True
  attribute.table_id = 1
  attribute.regex = '^.+$'
  attribute.value_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.view_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = 'dea62bf0-8deb-11e3-baa8-0800200c9a66'
  attribute.creator = user
  attribute.modifier = user
  object_def.attributes.append(attribute)

  attribute = AttributeDefinition()
  attribute.identifier = '1a5b25fe-e427-4647-bf87-d406c97ed57ab'
  attribute.name = 'file_name'
  attribute.chksum = '507e3aaf4fda10e106dc3746e68e1a7e1ae05f22'
  attribute.description = 'file_name'
  attribute.cybox_std = True
  attribute.table_id = 1
  attribute.regex = '^.+$'
  attribute.value_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.view_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = 'dea62bf0-8deb-11e3-baa8-0800200c9a66'
  attribute.creator = user
  attribute.modifier = user
  object_def.attributes.append(attribute)
  result.append(object_def)

  object_def = ObjectDefinition()
  object_def.identifier = '43fe36b5-55f4-416e-850c-df39709515d2'
  object_def.chksum = '709381e970d2d669ee1d1b4844a6dde9d9b63c77'
  object_def.name = 'hostname'
  object_def.description = 'hostname'
  object_def.creator = user
  object_def.modifier = user

  attribute = AttributeDefinition()
  attribute.identifier = 'caba989d-b213-48a2-8363-2fbf005cd8a2'
  attribute.name = 'hostname'
  attribute.chksum = 'd0f5ee98489d940fbc41a178f2b3d0ded011d315'
  attribute.description = 'hostname'
  attribute.cybox_std = True
  attribute.table_id = 1
  attribute.regex = '^.+$'
  attribute.value_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.view_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = 'dea62bf0-8deb-11e3-baa8-0800200c9a66'
  attribute.creator = user
  attribute.modifier = user
  object_def.attributes.append(attribute)



  result.append(object_def)

  object_def = ObjectDefinition()
  object_def.identifier = '69cdc198-5d29-4f3d-bf1a-b1a94b4bafa9'
  object_def.chksum = '9120580e94f134cb7c9f27cd1e43dbc82980e152'
  object_def.name = 'domain'
  object_def.description = 'domain'
  object_def.creator = user
  object_def.modifier = user

  attribute = AttributeDefinition()
  attribute.identifier = '924335f6-f396-44c4-844c-e5c22f39ff0f'
  attribute.name = 'domain'
  attribute.chksum = 'c3808d106fbe167f7f7403f59f827d21cdf8df71'
  attribute.description = 'domain'
  attribute.cybox_std = True
  attribute.table_id = 1
  attribute.regex = '^.+$'
  attribute.value_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.view_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = 'dea62bf0-8deb-11e3-baa8-0800200c9a66'
  attribute.creator = user
  attribute.modifier = user
  object_def.attributes.append(attribute)
  result.append(object_def)

  object_def = ObjectDefinition()
  object_def.identifier = 'c818d722-d217-4ce5-8da2-c2c5ce08f75a'
  object_def.chksum = '2c6d680f5c570ba21d22697cd028f230e9f4cd56'
  object_def.name = 'uri'
  object_def.description = 'uri'
  object_def.creator = user
  object_def.modifier = user

  attribute = AttributeDefinition()
  attribute.identifier = '99801f4a-15e1-4a87-9030-fe37879758d9'
  attribute.name = 'url'
  attribute.chksum = '7b9299c7f86cf8d5046b7fda2afc15fd848ddc8d'
  attribute.description = 'email'
  attribute.cybox_std = True
  attribute.table_id = 1
  attribute.regex = '^.+$'
  attribute.value_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.view_type_id = '2fcdfa20-6b19-11e4-9803-0800200c9a66'
  attribute.relation = True
  attribute.share = True
  attribute.attributehandler_id = 'dea62bf0-8deb-11e3-baa8-0800200c9a66'
  attribute.creator = user
  attribute.modifier = user
  object_def.attributes.append(attribute)
  result.append(object_def)

  return result
