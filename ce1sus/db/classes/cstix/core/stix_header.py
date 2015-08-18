# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 29, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.vocabs import PackageIntent as VocabPackageIntent
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.internal.corebase import BaseObject, BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_STIXHEADER_STRUCTUREDTEXT = Table('rel_stixheader_structuredtext', getattr(Base, 'metadata'),
                                       Column('rtstixheaderst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('stixheader_id',
                                              BigIntegerType,
                                              ForeignKey('stixheaders.stixheader_id',
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

_REL_STIXHEADER_STRUCTUREDTEXT_SHORT = Table('rel_stixheader_structuredtext_short', getattr(Base, 'metadata'),
                                       Column('rtstixheaderst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('stixheader_id',
                                              BigIntegerType,
                                              ForeignKey('stixheaders.stixheader_id',
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

_REL_STIXHEADER_INFORMATIONSOURCE = Table('rel_stixheader_informationsource', getattr(Base, 'metadata'),
                                       Column('rstixheaderis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('stixheader_id',
                                              BigIntegerType,
                                              ForeignKey('stixheaders.stixheader_id',
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

_REL_STIXHEADER_HANDLING = Table('rel_stixheader_handling', getattr(Base, 'metadata'),
                            Column('eih_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                            Column('stixheader_id', BigIntegerType, ForeignKey('stixheaders.stixheader_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                            Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                            )

class PackageIntent(BaseObject, Base):

  intent_id = Column('intent_id', Integer, default=None, nullable=False)
  stix_header_id = Column('stix_header_id', BigIntegerType, ForeignKey('stixheaders.stixheader_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  __intent = None

  _PARENTS = ['stix_header']

  @property
  def intent(self):
    if not self.__intent:
      if self.intent_id:
        self.__intent = VocabPackageIntent(self, 'intent_id')
    return self.__intent

  @intent.setter
  def intent(self, intent):
    if not self.intent:
      self.__intent = VocabPackageIntent(self, 'intent_id')
    self.__intent.name = intent

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'intent': self.convert_value(self.intent)}


class STIXHeader(Entity, Base):

  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  package_intents = relationship(PackageIntent, backref='stix_header')
  title = Column('title', UnicodeType(255), index=True, nullable=False)
  description = relationship(StructuredText, secondary=_REL_STIXHEADER_STRUCTUREDTEXT, uselist=False, backref='stix_header_description')
  short_description = relationship(StructuredText, secondary=_REL_STIXHEADER_STRUCTUREDTEXT_SHORT, uselist=False, backref='stix_header_short_description')
  handling = relationship(MarkingSpecification, secondary=_REL_STIXHEADER_HANDLING, backref='stix_header')
  information_source = relationship(InformationSource, secondary=_REL_STIXHEADER_INFORMATIONSOURCE, uselist=False, backref='stix_header')
  # TODO: profiles

  _PARENTS = ['event']

  def to_dict(self, cache_object):
    print self.description.parent
    if cache_object.complete:
      result = {'package_intents': self.attributelist_to_dict(self.package_intents, cache_object),
                'title': self.convert_value(self.title),
                'description': self.attribute_to_dict(self.description, cache_object),
                'short_description': self.attribute_to_dict(self.short_description, cache_object),
                'information_source': self.attribute_to_dict(self.information_source, cache_object),
                'handling': self.attributelist_to_dict(self.handling, cache_object),
                }
    else:
      result = {'title': self.convert_value(self.title),
                'information_source': self.attribute_to_dict(self.information_source, cache_object),
                'handling': self.attributelist_to_dict(self.handling, cache_object),
                }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
