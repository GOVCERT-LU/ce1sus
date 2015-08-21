# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.ccybox.common.time import CyboxTime
from ce1sus.db.classes.ccybox.core.relations import _REL_CAMPAIGN_INFORMATIONSOURCE
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.relations import _REL_RELATEDCOA_INFORMATIONSOURCE, _REL_RELATEDCAMPAIGN_INFORMATIONSOURCE, \
  _REL_RELATEDOBSERVABLE_INFORMATIONSOURCE, _REL_RELATEDEXPLOITTARGET_INFORMATIONSOURCE, _REL_RELATEDPACKAGEREF_INFORMATIONSOURCE, \
  _REL_RELATEDPACKAGE_INFORMATIONSOURCE, _REL_RELATEDIDENTITY_INFORMATIONSOURCE, _REL_RELATEDINDICATOR_INFORMATIONSOURCE, \
  _REL_RELATEDTHREATACTOR_INFORMATIONSOURCE, _REL_RELATEDTTP_INFORMATIONSOURCE, _REL_RELATEDINCIDENT_INFORMATIONSOURCE
from ce1sus.db.classes.cstix.common.relations import _REL_CONFIDENCE_INFORMATIONSOURCE, _REL_INFORMATIONSOURCE_STRUCTUREDTEXT, _REL_INFORMATIONSOURCE_IDENTITY, \
  _REL_INFORMATIONSOURCE_INFORMATIONSOURCE, _REL_INFORMATIONSOURCE_TOOL, _REL_STATEMENT_INFORMATIONSOURCE
from ce1sus.db.classes.cstix.common.tools import ToolInformation
from ce1sus.db.classes.cstix.common.vocabs import InformationSourceRole as VocabInformationSourceRole
from ce1sus.db.classes.cstix.core.relations import _REL_STIXHEADER_INFORMATIONSOURCE
from ce1sus.db.classes.cstix.exploit_target.relations import _REL_EXPLOITTARGET_INFORMATIONSOURCE
from ce1sus.db.classes.cstix.incident.relations import _REL_INCIDENT_INFORMATIONSOURCE_REP, _REL_INCIDENT_INFORMATIONSOURCE_RES, \
  _REL_INCIDENT_INFORMATIONSOURCE_COO, _REL_INCIDENT_INFORMATIONSOURCE
