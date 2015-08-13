# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 2, 2015
"""
from ce1sus.helpers.bitdecoder import BitBase
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Boolean

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.common import ServerType
from ce1sus.db.classes.internal.core import ExtendedLogingInformations, BigIntegerType, UnicodeType, UnicodeTextType, BaseObject
from ce1sus.db.common.session import Base


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

  def to_dict(self, cache_object):
    return {'is_pull': self.is_pull,
            'is_push': self.is_push
            }


class SyncServer(ExtendedLogingInformations, Base):

  name = Column('name', UnicodeType(255), unique=True)
  user_id = Column('user_id', BigIntegerType, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), index=True)
  user = relationship('User', primaryjoin='SyncServer.user_id==User.identifier')
  baseurl = Column('baseurl', UnicodeType(255), index=True, unique=True)
  mode_code = Column('mode_id', Integer, index=True, default=0)
  type_id = Column('type_id', Integer, index=True)
  description = Column('description', UnicodeTextType())
  certificate = Column('certificat', UnicodeTextType())
  ca_certificate = Column('ca_certificat', UnicodeTextType())
  verify_ssl = Column('verify_ssl', Boolean)
  __mode_code = None

  @property
  def mode(self):
    if self.mode_code:
      self.__mode_code = ServerMode(self.mode_code, self, 'mode_code')
    else:
      self.__mode_code = ServerMode('0', self, 'mode_code')
    return self.__mode_code

  @mode.setter
  def mode(self, value):
    self.__mode_code = value
    self.mode_code = value.bit_code
    self.__mode_code.parent = self

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

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
              'name': self.convert_value(self.name),
              'description': self.convert_value(self.description),
              'mode': self.attribute_to_dict(self.mode, cache_object),
              'type_id': self.convert_value(self.type_id),
              'type': self.convert_value(self.type),
              'baseurl': self.convert_value(self.baseurl),
              'certificate': self.convert_value(self.certificate),
              'ca_certificate': self.convert_value(self.ca_certificate),
              'verify_ssl': self.convert_value(self.verify_ssl),
              'user': self.attribute_to_dict(self.user, cache_object),
              'user_id': self.convert_value(self.user.uuid),
              }
    else:
      result = {'name': self.convert_value(self.name)}

    parent_dict = BaseObject.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


  def validate(self):
    # TODO implement validate
    return True
