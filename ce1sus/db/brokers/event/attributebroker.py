# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
import sqlalchemy

from ce1sus.db.brokers.values import ValueBroker
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.common.broker import BrokerBase, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class AttributeBroker(BrokerBase):


  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Attribute

  def get_all_by_uuids(self, uuids):
    try:
      return self.session.query(Attribute).filter(Attribute.uuid.in_(uuids)).all()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
