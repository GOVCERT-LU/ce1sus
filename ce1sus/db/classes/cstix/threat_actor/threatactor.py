# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 1, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.intended_effect import IntendedEffect
from ce1sus.db.classes.cstix.common.related import RelatedPackageRef, RelatedThreatActor
from ce1sus.db.classes.cstix.common.vocabs import Motivation as VocabMotivation
from ce1sus.db.classes.cstix.common.vocabs import ThreatActorSophistication as VocabPlanningAndOperationalSupport
from ce1sus.db.classes.cstix.common.vocabs import ThreatActorType as VocabThreatActorType
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_THREATACTOR_IDENTITY = Table('rel_threatactor_identity', getattr(Base, 'metadata'),
                                  Column('rti_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                  Column('identity_id', BigIntegerType, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                  )

_REL_THREATACTOR_RELATED_PACKAGES = Table('rel_threatactor_rel_package', getattr(Base, 'metadata'),
                                          Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                          Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                          Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                          )

_REL_THREATACTOR_RELATED_THREATACTOR = Table('rel_threatactor_rel_threatactor', getattr(Base, 'metadata'),
                                          Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                          Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                          Column('relatedthreatactor_id', BigIntegerType, ForeignKey('relatedthreatactors.relatedthreatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                          )

_REL_THREATACTOR_HANDLING = Table('rel_threatactor_handling', getattr(Base, 'metadata'),
                                Column('rth_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                )

_REL_THREATACTOR_STRUCTUREDTEXT = Table('rel_threatactor_structuredtext', getattr(Base, 'metadata'),
                                       Column('rtast_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('threatactor_id',
                                              BigIntegerType,
                                              ForeignKey('threatactors.threatactor_id',
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

_REL_THREATACTOR_STRUCTUREDTEXT_SHORT = Table('rel_threatactor_structuredtext_short', getattr(Base, 'metadata'),
                                       Column('rtast_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('threatactor_id',
                                              BigIntegerType,
                                              ForeignKey('threatactors.threatactor_id',
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

class ThreatActorType(Entity, Base):

  type_id = Column('type_id', Integer, default=None, nullable=False)
  threatactor_id = Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  __type_ = None

  @property
  def type_(self):
    if not self.__type_:
      if self.status_id:
        self.__type_ = VocabThreatActorType(self, 'type_id')
    return self.__type_

  @type_.setter
  def type_(self, type_):
    if not self.type_:
      self.__type_ = VocabThreatActorType(self, 'type_id')
    self.type_.name = type_

class Motivation(Entity, Base):

  mot_id = Column('mot_id', Integer, default=None, nullable=False)
  threatactor_id = Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  __motivation = None

  @property
  def motivation(self):
    if not self.__motivation:
      self.__motivation = VocabMotivation(self, 'mot_id')
    return self.__motivation

  @motivation.setter
  def motivation(self, motivation):
    if not self.motivation:
      self.__motivation = VocabMotivation(self, 'mot_id')
    self.motivation.name = motivation

  def to_dict(self, cache_object):

    result = {
              'motivation': self.convert_value(self.motivation),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class Sophistication(Entity, Base):

  sop_id = Column('sop_id', Integer, default=None, nullable=False)
  threatactor_id = Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  __sophistication = None

  @property
  def sophistication(self):
    if not self.sophistication:
      self.__sophistication = VocabMotivation(self, 'sop_id')
    return self.__sophistication

  @sophistication.setter
  def sophistication(self, sophistication):
    if not self.sophistication:
      self.__sophistication = VocabMotivation(self, 'sop_id')
    self.sophistication.name = sophistication

  def to_dict(self, cache_object):

    result = {
              'sophistication': self.convert_value(self.sophistication),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class PlanningAndOperationalSupport(Entity, Base):

  paos_id = Column('paos_id', Integer, default=None, nullable=False)
  threatactor_id = Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  __paos = None

  @property
  def paos(self):
    if not self.paos:
      if self.status_id:
        self.__paos = VocabPlanningAndOperationalSupport(self, 'paos_id')
    return self.__paos

  @paos.setter
  def paos(self, paos):
    if not self.paos:
      self.__paos = VocabPlanningAndOperationalSupport(self, 'paos_id')
    self.paos.name = paos

  def to_dict(self, cache_object):

    result = {
              'paos': self.convert_value(self.paos),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class ThreatActor(BaseCoreComponent, Base):

  identity = relationship(Identity, secondary=_REL_THREATACTOR_IDENTITY, uselist=False)
  types = relationship(ThreatActorType)
  motivations = relationship(Motivation)
  sophistications = relationship(Sophistication)
  intended_effects = relationship(IntendedEffect)
  planning_and_operational_supports = relationship(PlanningAndOperationalSupport)
  confidence = Column('confidence', UnicodeType(5), default=u'HIGH', nullable=False)
  handling = relationship(MarkingSpecification, secondary=_REL_THREATACTOR_HANDLING)
  # TODO: observed_ttps is the same as related TTP
  # observed_ttps = None
  # TODO: associated_campaigns is the same as relate Campaign
  # associated_campaigns = None
  # associated_actors is the same as relatedThreatActor
  associated_actors = relationship(RelatedThreatActor, secondary=_REL_THREATACTOR_RELATED_THREATACTOR)
  related_packages = relationship(RelatedPackageRef, secondary=_REL_THREATACTOR_RELATED_PACKAGES)

  event = relationship('Event', uselist=False)
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  def to_dict(self, cache_object):

    result = {
              'identity': self.attribute_to_dict(self.identity, cache_object),
              'types': self.attributelist_to_dict(self.types, cache_object),
              'moditvations': self.attributelist_to_dict(self.motivations, cache_object),
              'sophistications': self.attributelist_to_dict(self.sophistications, cache_object),
              'intended_effects': self.attributelist_to_dict(self.intended_effects, cache_object),
              'planning_and_operational_supports': self.attributelist_to_dict(self.planning_and_operational_supports, cache_object),
              'confidence': self.attribute_to_dict(self.confidence, cache_object),
              'handling': self.attributelist_to_dict(self.handling, cache_object),
              'associated_actors': self.attributelist_to_dict(self.associated_actors, cache_object),
              'related_packages': self.attributelist_to_dict(self.associated_actors, cache_object)
              }

    parent_dict = BaseCoreComponent.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