from ce1sus.db.classes.cstix.indicator.relations import _REL_INDICAOTR_INFORMATIONSOURCE, _REL_SIGHTING_INFORMATIONSOURCE, _REL_TESTMECHANISM_INFORMATIONSOURCE
from ce1sus.db.classes.cstix.relations import _REL_MARKINGSPECIFICATIONS_INFORMATIONSOURCE
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base
from ce1sus.db.classes.cstix.threat_actor.relations import _REL_THREATACTOR_INFORMATIONSOURCE
from ce1sus.db.classes.cstix.ttp.relations import _REL_TTP_INFORMATIONSOURCE


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class InformationSourceRole(Entity, Base):
  
  role_id = Column('role_id', Integer, default=None, nullable=False)
  informationsource_id = Column(BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  information_source = relationship('InformationSource', uselist=False)

  _PARENTS = ['information_source']

  __role = None
  @property
  def role(self):
    if not self.__role:
      if self.role_id:
        self.__role = VocabInformationSourceRole(self, 'role_id')
    return self.__role.name

  @role.setter
  def role(self, role):
    if not self.__role:
      self.__role = VocabInformationSourceRole(self, 'role_id')
    self.__role.name = role


  def to_dict(self, cache_object):
    result = {'name': self.convert_value(self.role)}
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class InformationSource(Entity, Base):
  """ An information source is a bit tricky as the groups contain half of the needed elements """

  description = relationship('StructuredText', secondary=_REL_INFORMATIONSOURCE_STRUCTUREDTEXT, uselist=False)
  identity = relationship(Identity, secondary=_REL_INFORMATIONSOURCE_IDENTITY, uselist=False)

  contributing_sources = relationship('InformationSource',
                                      secondary=_REL_INFORMATIONSOURCE_INFORMATIONSOURCE,
                                      primaryjoin='InformationSource.identifier == rel_informationsource_contributing_sources.c.parent_id',
                                      secondaryjoin='InformationSource.identifier == rel_informationsource_contributing_sources.c.child_id'
                                      )
  
  time = relationship(CyboxTime, uselist=False)
  tools = relationship(ToolInformation, secondary=_REL_INFORMATIONSOURCE_TOOL)

  roles = relationship(InformationSourceRole)
  # TODO: references -> relation

  confidence = relationship('Confidence', secondary=_REL_CONFIDENCE_INFORMATIONSOURCE, uselist=False)
  information_source = relationship('InformationSource',
                                    uselist=False,
                                    secondary=_REL_INFORMATIONSOURCE_INFORMATIONSOURCE,
                                    secondaryjoin='InformationSource.identifier == rel_informationsource_contributing_sources.c.parent_id',
                                    primaryjoin='InformationSource.identifier == rel_informationsource_contributing_sources.c.child_id'
                                    )

  related_relatedcoa = relationship('RelatedCOA', uselist=False, secondary=_REL_RELATEDCOA_INFORMATIONSOURCE)
  related_relatedcampaign = relationship('RelatedCampaign', uselist=False, secondary=_REL_RELATEDCAMPAIGN_INFORMATIONSOURCE)
  related_relatedobservable = relationship('RelatedObservable', uselist=False, secondary=_REL_RELATEDOBSERVABLE_INFORMATIONSOURCE)
  related_relatedexplottarget = relationship('RelatedExploitTarget', uselist=False, secondary=_REL_RELATEDEXPLOITTARGET_INFORMATIONSOURCE)
  related_relatedpackageref = relationship('RelatedPackageRef', uselist=False, secondary=_REL_RELATEDPACKAGEREF_INFORMATIONSOURCE)
  related_relatedpackage = relationship('RelatedPackage', uselist=False, secondary=_REL_RELATEDPACKAGE_INFORMATIONSOURCE)
  related_relatedidentity = relationship('RelatedIdentity', uselist=False, secondary=_REL_RELATEDIDENTITY_INFORMATIONSOURCE)
  related_relatedincident = relationship('RelatedIncident', uselist=False, secondary=_REL_RELATEDINCIDENT_INFORMATIONSOURCE)
  related_relatedindicator = relationship('RelatedIndicator', uselist=False, secondary=_REL_RELATEDINDICATOR_INFORMATIONSOURCE)
  related_relatedthreatactor = relationship('RelatedThreatActor', uselist=False, secondary=_REL_RELATEDTHREATACTOR_INFORMATIONSOURCE)
  related_relatedttp = relationship('RelatedTTP', uselist=False, secondary=_REL_RELATEDTTP_INFORMATIONSOURCE)
  statement_description = relationship('Statement', secondary=_REL_STATEMENT_INFORMATIONSOURCE, uselist=False)
  stix_header = relationship('STIXHeader', secondary=_REL_STIXHEADER_INFORMATIONSOURCE, uselist=False)
  incident_reporter = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_INFORMATIONSOURCE_REP)
  incident_responder = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_INFORMATIONSOURCE_RES)
  incident_coordinators = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_INFORMATIONSOURCE_COO)
  indicator_producer = relationship('Indicator', uselist=False, secondary=_REL_INDICAOTR_INFORMATIONSOURCE)
  sighting = relationship('Sighting', uselist=False, secondary=_REL_SIGHTING_INFORMATIONSOURCE)
  base_test_mechanism = relationship('BaseTestMechanism', secondary=_REL_TESTMECHANISM_INFORMATIONSOURCE, uselist=False)
  markingspecification = relationship('MarkingSpecification', uselist=False, secondary=_REL_MARKINGSPECIFICATIONS_INFORMATIONSOURCE)
  campaign = relationship('Campaign', uselist=False, secondary=_REL_CAMPAIGN_INFORMATIONSOURCE)
  exploit_target = relationship('ExploitTarget', uselist=False, secondary=_REL_EXPLOITTARGET_INFORMATIONSOURCE)
  incident = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_INFORMATIONSOURCE)
  threatactor = relationship('ThreatActor', uselist=False, secondary=_REL_THREATACTOR_INFORMATIONSOURCE)
  ttp = relationship('TTP', uselist=False, secondary=_REL_TTP_INFORMATIONSOURCE)
  indicator = relationship('Indicator', uselist=False, secondary=_REL_INDICAOTR_INFORMATIONSOURCE)

  _PARENTS = ['information_source',
              'exploit_target',
              'confidence',
              'statement',
              'base_test_mechanism',
              'sighting',
              'indicator',
              'incident_reporter',
              'incident_responder',
              'incident_coordinators',
              'campaign',
              'exploittarget',
              'incident',
              'threatactor',
              'ttp',
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
              'related_relatedindicator', ]

  def to_dict(self, cache_object):
    copy = cache_object.make_copy()
    copy.inflated = True
    if cache_object.complete:
      result = {
                'description':self.attribute_to_dict(self.description, cache_object),
                'identity': self.attribute_to_dict(self.identity, copy),
                'time': self.attribute_to_dict(self.time, cache_object),
                'tools': self.attributelist_to_dict(self.tools, cache_object),
                'roles': self.attributelist_to_dict(self.roles, copy),
                'contributing_sources': self.attributelist_to_dict(self.contributing_sources, copy)
              }
    else:
      result = {
                'identity': self.attribute_to_dict(self.identity, cache_object),
                'time': self.attribute_to_dict(self.identity, cache_object),
                'roles': self.attributelist_to_dict(self.roles, cache_object),
              }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
