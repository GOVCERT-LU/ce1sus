# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.ccybox.core.relations import _REL_OBSERVABLE_STRUCTUREDTEXT
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.campaign.relations import _REL_CAMPAIGN_STRUCTUREDTEXT, _REL_CAMPAIGN_STRUCTUREDTEXT_SHORT
from ce1sus.db.classes.cstix.coa.relations import _REL_OBJECTIVE_SHORT_STRUCTUREDTEXT, _REL_OBJECTIVE_STRUCTUREDTEXT
from ce1sus.db.classes.cstix.common.relations import _REL_ACTIVITY_STRUCTUREDTEXT, _REL_CONFIDENCE_STRUCTUREDTEXT, _REL_INFORMATIONSOURCE_STRUCTUREDTEXT, \
  _REL_STATEMENT_STRUCTUREDTEXT, _REL_TOOLINFORMATION_STRUCTUREDTEXT, _REL_TOOLINFORMATION_STRUCTUREDTEXT_SHORT
from ce1sus.db.classes.cstix.core.relations import _REL_STIXHEADER_STRUCTUREDTEXT, _REL_STIXHEADER_STRUCTUREDTEXT_SHORT
from ce1sus.db.classes.cstix.exploit_target.relations import _REL_CONFIGURATION_STRUCTUREDTEXT, _REL_CONFIGURATION_STRUCTUREDTEXT_SHORT, \
  _REL_VULNERABILITY_STRUCTUREDTEXT, _REL_VULNERABILITY_STRUCTUREDTEXT_SHORT, _REL_EXPLOITTARGET_STRUCTUREDTEXT, _REL_EXPLOITTARGET_STRUCTUREDTEXT_SHORT
from ce1sus.db.classes.cstix.incident.relations import _REL_AFFECTEDASSET_STRUCTUREDTEXT, _REL_AFFECTEDASSET_BFR_STRUCTUREDTEXT, \
  _REL_PROPERTYAFFECTED_STRUCTUREDTEXT, _REL_INCIDENT_STRUCTUREDTEXT, _REL_INCIDENT_STRUCTUREDTEXT_SHORT
from ce1sus.db.classes.cstix.indicator.relations import _REL_TESTMECHANISM_STRUCTUREDTEXT, _REL_SIGHTING_STRUCTUREDTEXT, _REL_INDICATOR_STRUCTUREDTEXT, \
  _REL_INDICATOR_STRUCTUREDTEXT_SHORT
from ce1sus.db.classes.cstix.threat_actor.relations import _REL_THREATACTOR_STRUCTUREDTEXT, _REL_THREATACTOR_STRUCTUREDTEXT_SHORT
from ce1sus.db.classes.cstix.ttp.relations import _REL_ATTACKPATTERN_STRUCTUREDTEXT, _REL_ATTACKPATTERN_STRUCTUREDTEXT_SHORT, _REL_EXPLOIT_STRUCTUREDTEXT, \
  _REL_EXPLOIT_STRUCTUREDTEXT_SHORT, _REL_INFRASTRUCTURE_STRUCTUREDTEXT, _REL_INFRASTRUCTURE_STRUCTUREDTEXT_SHORT, _REL_MALWAREINSTANCE_STRUCTUREDTEXT, \
  _REL_MALWAREINSTANCE_STRUCTUREDTEXT_SHORT, _REL_TTP_STRUCTUREDTEXT, _REL_TTP_STRUCTUREDTEXT_SHORT
