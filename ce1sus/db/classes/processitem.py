# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 8, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, BigInteger, Unicode

from ce1sus.db.classes.basedbobject import SimpleLogingInformations
from ce1sus.db.classes.common import StaticBase
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ProcessStatus(StaticBase):

  SCHEDULED = u'Scheduled'
  MARKED = u'Marked'
  PROCESSING = u'Processing'
  FINISHED = u'Finished'
  FAILED = u'Failed'
  CANCELLED = u'Cancelled'

  @classmethod
  def get_dictionary(cls):
    return {0: ProcessStatus.SCHEDULED,
            1: ProcessStatus.MARKED,
            2: ProcessStatus.PROCESSING,
            3: ProcessStatus.FINISHED,
            4: ProcessStatus.FAILED,
            5: ProcessStatus.CANCELLED}


class ProcessType(StaticBase):

  PULL = u'Pull'
  PUSH = u'Push'
  PUBLISH = u'Publish'
  RELATIONS = u'Relations'

  TYPES = [PULL, PUSH, PUBLISH, RELATIONS]

  @classmethod
  def get_dictionary(cls):
    return {0: ProcessType.PULL,
            1: ProcessType.PUSH,
            2: ProcessType.PUBLISH,
            3: ProcessType.RELATIONS,
            }


class ProcessItem(SimpleLogingInformations, Base):

  db_status = Column('status', Integer, nullable=False, index=True, default=0)
  db_type = Column('type', Integer, nullable=False)
  event_uuid = Column('event_uuid', Unicode(40), index=True)
  server_details_id = Column('syncserver_id', BigInteger, ForeignKey('syncservers.syncserver_id', onupdate='cascade', ondelete='cascade'))
  server_details = relationship('SyncServer', uselist=False, primaryjoin='ProcessItem.server_details_id==SyncServer.identifier')

  @property
  def status(self):
    return ProcessStatus.get_by_id(self.db_status)

  @status.setter
  def status(self, text):
    """
    returns the status

    :returns: String
    """
    self.db_status = ProcessStatus.get_by_value(text)

  def next_step(self):
    self.db_status = self.db_type + 1

  @property
  def type_(self):
    return ProcessType.get_by_id(self.db_type)

  @type_.setter
  def type_(self, text):
    """
    returns the status

    :returns: String
    """
    self.db_type = ProcessType.get_by_value(text)

  def validate(self):
    # TODO: validation
    return True

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'status': self.convert_value(self.status),
            'type_': self.convert_value(self.type_),
            'event_uuid': self.convert_value(self.event_uuid),
            'server_details_id': self.convert_value(self.server_details_id),
            'server_details': self.server_details.to_dict(True, False)
            }
