# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""


from apt_pkg import Group
from datetime import datetime
import os
import sqlalchemy.exc

import ce1sus.db.classes.attribute
import ce1sus.db.classes.definitions
import ce1sus.db.classes.event
import ce1sus.db.classes.indicator
import ce1sus.db.classes.mailtemplate
import ce1sus.db.classes.object
import ce1sus.db.classes.relation
import ce1sus.db.classes.types
import ce1sus.db.classes.user
import ce1sus.db.classes.values
import ce1sus.db.classes.observables
from ce1sus.db.common.session import SessionManager, Base
from ce1sus.helpers.common.config import Configuration
from db_data import get_mail_templates, get_users


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

  users = get_users()
  for user in users:
    session.add(user)
    try:
      session.flush()
    except sqlalchemy.exc.IntegrityError:
      pass

  mail_templates = get_mail_templates(users[0])
  for mail_template in mail_templates:
    session.add(mail_template)
    try:
      session.flush()
    except sqlalchemy.exc.IntegrityError:
      pass

  view_type = ce1sus.db.classes.types.AttributeViewType()
  view_type.name = 'Link'
  view_type.description = 'Used to display the value as a link'
  session.add(view_type)
  try:
    session.flush()
  except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
    session.rollback()

  view_type = ce1sus.db.classes.types.AttributeViewType()
  view_type.name = 'Download'
  view_type.description = 'Used to display the value as download'
  session.add(view_type)
  try:
    session.flush()
  except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
    session.rollback()
  session.commit()

  session.close()