from ce1sus.db.classes.internal.corebase import UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base
from ce1sus.db.classes.internal.relations import _REL_REPORT_STRUCTUREDTEXT


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class StructuredText(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.__class__.__name__, self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')
  # TODO: make structured text as Entity
  value = Column('description', UnicodeTextType(), nullable=False)
  structuring_format = Column('structuring_format', UnicodeType(10), nullable=False, default=u'text')
  ordinality = Column('ordinality', Integer, nullable=False, default=1)

  _PARENTS = ['stix_header_description',
              'stix_header_short_description',
              'information_source_description',
              'tool_information_description',
              'tool_information_short_description',
              'malware_instance_description',
              'malware_instance_short_description',
              'attack_pattern_description',
              'attack_pattern_short_description',
              'infrastructure_description',
              'infrastructure_short_description',
              'exploit_description',
              'exploit_short_description',
              'vulnerability_description',
              'vulnerability_short_description',
              'configuration_description',
              'configuration_short_description',
              'confidence_description',
              'statement_description',
              'generic_test_meachanism_description',
              'sighting_description',
              'activity_description',
              'affected_asset_description',
              'affected_asset_short_description',
              'observable_description',
              'property_affacted_description',
              'objective_description',
              'objective_short_description',
              'campaign',
              'exploit_target',
              'incident',
              'threatactor',
              'ttp',
              'indicator',
              'report_description',
              'report_short_description', ]

  observable_description = relationship('Observable', secondary=_REL_OBSERVABLE_STRUCTUREDTEXT, uselist=False)
  objective_description = relationship('Objective', secondary=_REL_OBJECTIVE_STRUCTUREDTEXT, uselist=False)
  objective_short_description = relationship('Objective', secondary=_REL_OBJECTIVE_SHORT_STRUCTUREDTEXT, uselist=False)
  activity_description = relationship('Activity', secondary=_REL_ACTIVITY_STRUCTUREDTEXT, uselist=False)
  confidence_description = relationship('Confidence', secondary=_REL_CONFIDENCE_STRUCTUREDTEXT, uselist=False)
  information_source_description = relationship('InformationSource', secondary=_REL_INFORMATIONSOURCE_STRUCTUREDTEXT, uselist=False)
  statement_description = relationship('Statement', secondary=_REL_STATEMENT_STRUCTUREDTEXT, uselist=False)
  tool_information_description = relationship('ToolInformation', secondary=_REL_TOOLINFORMATION_STRUCTUREDTEXT, uselist=False)
  tool_information_short_description = relationship('ToolInformation', secondary=_REL_TOOLINFORMATION_STRUCTUREDTEXT_SHORT, uselist=False)
  stix_header_description = relationship('STIXHeader', secondary=_REL_STIXHEADER_STRUCTUREDTEXT, uselist=False)
  stix_header_short_description = relationship('STIXHeader', secondary=_REL_STIXHEADER_STRUCTUREDTEXT_SHORT, uselist=False)
  configuration_description = relationship('Configuration', uselist=False, secondary=_REL_CONFIGURATION_STRUCTUREDTEXT)
  configuration_short_description = relationship('Configuration', uselist=False, secondary=_REL_CONFIGURATION_STRUCTUREDTEXT_SHORT)
  vulnerability_description = relationship('Vulnerability', uselist=False, secondary=_REL_VULNERABILITY_STRUCTUREDTEXT)
  vulnerability_short_description = relationship('Vulnerability', uselist=False, secondary=_REL_VULNERABILITY_STRUCTUREDTEXT_SHORT)
  generic_test_meachanism_description = relationship('GenericTestMechanism', uselist=False, secondary=_REL_TESTMECHANISM_STRUCTUREDTEXT)
  affected_asset_description = relationship('AffectedAsset', uselist=False, secondary=_REL_AFFECTEDASSET_STRUCTUREDTEXT)
  affected_asset_short_description = relationship('AffectedAsset', uselist=False, secondary=_REL_AFFECTEDASSET_BFR_STRUCTUREDTEXT)
  property_affacted_description = relationship('PropertyAffected', uselist=False, secondary=_REL_PROPERTYAFFECTED_STRUCTUREDTEXT)
  sighting_description = relationship('Sighting', uselist=False, secondary=_REL_SIGHTING_STRUCTUREDTEXT)
  attack_pattern_description = relationship('AttackPattern', uselist=False, secondary=_REL_ATTACKPATTERN_STRUCTUREDTEXT)
  attack_pattern_short_description = relationship('AttackPattern', uselist=False, secondary=_REL_ATTACKPATTERN_STRUCTUREDTEXT_SHORT)
  exploit_description = relationship('Exploit', uselist=False, secondary=_REL_EXPLOIT_STRUCTUREDTEXT)
  exploit_short_description = relationship('Exploit', uselist=False, secondary=_REL_EXPLOIT_STRUCTUREDTEXT_SHORT)
  infrastructure_description = relationship('Infrastructure', uselist=False, secondary=_REL_INFRASTRUCTURE_STRUCTUREDTEXT)
  infrastructure_short_description = relationship('Infrastructure', uselist=False, secondary=_REL_INFRASTRUCTURE_STRUCTUREDTEXT_SHORT)
  malware_instance_description = relationship('MalwareInstance', uselist=False, secondary=_REL_MALWAREINSTANCE_STRUCTUREDTEXT)
  malware_instance_short_description = relationship('MalwareInstance', uselist=False, secondary=_REL_MALWAREINSTANCE_STRUCTUREDTEXT_SHORT)
  campaign_description = relationship('Campaign', uselist=False, secondary=_REL_CAMPAIGN_STRUCTUREDTEXT)
  exploit_target_description = relationship('ExploitTarget', uselist=False, secondary=_REL_EXPLOITTARGET_STRUCTUREDTEXT)
  incident_description = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_STRUCTUREDTEXT)
  threatactor_description = relationship('ThreatActor', uselist=False, secondary=_REL_THREATACTOR_STRUCTUREDTEXT)
  ttp_description = relationship('TTP', uselist=False, secondary=_REL_TTP_STRUCTUREDTEXT)
  indicator_description = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_STRUCTUREDTEXT)
  campaign_short_description = relationship('Campaign', uselist=False, secondary=_REL_CAMPAIGN_STRUCTUREDTEXT_SHORT)
  exploit_target_short_description = relationship('ExploitTarget', uselist=False, secondary=_REL_EXPLOITTARGET_STRUCTUREDTEXT_SHORT)
  incident_short_description = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_STRUCTUREDTEXT_SHORT)
  threatactor_short_description = relationship('ThreatActor', uselist=False, secondary=_REL_THREATACTOR_STRUCTUREDTEXT_SHORT)
  ttp_short_description = relationship('TTP', uselist=False, secondary=_REL_TTP_STRUCTUREDTEXT_SHORT)
  indicator_short_description = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_STRUCTUREDTEXT_SHORT)
  report_description = relationship('Report', secondary=_REL_REPORT_STRUCTUREDTEXT, uselist=False)
  report_short_description = relationship('Report', secondary=_REL_REPORT_STRUCTUREDTEXT, uselist=False)


  def to_dict(self, cache_object):
    result = {'id_': self.convert_value(self.id_),
              'structuring_format': self.convert_value(self.structuring_format),
              'value':self.convert_value(self.value),
              'ordinality':self.convert_value(self.ordinality)
              }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
