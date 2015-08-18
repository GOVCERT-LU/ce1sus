# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import DateTime, Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.vocabs import HighMediumLow
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_CONFIDENCE_STRUCTUREDTEXT = Table('rel_confidence_structuredtext', getattr(Base, 'metadata'),
                                       Column('rcst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('confidence_id',
                                              BigIntegerType,
                                              ForeignKey('confidences.confidence_id',
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

_REL_CONFIDENCE_INFORMATIONSOURCE = Table('rel_confidence_informationsource', getattr(Base, 'metadata'),
                                       Column('rcst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('confidence_id',
                                              BigIntegerType,
                                              ForeignKey('confidences.confidence_id',
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

class Confidence(Entity, Base):

  timestamp_precision = Column('timestamp_precision', UnicodeType(10), default=u'second')
  value_db = Column('confidence', Integer, default=3, nullable=False)

  description = relationship(StructuredText, secondary=_REL_CONFIDENCE_STRUCTUREDTEXT, uselist=False, lazy='joined', backref='confidence_description')
  source = relationship(InformationSource, secondary=_REL_CONFIDENCE_INFORMATIONSOURCE, uselist=False, backref='confidence')
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
              'related_relatedcoa',
              ]


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

