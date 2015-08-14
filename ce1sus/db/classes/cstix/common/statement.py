# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_STATEMENT_STRUCTUREDTEXT = Table('rel_statement_structuredtext', getattr(Base, 'metadata'),
                                      Column('rss_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                      Column('statement_id',
                                             BigIntegerType,
                                             ForeignKey('statements.statement_id',
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

_REL_STATEMENT_INFORMATIONSOURCE = Table('rel_statement_informationsource', getattr(Base, 'metadata'),
                                         Column('rss_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                         Column('statement_id',
                                                BigIntegerType,
                                                ForeignKey('statements.statement_id',
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

_REL_STATEMENT_CONFIDENCE = Table('rel_statement_confidence', getattr(Base, 'metadata'),
                                  Column('rss_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('statement_id',
                                         BigIntegerType,
                                         ForeignKey('statements.statement_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         index=True,
                                         nullable=False),
                                  Column('confidence_id',
                                         BigIntegerType,
                                         ForeignKey('confidences.confidence_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         nullable=False,
                                         index=True)
                                  )


class Statement(Entity, Base):

  timestamp = Column('timestamp', DateTime, default=datetime.utcnow())
  timestamp_precision = Column('timestamp_precision', UnicodeType(10), default=u'seconds')
  value = Column('value', UnicodeType(255), nullable=False)
  description = relationship(StructuredText, secondary=_REL_STATEMENT_STRUCTUREDTEXT, uselist=False, backref='statement_description')
  source = relationship(InformationSource, uselist=False, secondary=_REL_STATEMENT_INFORMATIONSOURCE, backref='statement')
  confidence = relationship(Confidence, uselist=False, secondary=_REL_STATEMENT_CONFIDENCE, backref='statement')
    
  _PARENTS = ['base_test_mechanism',
              'indicator',
              'coa_impact',
              'coa_cost',
              'coa_efficacy',
              'simple_marking_structure'
              ]

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'timestamp': self.convert_value(self.timestamp),
                'timestamp_precision': self.convert_value(self.timestamp_precision),
                'value': self.convert_value(self.value),
                'description': self.attribute_to_dict(self.description, cache_object),
                'source': self.attribute_to_dict(self.source, cache_object),
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
               }
    else:
      result = {
                'timestamp': self.convert_value(self.timestamp),
                'timestamp_precision': self.convert_value(self.timestamp_precision),
                'value': self.convert_value(self.value),
               }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
