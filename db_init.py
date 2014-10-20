# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""


import os
from sqlalchemy.schema import MetaData

from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.config import Ce1susConfig
from ce1sus.db.classes.event import Event
from ce1sus.db.classes.object import Object
from ce1sus.db.classes.permissions import Group, User, Association
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
  session.close()

