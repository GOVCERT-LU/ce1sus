# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""


from apt_pkg import Group
from datetime import datetime
import os
import sqlalchemy.exc

from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.definitions import AttributeDefinition, ObjectDefinition, AttributeHandler
from ce1sus.db.classes.event import Event
from ce1sus.db.classes.mailtemplate import MailTemplate
from ce1sus.db.classes.object import Object
from ce1sus.db.classes.relation import Relation
from ce1sus.db.classes.types import AttributeViewType, AttributeType
from ce1sus.db.classes.user import User
from ce1sus.db.classes.values import DateValue, StringValue, NumberValue, \
  TextValue
from ce1sus.db.common.session import SessionManager, Base
from ce1sus.helpers.common.config import Configuration


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


if __name__ == '__main__':
  # want parent of parent directory aka ../../
  basePath = os.path.dirname(os.path.abspath(__file__))

  # setup cherrypy
  #
  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  session = SessionManager(config)
  engine = session.connector.get_engine()
  Base.metadata.create_all(engine, checkfirst=True)

  mysql_session = session.connector.get_direct_session()
  session = mysql_session.get_session()

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
  session.add(user)
  try:
    session.flush()
  except sqlalchemy.exc.IntegrityError:
    pass

  mail = MailTemplate()
  mail.name = 'Activation'
  mail.body = 'Mail Body'
  mail.subject = 'User Registration'
  mail.creator = user
  mail.modifier = user
  session.add(mail)
  try:
    session.flush()
  except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
    session.rollback()

  mail = MailTemplate()
  mail.name = 'Update'
  mail.body = 'Mail Body'
  mail.subject = 'Event[${event_id}] ${event_uuid} Updated - ${event_tlp} - ${event_risk} - ${event_title}'
  mail.creator = user
  mail.modifier = user
  session.add(mail)
  try:
    session.flush()
  except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
    session.rollback()

  mail = MailTemplate()
  mail.name = 'Publication'
  mail.body = 'Mail Body'
  mail.subject = 'Event[${event_id}] ${event_uuid} Published - ${event_tlp} - ${event_risk} - ${event_title}'
  mail.creator = user
  mail.modifier = user
  session.add(mail)
  try:
    session.flush()
  except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
    session.rollback()

  mail = MailTemplate()
  mail.name = 'Notification'
  mail.body = 'Mail Body'
  mail.subject = 'Event[${event_id}] ${event_uuid} Notification - ${event_tlp} - ${event_risk} - ${event_title}'
  mail.creator = user
  mail.modifier = user
  session.add(mail)
  try:
    session.flush()
  except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
    session.rollback()

  view_type = AttributeViewType()
  view_type.name = 'Plain'
  view_type.description = 'Used to display the value as plain text'
  session.add(view_type)
  try:
    session.flush()
  except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
    session.rollback()

  view_type = AttributeViewType()
  view_type.name = 'Link'
  view_type.description = 'Used to display the value as a link'
  session.add(view_type)
  try:
    session.flush()
  except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
    session.rollback()

  view_type = AttributeViewType()
  view_type.name = 'Download'
  view_type.description = 'Used to display the value as download'
  session.add(view_type)
  try:
    session.flush()
  except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
    session.rollback()
  session.commit()

  session.close()
