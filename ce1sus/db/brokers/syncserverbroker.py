# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 2, 2015
"""
import sqlalchemy.orm.exc

from ce1sus.db.classes.servers import SyncServer
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, TooManyResultsFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SyncServerBroker(BrokerBase):

  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    return SyncServer

  def get_server_by_user_id(self, identifier):
    try:
      return self.session.query(self.get_broker_class()).filter(SyncServer.user_id == identifier).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(identifier, self.__class__.__name__))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID :{0}'.format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
