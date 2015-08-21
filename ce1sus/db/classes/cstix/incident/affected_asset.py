# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.vocabs import AssetType as VocabAssetType
from ce1sus.db.classes.cstix.common.vocabs import OwnerShipClass
from ce1sus.db.classes.cstix.incident.property_affected import PropertyAffected
from ce1sus.db.classes.cstix.incident.relations import _REL_AFFECTEDASSET_STRUCTUREDTEXT, _REL_AFFECTEDASSET_BFR_STRUCTUREDTEXT
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class AssetType(Entity, Base):
  type_id = Column('type_id', Integer, default=None, nullable=False)
  count_affected = Column('count_affected', Integer, nullable=False, default=1)

  affectedasset_id = Column(BigIntegerType, ForeignKey('affectedassets.affectedasset_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  __value = None

  _PARENTS = ['affected_asset']
  affected_asset = relationship('AffectedAsset', uselist=False)
  @property
  def value(self):
    if not self.__value:
      if self.type_id:
        self.__value = VocabAssetType(self, 'type_id')
    return self.__value

  @value.setter
  def value(self, value):
    if not self.value:
      self.__value = VocabAssetType(self, 'type_id')
    self.value.name = value

  def to_dict(self, cache_object):

    result = {
              'count_affected': self.convert_value(self.count_affected),
              'value': self.convert_value(self.value)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)



class AffectedAsset(Entity, Base):

  type_ = relationship(AssetType, uselist=False)
  description = relationship(StructuredText, secondary=_REL_AFFECTEDASSET_STRUCTUREDTEXT, uselist=False)
  business_function_or_role = relationship(StructuredText, secondary=_REL_AFFECTEDASSET_BFR_STRUCTUREDTEXT, uselist=False)

  ownership_class_id = Column('ownership_class_id', Integer)
  __ownership_class = None
  
  @property
  def ownership_class(self):
    if not self.__ownership_class:
      if self.ownership_class_id:
        self.__ownership_class = OwnerShipClass(self, 'ownership_class_id')
      else:
        return None
    return self.__ownership_class.name

  @ownership_class.setter
  def ownership_class(self, value):
    if not self.ownership_class:
      self.__ownership_class = OwnerShipClass(self, 'ownership_class_id')
    self.ownership_class.name = value

  management_class_id = Column('management_class_id', Integer)
  __management_class = None

  @property
  def management_class(self):
    if not self.__management_class:
      if self.management_class_id:
        self.__management_class = OwnerShipClass(self, 'management_class_id')
      else:
        return None
    return self.__management_class.name

  @management_class.setter
  def management_class(self, value):
    if not self.management_class:
      self.__management_class = OwnerShipClass(self, 'management_class_id')
    self.management_class.name = value

  location_class_id = Column('location_class_id', Integer)
  __location_class = None

  @property
  def location_class(self):
    if not self.__location_class:
      if self.location_class_id:
        self.__location_class = OwnerShipClass(self, 'location_class_id')
      else:
        return None
    return self.__location_class.name

  @location_class.setter
  def location_class(self, value):
    if not self.location_class:
      self.__location_class = OwnerShipClass(self, 'location_class_id')
    self.location_class.name = value

  # WTF is this?
  # TODO: location
  # location = None
  nature_of_security_effect = relationship(PropertyAffected, uselist=False)
  # TODO: structured_description
  # structured_description = None

  incident_id = Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  _PARENTS = ['incident']
  incident = relationship('Incident', uselist=False)

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'type_': self.attribute_to_dict(self.type_, cache_object),
                'description': self.attribute_to_dict(self.description, cache_object),
                'business_function_or_role': self.convert_value(self.business_function_or_role),
                'ownership_class': self.convert_value(self.ownership_class),
                'management_class': self.convert_value(self.management_class),
                'location_class': self.convert_value(self.location_class),
                'nature_of_security_effect': self.attribute_to_dict(self.nature_of_security_effect, cache_object)
                }
    else:
      result = {
                'type_': self.attribute_to_dict(self.type_, cache_object),
                }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)