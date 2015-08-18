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
from ce1sus.db.classes.internal.corebase import UnicodeType, UnicodeTextType
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

  _PARENTS = ['stix_header_description',
              'stix_header_short_description',
              'information_source_description',
              'tool_information_description',
              'tool_information_short_description',
              'malware_instance_description',
              'malware_instance_short_description',
              'attack_pattern_description',
              'attack_pattern_short_description',
              'attack_pattern_description',
              'attack_exploit_short_description',
              'infrastructure_description',
              'infrastructure_short_description',
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
              'property_affacted_description',
              'objective_description',
              'objective_short_description']

  def to_dict(self, cache_object):
    result = {'id_': self.convert_value(self.id_),
              'structuring_format': self.convert_value(self.structuring_format),
              'value':self.convert_value(self.value),
              'ordinality':self.convert_value(self.ordinality)
              }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
