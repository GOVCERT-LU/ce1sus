# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 31, 2014
"""

import sqlalchemy
from ce1sus.db.common.broker import BrokerBase, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class SearchBroker(BrokerBase):

  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return None

  def look_for_identifier_by_class(self, clazz, needle, operand, bypass_validation=False):
    """
    Searches the tables for a value
    """
    if bypass_validation:
      code = 0
    else:
      code = 1
    try:
      if operand == '==':
        return self.session.query(clazz).filter(clazz.identifier == needle,
                                                clazz.dbcode.op('&')(code) == code
                                                ).all()
      if operand == '<':
        return self.session.query(clazz).filter(clazz.identifier < needle,
                                                clazz.dbcode.op('&')(code) == code
                                                ).all()
      if operand == '>':
        return self.session.query(clazz).filter(clazz.identifier > needle,
                                                clazz.dbcode.op('&')(code) == code
                                                ).all()
      if operand == '<=':
        return self.session.query(clazz).filter(clazz.identifier <= needle,
                                                clazz.dbcode.op('&')(code) == code
                                                ).all()
      if operand == '>=':
        return self.session.query(clazz).filter(clazz.identifier >= needle,
                                                clazz.dbcode.op('&')(code) == code
                                                ).all()
      if operand == 'like':
        return self.session.query(clazz).filter(clazz.identifier.like('%{0}%'.format(needle)),
                                                clazz.dbcode.op('&')(code) == code
                                                ).all()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
