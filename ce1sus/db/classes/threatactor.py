# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 1, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import BigInteger, Unicode, UnicodeText, Integer

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Marking, IntendedEffect
from ce1sus.db.classes.identity import Identity
from ce1sus.db.common.session import Base
from stix.common.vocabs import Motivation as StixMotivation
from stix.common.vocabs import PlanningAndOperationalSupport as StixPlanningAndOperationalSupport
from stix.common.vocabs import ThreatActorSophistication
from stix.common.vocabs import ThreatActorType as StixThreatActorType


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_THREATACTOR_IDENTITY = Table('rel_threatactor_identity', Base.metadata,
                                  Column('rti_id', BigInteger, primary_key=True, nullable=False, index=True),
                                  Column('threatactor_id', BigInteger, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                  Column('identity_id', BigInteger, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                  )

_REL_THREATACTOR_INTENDEDEFFECT = Table('rel_threatactor_intendedeffect', Base.metadata,
                                        Column('rti_id', BigInteger, primary_key=True, nullable=False, index=True),
                                        Column('threatactor_id', BigInteger, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                        Column('intendedeffect_id', BigInteger, ForeignKey('intendedeffects.intendedeffect_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                        )

class ThreatActorType(Base):

  type = Column('type', Integer, default=None, nullable=False)
  threatactor_id = Column('threatactor_id', BigInteger, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  @classmethod
  def get_dictionary(cls):
    return {
            0: StixThreatActorType.TERM_CYBER_ESPIONAGE_OPERATIONS,
            1: StixThreatActorType.TERM_HACKER,
            2: StixThreatActorType.TERM_HACKER_WHITE_HAT,
            3: StixThreatActorType.TERM_HACKER_GRAY_HAT,
            4: StixThreatActorType.TERM_HACKER_BLACK_HAT,
            5: StixThreatActorType.TERM_HACKTIVIST,
            6: StixThreatActorType.TERM_STATE_ACTOR_OR_AGENCY,
            7: StixThreatActorType.TERM_ECRIME_ACTOR_CREDENTIAL_THEFT_BOTNET_OPERATOR,
            8: StixThreatActorType.TERM_ECRIME_ACTOR_CREDENTIAL_THEFT_BOTNET_SERVICE,
            9: StixThreatActorType.TERM_ECRIME_ACTOR_MALWARE_DEVELOPER,
            10: StixThreatActorType.TERM_ECRIME_ACTOR_MONEY_LAUNDERING_NETWORK,
            11: StixThreatActorType.TERM_ECRIME_ACTOR_ORGANIZED_CRIME_ACTOR,
            12: StixThreatActorType.TERM_ECRIME_ACTOR_SPAM_SERVICE,
            13: StixThreatActorType.TERM_ECRIME_ACTOR_TRAFFIC_SERVICE,
            14: StixThreatActorType.TERM_ECRIME_ACTOR_UNDERGROUND_CALL_SERVICE,
            15: StixThreatActorType.TERM_INSIDER_THREAT,
            16: StixThreatActorType.TERM_DISGRUNTLED_CUSTOMER_OR_USER,
            }

  @property
  def name(self):
    return self.get_dictionary().get(self.type, None)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}


class Motivation(Base):

  type = Column('type', Integer, default=None, nullable=False)
  threatactor_id = Column('threatactor_id', BigInteger, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  @classmethod
  def get_dictionary(cls):
    return {
            0: StixMotivation.TERM_IDEOLOGICAL,
            1: StixMotivation.TERM_IDEOLOGICAL_ANTICORRUPTION,
            2: StixMotivation.TERM_IDEOLOGICAL_ANTIESTABLISHMENT,
            3: StixMotivation.TERM_IDEOLOGICAL_ENVIRONMENTAL,
            4: StixMotivation.TERM_IDEOLOGICAL_ETHNIC_OR_NATIONALIST,
            5: StixMotivation.TERM_IDEOLOGICAL_INFORMATION_FREEDOM,
            6: StixMotivation.TERM_IDEOLOGICAL_RELIGIOUS,
            7: StixMotivation.TERM_IDEOLOGICAL_SECURITY_AWARENESS,
            8: StixMotivation.TERM_IDEOLOGICAL_HUMAN_RIGHTS,
            9: StixMotivation.TERM_EGO,
            10: StixMotivation.TERM_FINANCIAL_OR_ECONOMIC,
            11: StixMotivation.TERM_MILITARY,
            12: StixMotivation.TERM_OPPORTUNISTIC,
            13: StixMotivation.TERM_POLITICAL,
            }

  @property
  def name(self):
    return self.get_dictionary().get(self.type, None)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}


class Sophistication(Base):

  type = Column('type', Integer, default=None, nullable=False)
  threatactor_id = Column('threatactor_id', BigInteger, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  @classmethod
  def get_dictionary(cls):
    return {
            0: ThreatActorSophistication.TERM_INNOVATOR,
            1: ThreatActorSophistication.TERM_EXPERT,
            2: ThreatActorSophistication.TERM_PRACTITIONER,
            3: ThreatActorSophistication.TERM_NOVICE,
            4: ThreatActorSophistication.TERM_ASPIRANT,
            }

  @property
  def name(self):
    return self.get_dictionary().get(self.type, None)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}


class PlanningAndOperationalSupport(Base):

  type = Column('type', Integer, default=None, nullable=False)
  threatactor_id = Column('threatactor_id', BigInteger, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  @classmethod
  def get_dictionary(cls):
    return {
            0: StixPlanningAndOperationalSupport.TERM_DATA_EXPLOITATION,
            1: StixPlanningAndOperationalSupport.TERM_DATA_EXPLOITATION_ANALYTIC_SUPPORT,
            2: StixPlanningAndOperationalSupport.TERM_DATA_EXPLOITATION_TRANSLATION_SUPPORT,
            3: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES,
            4: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES_ACADEMIC,
            5: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES_COMMERCIAL,
            6: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES_GOVERNMENT,
            7: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES_HACKTIVIST_OR_GRASSROOT,
            8: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES_NONATTRIBUTABLE_FINANCE,
            9: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT,
            10: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_CONTRACTING_AND_HIRING,
            11: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_DOCUMENT_EXPLOITATION_DOCEX_TRAINING,
            12: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_INTERNAL_TRAINING,
            13: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_MILITARY_PROGRAMS,
            14: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_SECURITY_OR_HACKER_CONFERENCES,
            15: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_UNDERGROUND_FORUMS,
            16: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_UNIVERSITY_PROGRAMS,
            17: StixPlanningAndOperationalSupport.TERM_PLANNING,
            18: StixPlanningAndOperationalSupport.TERM_PLANNING_OPERATIONAL_COVER_PLAN,
            19: StixPlanningAndOperationalSupport.TERM_PLANNING_OPENSOURCE_INTELLIGENCE_OSINT_GATHERING,
            20: StixPlanningAndOperationalSupport.TERM_PLANNING_PREOPERATIONAL_SURVEILLANCE_AND_RECONNAISSANCE,
            21: StixPlanningAndOperationalSupport.TERM_PLANNING_TARGET_SELECTION,
            }

  @property
  def name(self):
    return self.get_dictionary().get(self.type, None)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}


class ThreatActor(ExtendedLogingInformations, Base):

  # base properties
  title = Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=True)
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  short_description = Column('short_description', Unicode(255, collation='utf8_unicode_ci'))
  version = Column('version', Unicode(40, collation='utf8_unicode_ci'), default=u'1.0.0', nullable=False)
  handling = relationship(Marking, secondary='rel_ttp_handling')

  identity = relationship(Identity, secondary='rel_threatactor_identity', uselist=False)
  types = relationship(ThreatActorType)
  motivations = relationship(Motivation)
  sophistications = relationship(Sophistication)
  intended_effects = relationship(IntendedEffect, secondary='rel_threatactor_intendedeffect')
  planning_and_operational_supports = relationship(PlanningAndOperationalSupport)
  confidence = Column('confidence', Unicode(5, collation='utf8_unicode_ci'), default=u'HIGH', nullable=False)
  # TODO: observed_ttps is the same as related TTP
  # observed_ttps = None
  # TODO: associated_campaigns is the same as relate Campaign
  # associated_campaigns = None
  # TODO: associated_actors is the same as relatedThreatActor
  # associated_actors = None
  # TODO: related_packages
  # TODO: related packages
  # related_packages = None

  # custom ones related to ce1sus internals
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  event = relationship('Event', uselist=False)
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
