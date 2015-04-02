# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""


from apt_pkg import Group
from datetime import datetime
import os
import sqlalchemy.exc

from ce1sus.db.classes.attribute import Condition
import ce1sus.db.classes.attribute
import ce1sus.db.classes.definitions
import ce1sus.db.classes.event
import ce1sus.db.classes.indicator
import ce1sus.db.classes.mailtemplate
import ce1sus.db.classes.object
import ce1sus.db.classes.observables
import ce1sus.db.classes.relation
import ce1sus.db.classes.report
from ce1sus.db.classes.types import AttributeType
import ce1sus.db.classes.types
from ce1sus.db.classes.user import User
import ce1sus.db.classes.user
import ce1sus.db.classes.values
import ce1sus.db.classes.servers
from ce1sus.db.common.session import SessionManager, Base
from ce1sus.helpers.common.config import Configuration
from db_data import get_mail_templates, get_users, get_object_definitions, get_attribute_type_definitions, get_attribute_definitions, get_conditions
from maintenance import Maintenance
from ce1sus.db.classes.definitions import AttributeDefinition


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

  all_users = get_users()
  users = list()
  for user in all_users:
    session.add(user)
    try:
      session.flush()
      users.append(user)
    except sqlalchemy.exc.IntegrityError:
      try:
        session.rollback()
        existing_user = session.query(User).filter(User.username == user.username).one()
        users.append(existing_user)
      except sqlalchemy.exc.SQLAlchemyError as error:
        pass


  session.commit()
  # Add handlers
  maintenance = Maintenance(config)
  try:
    maintenance.add_handler('availablehandlers/attributes/generichandler/generichandler.py', None)
  except Exception as error:

    pass

  # maintenance.add_handler('availablehandlers/attributes/cbhandler/cbvaluehandler.py', 'CBValueHandler')

  # maintenance.add_handler('availablehandlers/attributes/datehandler/datehandler.py', None)

  # maintenance.add_handler('availablehandlers/attributes/filehandler/filehandler.py', 'FileHandler')

  # maintenance.add_handler('availablehandlers/attributes/filehandler/filehandler.py', 'FileWithHashesHandler')

  # maintenance.add_handler('availablehandlers/attributes/texthandler/texthandler.py', None)
  # maintenance.add_handler('availablehandlers/attributes/multiplehandler/multiplegenerichandler.py', 'MultipleGenericHandler')


  session.commit()
  mail_templates = get_mail_templates(users[0])
  for mail_template in mail_templates:
    session.add(mail_template)
    try:
      session.flush()
    except sqlalchemy.exc.IntegrityError as error:
      print error
      session.rollback()
      pass
  session.commit()


  all_attr_types = get_attribute_type_definitions()
  attr_types = dict()
  for key, value in all_attr_types.iteritems():

    session.add(value)

    try:
      session.flush()
      attr_types[key] = value
    except sqlalchemy.exc.IntegrityError:
      session.rollback()
      existing_type = session.query(AttributeType).filter(AttributeType.name == value.name).one()
      attr_types[key] = existing_type


  session.commit()
  """
  all_conditions = get_conditions()
  conditions = dict()
  for key, value in all_conditions.iteritems():

    session.add(value)

    try:
      session.flush()
      conditions[key] = value
    except sqlalchemy.exc.IntegrityError:
      session.rollback()
      existing = session.query(Condition).filter(Condition.value == value.value).one()
      conditions[key] = existing_type

  session.commit()

  all_attr_definitions = get_attribute_definitions(users[0], attr_types, conditions)
  attr_definitions = dict()
  for key, value in all_attr_definitions.iteritems():

    session.add(value)

    try:
      session.flush()
      attr_definitions[key] = value
    except sqlalchemy.exc.IntegrityError as error:
      session.rollback()
      existing = session.query(AttributeDefinition).filter(AttributeDefinition.name == value.name).one()
      attr_definitions[key] = existing_type

  object_definitions = get_object_definitions(users[0], attr_definitions)
  for key, value in object_definitions.iteritems():
    session.add(value)
    try:
      session.flush()
    except sqlalchemy.exc.IntegrityError:
      session.rollback()
  """
  session.commit()
  session.close()
