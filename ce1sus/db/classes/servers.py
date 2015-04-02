# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 2, 2015
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode, UnicodeText, Integer, Boolean

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import ServerType
from ce1sus.db.common.session import Base
from ce1sus.helpers.bitdecoder import BitBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ServerMode(BitBase):

  """
  The __bit_value is defined as follows:
  [0] : Is validated
  [1] : Is sharable - On event lvl it has the same meaning as published
  [2] : Is proposal
  """
  # 1
  PULL = 0
  # 2
  PUSH = 1

  @property
  def is_push(self):
    return self._get_value(ServerMode.PULL)

  @is_push.setter
  def is_push(self, value):
    self._set_value(ServerMode.PULL, value)

  @property
  def is_pull(self):
    return self._get_value(ServerMode.PUSH)

  @is_pull.setter
  def is_pull(self, value):
    self._set_value(ServerMode.PUSH, value)


class SyncServer(ExtendedLogingInformations, Base):

  name = Column('name', Unicode(255))
  api_key = Column('apikey', Unicode(255), index=True)
  baseurl = Column('baseurl', Unicode(255), index=True)
  mode_code = Column('mode_id', Integer, index=True)
  type_id = Column('type_id', Integer, index=True)
  description = Column('description', UnicodeText)
  certificat = Column('certificat', UnicodeText)
  ca_certificat = Column('ca_certificat', UnicodeText)
  verify_ssl = Column('verify_ssl', Boolean)

  @property
  def mode(self):
    if self.dbcode:
      self.__bit_code = ServerMode(self.dbcode, self)
    else:
      self.__bit_code = ServerMode('0', self)
    return self.__bit_code

  @mode.setter
  def mode(self, value):
    self.__bit_code = value
    self.dbcode = value.bit_code
    self.__bit_code.parent = self

  @property
  def type(self):
    """
    returns the status

    :returns: String
    """
    return ServerType.get_by_id(self.type_id)

  @type.setter
  def type(self, type_text):
    """
    returns the status

    :returns: String
    """
    self.type_id = ServerType.get_by_value(type_text)
