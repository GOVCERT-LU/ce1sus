# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Boolean, Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.vocabs import LossProperty, AvailabilityLoss, LossDuration
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_PROPERTYAFFECTED_STRUCTUREDTEXT = Table('rel_propertyaffected_structuredtext', getattr(Base, 'metadata'),
                                             Column('rps_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                             Column('propertyaffected_id',
                                                    BigIntegerType,
                                                    ForeignKey('propertyaffecteds.propertyaffected_id',
                                                               ondelete='cascade',
                                                               onupdate='cascade'),
                                                    index=True,
                                                    nullable=False),
                                             Column('structuredtext_id',
                                                    BigIntegerType,
                                                    ForeignKey('structuredtexts.structuredtext_id',
                                                               ondelete='cascade',
                                                               onupdate='cascade'),
                                                    nullable=False,
                                                    index=True)
                                             )


class NonPublicDataCompromised(Entity, Base):

  vocab_name = Column('vocab_name', UnicodeType(255), nullable=True)
  vocab_reference = Column('vocab_reference', UnicodeType(255), nullable=True)
  data_encrypted = Column('data_encrypted', Boolean, nullable=True)

  propertyaffected_id = Column('propertyaffected_id', BigIntegerType, ForeignKey('propertyaffecteds.propertyaffected_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  _PARENTS = ['property_affacted']

class PropertyAffected(Entity, Base):
  property_id = Column(Integer)
  __property_ = None
  @property
  def property_(self):
    if not self.__property_:
      if self.property_id:
        self.__property_ = LossProperty(self, 'property_id')
    return self.__property_

  @property_.setter
  def property_(self, property_):
    if not self.property_:
      self.__property_ = LossProperty(self, 'property_id')
    self.property_.name = property_

  description_of_effect = relationship(StructuredText, secondary=_REL_PROPERTYAFFECTED_STRUCTUREDTEXT, backref='property_affacted_description')

  type_of_availability_loss_id = Column(Integer)
  __type_of_availability_loss = None

  @property
  def type_of_availability_loss(self):
    if not self.__type_of_availability_loss:
      if self.type_of_availability_lossid:
        self.__type_of_availability_loss = AvailabilityLoss(self, 'type_of_availability_loss_id')
    return self.__type_of_availability_loss

  @type_of_availability_loss.setter
  def type_of_availability_loss(self, type_of_availability_loss):
    if not self.type_of_availability_loss:
      self.__type_of_availability_loss = AvailabilityLoss(self, 'type_of_availability_loss_id')
    self.type_of_availability_loss.name = type_of_availability_loss


  duration_of_availability_loss_id = Column(Integer)
  __duration_of_availability_loss = None

  @property
  def duration_of_availability_loss(self):
    if not self.__duration_of_availability_loss:
      if self.duration_of_availability_lossid:
        self.__duration_of_availability_loss = LossDuration(self, 'duration_of_availability_loss_id')
    return self.__duration_of_availability_loss

  @duration_of_availability_loss.setter
  def duration_of_availability_loss(self, duration_of_availability_loss):
    if not self.duration_of_availability_loss:
      self.__duration_of_availability_loss = LossDuration(self, 'duration_of_availability_loss_id')
    self.duration_of_availability_loss.name = duration_of_availability_loss

  non_public_data_compromised = relationship(NonPublicDataCompromised, uselist=False, backref='property_affacted')

  affectedasset_id = Column('affectedasset_id', BigIntegerType, ForeignKey('affectedassets.affectedasset_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  _PARENTS = ['affected_asset']

  def to_dict(self, cache_object):

    result = {
              'property_': self.convert_value(self.property_),
              'type_of_availability_loss': self.convert_value(self.type_of_availability_loss),
              'duration_of_availability_loss': self.convert_value(self.duration_of_availability_loss),
              'non_public_data_compromised': self.attribute_to_dict(self.non_public_data_compromised, cache_object)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
