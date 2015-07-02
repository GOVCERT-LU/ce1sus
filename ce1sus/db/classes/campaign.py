# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 2, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Unicode, UnicodeText, BigInteger, Integer, DateTime

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Marking, IntendedEffect
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_CAMPAIGN_INTENDEDEFFECT = Table('rel_campaign_intendedeffect', Base.metadata,
                                     Column('rci_id', BigInteger, primary_key=True, nullable=False, index=True),
                                     Column('campaign_id', BigInteger, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                     Column('intendedeffect_id', BigInteger, ForeignKey('intendedeffects.intendedeffect_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                     )


class Names(ExtendedLogingInformations, Base):

  name = Column('name', Unicode(255, collation='utf8_unicode_ci'), default=None, nullable=False)
  # reference = anyuri
  reference = Column('reference', Unicode(255, collation='utf8_unicode_ci'), default=None, nullable=False)
  campaign_id = Column('campaign_id', BigInteger, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}


class Status(ExtendedLogingInformations, Base):

  name = Column('name', Unicode(255, collation='utf8_unicode_ci'), default=None, nullable=False)
  # reference = anyuri
  reference = Column('reference', Unicode(255, collation='utf8_unicode_ci'), default=None, nullable=False)
  campaign_id = Column('campaign_id', BigInteger, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}


class Attribution(ExtendedLogingInformations, Base):
  name = Column('name', Unicode(255, collation='utf8_unicode_ci'), default=None, nullable=False)
  # reference = anyuri
  reference = Column('reference', Unicode(255, collation='utf8_unicode_ci'), default=None, nullable=False)
  campaign_id = Column('campaign_id', BigInteger, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}


class Activity(ExtendedLogingInformations, Base):
  
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  campaign_id = Column('campaign_id', BigInteger, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  date_time = Column('date_time', DateTime, nullable=False)

class Campaign(ExtendedLogingInformations, Base):

  # base properties
  title = Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=True)
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  short_description = Column('short_description', Unicode(255, collation='utf8_unicode_ci'))
  version = Column('version', Unicode(40, collation='utf8_unicode_ci'), default=u'1.0.0', nullable=False)
  handling = relationship(Marking, secondary='rel_ttp_handling')

  names = relationship(Names)
  intended_effects = relationship(IntendedEffect, secondary='rel_campaign_intendedeffect')
  status = relationship(Status)
  # TODO: related_ttps
  # related_ttps = RelatedTTPs()
  # TODO: related_incidents
  # related_incidents = RelatedIncidents()
  # TODO: related_indicators
  # related_indicators = RelatedIndicators()

  attribution = relationship(Attribution)
  # TODO: associated_campaigns = relatedCampaign
  # associated_campaigns = AssociatedCampaigns()
  confidence = Column('confidence', Unicode(5, collation='utf8_unicode_ci'), default=u'HIGH', nullable=False)
  activity = relationship(Activity)
  # TOOO: relatedPackages
  # related_packages = RelatedPackageRefs()

  # custom ones related to ce1sus internals
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  event = relationship('Event', uselist=False)
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
