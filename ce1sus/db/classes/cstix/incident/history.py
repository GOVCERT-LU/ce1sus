# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.incident.coa import COATaken
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeTextType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_HISTORYITEM_COATAKEN = Table('rel_historyitem_coataken', getattr(Base, 'metadata'),
                                    Column('rhict_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('coataken_id',
                                           BigIntegerType,
                                           ForeignKey('coatakens.coataken_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           index=True,
                                           nullable=False),
                                    Column('historyitem_id',
                                           BigIntegerType,
                                           ForeignKey('historyitems.historyitem_id',
                                                      ondelete='cascade',
                                                onupdate='cascade'),
                                           nullable=False,
                                           index=True)
                                    )



class JournalEntry(Entity, Base):

  value = Column('value', UnicodeTextType())
  author = Column('author', UnicodeType(255))

  time = Column('time', DateTime)
  time_precision = Column('time_precision', UnicodeType(10), default=u'second', nullable=False)

  historyitem_id = Column('historyitem_id', BigIntegerType, ForeignKey('historyitems.historyitem_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  _PARENTS = ['history_item']

  def to_dict(self, cache_object):

    result = {
              'value': self.convert_value(self.value),
              'journal_entry': self.attribute_to_dict(self.journal_entry, cache_object),
              'author': self.convert_value(self.author),
              'time': self.convert_value(self.time),
              'time_precision': self.convert_value(self.time_precision),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class HistoryItem(Entity, Base):
  action_entry = relationship(COATaken, uselist=False, secondary=_REL_HISTORYITEM_COATAKEN, backref='history_item')
  journal_entry = relationship(JournalEntry, uselist=False, backref='history_item')

  incident_id = Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  _PARENTS = ['incident']

  def to_dict(self, cache_object):

    result = {
              'action_entry': self.attribute_to_dict(self.action_entry, cache_object),
              'journal_entry': self.attribute_to_dict(self.journal_entry, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
