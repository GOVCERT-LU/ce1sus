# -*- coding: utf-8 -*-

"""
(Description)

Created on Jun 25, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.vocabs import TargetedInformation as VocabTargetedInformation
from ce1sus.db.classes.cstix.common.vocabs import TargetedSystems as VocabTargetedSystems
from ce1sus.db.classes.internal.core import BaseElement, BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_VICTIMTARGETING_IDENTITY = Table('rel_victimtargeting_identity', getattr(Base, 'metadata'),
                                       Column('rti_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('victimtargeting_id', BigIntegerType, ForeignKey('victimtargetings.victimtargeting_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                       Column('identity_id', BigIntegerType, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                       )


class TargetedInformation(BaseElement, Base):
  targeted_information_id = Column('targeted_information_id', Integer, default=None)
  victimtargeting_id = Column(BigIntegerType, ForeignKey('victimtargetings.victimtargeting_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  __targeted_information = None

  @property
  def parent(self):
    return self.victim_targeting

  @property
  def targeted_information(self):
    if not self.__targeted_information:
      if self.status_id:
        self.__targeted_information = VocabTargetedInformation(self, 'targeted_information_id')
    return self.__targeted_information

  @targeted_information.setter
  def targeted_information(self, targeted_information):
    if not self.targeted_information:
      self.__targeted_information = VocabTargetedInformation(self, 'targeted_information_id')
    self.targeted_information.name = targeted_information


  def to_dict(self, cache_object):

    result = {
              'targeted_information': self.convert_value(self.targeted_information)
              }

    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


class TargetedSystems(BaseElement, Base):
  targeted_system_id = Column('targeted_system_id', Integer, default=None)
  victimtargeting_id = Column(BigIntegerType, ForeignKey('victimtargetings.victimtargeting_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  __targeted_system = None

  @property
  def parent(self):
    return self.victim_targeting

  @property
  def targeted_system(self):
    if not self.__targeted_system:
      if self.status_id:
        self.__targeted_system = VocabTargetedSystems(self, 'targeted_system_id')
    return self.__targeted_system

  @targeted_system.setter
  def targeted_system(self, targeted_system):
    if not self.targeted_system:
      self.__targeted_system = VocabTargetedSystems(self, 'targeted_system_id')
    self.targeted_system.name = targeted_system

  def to_dict(self, cache_object):

    result = {
              'targeted_system': self.convert_value(self.targeted_information)
              }

    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class VictimTargeting(BaseElement, Base):
  identity = relationship(Identity, secondary='rel_victimtargeting_identity', uselist=False, backref='victim_targeting')
  targeted_systems = relationship(TargetedSystems, backref='victim_targeting')
  targeted_information = relationship(TargetedInformation, backref='victim_targeting')
  # TODO targeted_technical_details
  # targeted_technical_details = None

  # custom ones related to ce1sus internals
  ttp_id = Column(BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  vulnerability_id = Column('vulnerability_id', BigIntegerType, ForeignKey('vulnerabilitys.vulnerability_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  @property
  def parent(self):
    return self.ttp

  def to_dict(self, cache_object):

    result = {
              'identity': self.attribute_to_dict(self.identity, cache_object),
              'targeted_systems': self.attributelist_to_dict(self.targeted_systems, cache_object),
              'targeted_information': self.attributelist_to_dict(self.targeted_information, cache_object),
              }

    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
