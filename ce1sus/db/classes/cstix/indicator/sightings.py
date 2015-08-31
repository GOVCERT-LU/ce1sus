# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.indicator.relations import _REL_SIGHTING_STRUCTUREDTEXT, _REL_SIGHTING_CONFIDENCE, _REL_SIGHTING_REL_OBSERVABLE, \
  _REL_SIGHTING_INFORMATIONSOURCE
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'



class Sighting(Entity, Base):
  timestamp = Column('timestamp', DateTime, default=datetime.utcnow())
  timestamp_precision = Column('timestamp_precision', UnicodeType(10), default=u'seconds')
  description = relationship('StructuredText', secondary=_REL_SIGHTING_STRUCTUREDTEXT, uselist=False)
  confidence = relationship(Confidence, secondary=_REL_SIGHTING_CONFIDENCE, uselist=False)
  # type reference = anyURI
  reference = Column('reference', UnicodeType(255))


  related_observables = relationship('RelatedObservable', secondary=_REL_SIGHTING_REL_OBSERVABLE)
  source = relationship('InformationSource', secondary=_REL_SIGHTING_INFORMATIONSOURCE, uselist=False)

  indicator_id = Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  indicator = relationship('Indicator', uselist=False)
  _PARENTS = ['indicator']

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'timestamp': self.convert_value(self.timestamp),
                'timestamp_precision': self.convert_value(self.timestamp_precision),
                'description': self.attribute_to_dict(self.description, cache_object),
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
                'reference': self.convert_value(self.reference),
                'related_observables': self.attributelist_to_dict('related_observables', cache_object),
                'source': self.attribute_to_dict(self.source, cache_object)
                }
    else:
      result = {
                'timestamp': self.convert_value(self.timestamp),
                'timestamp_precision': self.convert_value(self.timestamp_precision),
                'source': self.attribute_to_dict(self.source, cache_object)
                }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
