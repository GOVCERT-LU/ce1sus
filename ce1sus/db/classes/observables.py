# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Unicode, UnicodeText, Integer, BigInteger

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Properties
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ObservableKeyword(Base):
  observable_id = Column('observable_id', Unicode(40), ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False)
  keyword = Column('keyword', Unicode(255), nullable=False, index=True)


_REL_OBSERVABLE_COMPOSITION = Table('rel_observable_composition', Base.metadata,
                                    Column('roc_id', BigInteger, primary_key=True, nullable=False, index=True),
                                    Column('observablecomposition_id', Unicode(40), ForeignKey('observablecompositions.observablecomposition_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                    Column('child_id', Unicode(40), ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
                                    )


class ObservableComposition(Base):
  parent_id = Column('parent_id', Unicode(40), ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  operator = Column('operator', Unicode(3), default=u'AND')
  observables = relationship('Observable', secondary='rel_observable_composition')

  def validate(self):
    return True


class Observable(ExtendedLogingInformations, Base):

  title = Column('title', Unicode(255), index=True, unique=True)
  description = Column('description', UnicodeText)
  object = relationship('Object', back_populates='parent', uselist=False)
  observable_composition = relationship('ObservableComposition', uselist=False)
  keywords = relationship('ObservableKeyword', backref='observable')
  event = relationship('Event', uselist=False)
  event_id = Column('event_id', Unicode(40), ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), index=True)
  version = Column('version', Unicode(40), default=u'1.0.0', nullable=False)
  dbcode = Column('code', Integer)
  __bit_code = None

  @property
  def properties(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = Properties('0', self)
      else:
        self.__bit_code = Properties(self.dbcode, self)
    return self.__bit_code

  def validate(self):
    return True

  def to_dict(self, complete=True):
    return {'identifier': self.convert_value(self.identifier),
            'title': self.convert_value(self.title),
            'description': self.convert_value(self.description),
            'creator_group': self.creator_group.to_dict(False),
            'created_at': self.convert_value(self.created_at),
            }
