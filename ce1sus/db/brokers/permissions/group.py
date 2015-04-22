# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""
import sqlalchemy.orm.exc

from ce1sus.db.classes.group import Group
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, TooManyResultsFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class GroupBroker(BrokerBase):
  """This is the interface between python an the database"""

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Group

  def get_by_name(self, name):
    try:

      result = self.session.query(Group).filter(Group.name == name).one()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with name :{0}'.format(name))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for name :{0}'.format(name))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_all_notifiable_groups(self):
    try:
      result = self.session.query(Group).filter(Group.notifications == 1, Group.email != None).all()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'No notifiable users found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
