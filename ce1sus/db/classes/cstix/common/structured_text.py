# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.core import UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base


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

  @property
  def parent(self):
    if self.stix_header_description:
      return self.stix_header_description
    elif self.stix_header_short_description:
      return self.stix_header_short_description

    elif self.information_source_description:
      return self.information_source_description

    elif self.tool_information_description:
      return self.tool_information_description
    elif self.tool_information_short_description:
      return self.tool_information_short_description

    elif self.malware_instance_description:
      return self.malware_instance_description
    elif self.malware_instance_short_description:
      return self.malware_instance_short_description

    elif self.attack_pattern_description:
      return self.attack_pattern_description
    elif self.attack_pattern_short_description:
      return self.attack_pattern_short_description

    elif self.attack_exploit_description:
      return self.attack_pattern_description
    elif self.attack_exploit_short_description:
      return self.attack_exploit_short_description

    elif self.infrastructure_description:
      return self.infrastructure_description
    elif self.infrastructure_short_description:
      return self.infrastructure_short_description

    elif self.vulnerability_description:
      return self.vulnerability_description
    elif self.vulnerability_short_description:
      return self.vulnerability_short_description

    elif self.configuration_description:
      return self.configuration_description
    elif self.configuration_short_description:
      return self.configuration_short_description

    elif self.confidence_description:
      return self.confidence_description

    elif self.statement_description:
      return self.statement_description

    elif self.generic_test_meachanism_description:
      return self.generic_test_meachanism_description

    elif self.sighting_description:
      return self.sighting_description

    elif self.activity_description:
      return self.activity_description

    elif self.affected_asset_description:
      return self.affected_asset_description
    elif self.affected_asset_short_description:
      return self.affected_asset_short_description

    elif self.property_affacted_description:
      return self.property_affacted_description

    elif self.objective_description:
      return self.objective_description
    elif self.objective_short_description:
      return self.objective_short_description

    raise ValueError('Parent not found')

  def to_dict(self, cache_object):
    result = {'id_': self.convert_value(self.id_),
              'structuring_format': self.convert_value(self.structuring_format),
              'value':self.convert_value(self.value),
              'ordinality':self.convert_value(self.ordinality)
              }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
