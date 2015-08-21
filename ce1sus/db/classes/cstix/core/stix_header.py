# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 29, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.vocabs import PackageIntent as VocabPackageIntent
from ce1sus.db.classes.cstix.core.relations import _REL_STIXHEADER_STRUCTUREDTEXT, _REL_STIXHEADER_STRUCTUREDTEXT_SHORT, _REL_STIXHEADER_HANDLING, \
  _REL_STIXHEADER_INFORMATIONSOURCE
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.internal.corebase import BaseObject, BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class PackageIntent(BaseObject, Base):

  intent_id = Column('intent_id', Integer, default=None, nullable=False)
  stix_header_id = Column('stix_header_id', BigIntegerType, ForeignKey('stixheaders.stixheader_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  __intent = None

  _PARENTS = ['stix_header']
  stix_header = relationship('STIXHeader', uselist=False)

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
  package_intents = relationship(PackageIntent)
  title = Column('title', UnicodeType(255), index=True, nullable=False)
  description = relationship(StructuredText, secondary=_REL_STIXHEADER_STRUCTUREDTEXT, uselist=False)
  short_description = relationship(StructuredText, secondary=_REL_STIXHEADER_STRUCTUREDTEXT_SHORT, uselist=False)
  handling = relationship(MarkingSpecification, secondary=_REL_STIXHEADER_HANDLING)
  information_source = relationship(InformationSource, secondary=_REL_STIXHEADER_INFORMATIONSOURCE, uselist=False)
  # TODO: profiles

  _PARENTS = ['event']
  event = relationship('Event', uselist=False)

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
