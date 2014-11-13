# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import or_, and_, not_, distinct

from ce1sus.db.classes.event import Event
from ce1sus.db.classes.object import Object
from ce1sus.db.common.broker import BrokerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class ObjectBroker(BrokerBase):
  """
  This broker handles all operations on event objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Object
