# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 2, 2015
"""
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import or_

from ce1sus.db.classes.internal.backend.servers import SyncServer, ServerMode
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, TooManyResultsFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SyncServerBroker(BrokerBase):

  def get_broker_class(self):
    return SyncServer

  def get_server_by_user_id(self, identifier):
    try:
      return self.session.query(SyncServer).filter(SyncServer.user_id == identifier).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(identifier, self.__class__.__name__))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID :{0}'.format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_all_pull_servers(self):
    try:
      sm_pull_only = ServerMode('0')
      sm_pull_only.is_pull = True

      sm_push_pull = ServerMode('0')
      sm_push_pull.is_pull = True
      sm_push_pull.is_push = True

      return self.session.query(SyncServer).filter(or_(SyncServer.mode_code == sm_pull_only.bit_code, SyncServer.mode_code == sm_push_pull.bit_code)).all()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_all_push_servers(self):
    try:
      sm_push_only = ServerMode('0')
      sm_push_only.is_pull = True

      sm_push_pull = ServerMode('0')
      sm_push_pull.is_pull = True
      sm_push_pull.is_push = True

      return self.session.query(SyncServer).filter(or_(SyncServer.mode_code == sm_push_only.bit_code, SyncServer.mode_code == sm_push_pull.bit_code)).all()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
