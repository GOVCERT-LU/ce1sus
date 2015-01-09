# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 21, 2014
"""


from sqlalchemy.exc import SQLAlchemyError

from ce1sus.db.classes.report import ReferenceDefinition, ReferenceHandler
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, TooManyResultsFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ReferencesBroker(BrokerBase):

  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    return ReferenceDefinition

  def get_all_handlers(self):
    try:
      result = self.session.query(ReferenceHandler)
      return result.all()
    except SQLAlchemyError as error:
      raise BrokerException(error)


class ReferenceDefintionsBroker(BrokerBase):

  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    return ReferenceDefinition
