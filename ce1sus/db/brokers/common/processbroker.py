# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 9, 2014
"""
import sqlalchemy.orm.exc

from ce1sus.db.classes.internal.backend.processitem import ProcessItem, ProcessStatus
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ProcessBroker(BrokerBase):

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return ProcessItem

  def get_scheduled_process_items(self):
    try:
      process_id = ProcessStatus.SCHEDULED
      result = self.session.query(ProcessItem).filter(ProcessItem.db_status == process_id)
      return result.all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
