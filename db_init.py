# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""


import os

from ce1sus.db.classes.config import Ce1susConfig
from ce1sus.db.classes.permissions import Group, User
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

  # Add admin user
  user = User()
  user.name = 'Root'
  user.sirname = 'Administrator'
  user.username = 'admin'
  user.spassword = 'admin'
  user.slast_login = None
  user.semail = None
  user.sapi_key = None
  user.sgpg_key = None
  user.sactivated = None
  user.sactivation_sent = None
  user.sactivation_str = None
  session.connector.get_direct_session().get_session().add(user)
  session.close()
