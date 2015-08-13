# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.related import RelatedObservable
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_SIGHTING_REL_OBSERVABLE = Table('rel_sigthing_rel_observable', getattr(Base, 'metadata'),
                                        Column('rsro_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('sighting_id', BigIntegerType, ForeignKey('sightings.sighting_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                        Column('relatedobservable_id', BigIntegerType, ForeignKey('relatedobservables.relatedobservable_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_SIGHTING_STRUCTUREDTEXT = Table('rel_sighting_structuredtext', getattr(Base, 'metadata'),
                                       Column('rsst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('sighting_id',
                                              BigIntegerType,
                                              ForeignKey('sightings.sighting_id',
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

_REL_SIGHTING_CONFIDENCE = Table('rel_sighting_confidence', getattr(Base, 'metadata'),
                                        Column('rsc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('sighting_id', BigIntegerType, ForeignKey('sightings.sighting_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_SIGHTING_INFORMATIONSOURCE = Table('rel_sighting_informationsource', getattr(Base, 'metadata'),
                                       Column('rsis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('sighting_id',
                                              BigIntegerType,
                                              ForeignKey('sightings.sighting_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('informationsource_id',
                                             BigIntegerType,
                                             ForeignKey('informationsources.informationsource_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )

class Sighting(Entity, Base):
  timestamp = Column('timestamp', DateTime, default=datetime.utcnow())
  timestamp_precision = Column('timestamp_precision', UnicodeType(10), default=u'seconds')
  description = relationship(StructuredText, secondary=_REL_SIGHTING_STRUCTUREDTEXT, uselist=False)
  confidence = relationship(Confidence, secondary=_REL_SIGHTING_CONFIDENCE, uselist=False)
  # type reference = anyURI
  reference = Column('reference', UnicodeType(255))


  related_observables = relationship(RelatedObservable, secondary=_REL_SIGHTING_REL_OBSERVABLE)
  source = relationship(InformationSource, secondary=_REL_SIGHTING_INFORMATIONSOURCE, uselist=False)

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'timestamp': self.convert_value(self.timestamp),
                'timestamp_precision': self.convert_value(self.timestamp_precision),
                'description': self.attribute_to_dict(self.description, cache_object),
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
                'reference': self.convert_value(self.reference),
                'related_observables': self.attributelist_to_dict(self.related_observables, cache_object),
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
