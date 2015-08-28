# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.campaign.relations import _REL_CAMPAIGN_CONFIDENCE
from ce1sus.db.classes.cstix.coa.relations import _REL_OBJECTIVE_CONFIDENCE
from ce1sus.db.classes.cstix.common.relations import _REL_CONFIDENCE_STRUCTUREDTEXT, _REL_CONFIDENCE_INFORMATIONSOURCE, _REL_STATEMENT_CONFIDENCE, \
  _REL_RELATEDINCIDENT_CONFIDENCE
from ce1sus.db.classes.cstix.common.vocabs import HighMediumLow
from ce1sus.db.classes.internal.corebase import UnicodeType
from ce1sus.db.common.session import Base
from ce1sus.db.classes.cstix.common.relations import _REL_RELATEDCOA_CONFIDENCE, _REL_RELATEDCAMPAIGN_CONFIDENCE, _REL_RELATEDOBSERVABLE_CONFIDENCE, \
  _REL_RELATEDEXPLOITTARGET_CONFIDENCE, _REL_RELATEDPACKAGEREF_CONFIDENCE, _REL_RELATEDPACKAGE_CONFIDENCE, _REL_RELATEDIDENTITY_CONFIDENCE, \
  _REL_RELATEDINDICATOR_CONFIDENCE, _REL_RELATEDTHREATACTOR_CONFIDENCE, _REL_RELATEDTTP_CONFIDENCE
from ce1sus.db.classes.cstix.incident.relations import _REL_INCIDENT_CONFIDENCE
from ce1sus.db.classes.cstix.indicator.relations import _REL_INDICATOR_CONFIDENCE, _REL_SIGHTING_CONFIDENCE


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Confidence(Entity, Base):

  timestamp_precision = Column('timestamp_precision', UnicodeType(10), default=u'second')
  value_db = Column('confidence', Integer, default=3, nullable=False)

  description = relationship('StructuredText', secondary=_REL_CONFIDENCE_STRUCTUREDTEXT, uselist=False, lazy='joined')
  source = relationship('InformationSource', secondary=_REL_CONFIDENCE_INFORMATIONSOURCE, uselist=False)
  # TODO: support confidence_assertion_chain
  timestamp = Column('timestamp', DateTime, default=datetime.utcnow())
  


  _PARENTS = ['campaign',
              'indicator',
              'statement',
              'sighting',
              'incident',
              'objective',
              'related_relatedcoa',
              'related_relatedcampaign',
              'related_relatedobservable',
              'related_relatedexplottarget',
              'related_relatedpackageref',
              'related_relatedpackage',
              'related_relatedidentity',
              'related_relatedindicator',
              'related_relatedthreatactor',
              'related_relatedttp',
              'related_relatedincident',
              ]

  campaign = relationship('Campaign', secondary=_REL_CAMPAIGN_CONFIDENCE, uselist=False)
  objective = relationship('Objective', secondary=_REL_OBJECTIVE_CONFIDENCE, uselist=False)
  related_relatedcoa = relationship('RelatedCOA', uselist=False, secondary=_REL_RELATEDCOA_CONFIDENCE)
  related_relatedcampaign = relationship('RelatedCampaign', uselist=False, secondary=_REL_RELATEDCAMPAIGN_CONFIDENCE)
  related_relatedobservable = relationship('RelatedObservable', uselist=False, secondary=_REL_RELATEDOBSERVABLE_CONFIDENCE)
  related_relatedexplottarget = relationship('RelatedExploitTarget', uselist=False, secondary=_REL_RELATEDEXPLOITTARGET_CONFIDENCE)
  related_relatedpackageref = relationship('RelatedPackageRef', uselist=False, secondary=_REL_RELATEDPACKAGEREF_CONFIDENCE)
  related_relatedpackage = relationship('RelatedPackage', uselist=False, secondary=_REL_RELATEDPACKAGE_CONFIDENCE)
  related_relatedidentity = relationship('RelatedIdentity', uselist=False, secondary=_REL_RELATEDIDENTITY_CONFIDENCE)
  related_relatedincident = relationship('RelatedIncident', uselist=False, secondary=_REL_RELATEDINCIDENT_CONFIDENCE)
  related_relatedindicator = relationship('RelatedIndicator', uselist=False, secondary=_REL_RELATEDINDICATOR_CONFIDENCE)
  related_relatedthreatactor = relationship('RelatedThreatActor', uselist=False, secondary=_REL_RELATEDTHREATACTOR_CONFIDENCE)
  related_relatedttp = relationship('RelatedTTP', uselist=False, secondary=_REL_RELATEDTTP_CONFIDENCE)
  statement = relationship('Statement', secondary=_REL_STATEMENT_CONFIDENCE, uselist=False)
  incident = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_CONFIDENCE)
  indicator = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_CONFIDENCE)
  sighting = relationship('Sighting', uselist=False, secondary=_REL_SIGHTING_CONFIDENCE)


  @property
  def value(self):
    return self.get_dictionary().get(self.value_db, None)

  @value.setter
  def value(self, confidence):
    value_to_set = None
    for key, value in self.get_dictionary().iteritems():
      if value.lower() == confidence.lower():
        value_to_set = key
        break
    if value_to_set:
      self.value_db = value_to_set
    else:
      raise ValueError('Value {0} is not applicable for Confidence'.format(confidence))

  @staticmethod
  def get_dictionary():
    return HighMediumLow.get_dictionary()

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'timestamp': self.convert_value(self.timestamp),
                'timestamp_precision': self.convert_value(self.timestamp_precision),
                'description': self.attribute_to_dict(self.description, cache_object),
                'source': self.attribute_to_dict(self.source, cache_object),
                'value': self.convert_value(self.value)
              }
    else:
      result = {
                'timestamp': self.convert_value(self.timestamp),
                'timestamp_precision': self.convert_value(self.timestamp_precision),
                'value': self.convert_value(self.value)
              }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

