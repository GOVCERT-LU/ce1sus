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
from ce1sus.db.common.broker import DateTime
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_INDICATOR_SIGHTINGS = Table('rel_indicator_sightings', Base.metadata,
                                 Column('ris_id', BigInteger, primary_key=True, nullable=False, index=True),
                                 Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                 Column('sighting_id', BigInteger, ForeignKey('sightings.sighting_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                 )

_REL_INDICATOR_TYPE = Table('rel_indicator_types', Base.metadata,
                            Column('rit_id', BigInteger, primary_key=True, nullable=False, index=True),
                            Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                            Column('indicatortype_id', BigInteger, ForeignKey('indicatortypes.indicatortype_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                            )


_REL_INDICATOR_KILLCHAINPHASE = Table('rel_indicator_killchainphase', Base.metadata,
                                      Column('rik_id', BigInteger, primary_key=True, nullable=False, index=True),
                                      Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                      Column('killchainphase_id', BigInteger, ForeignKey('killchainphases.killchainphase_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                      )

_REL_INDICATOR_OBSERVABLE = Table('rel_indicator_observable', Base.metadata,
                                  Column('rio_id', BigInteger, primary_key=True, nullable=False, index=True),
                                  Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                  Column('observable_id', BigInteger, ForeignKey('observables.observable_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                  )


class KillChainPhase(Base):
  # TODO enlarge, add the missing elements
  name = Column('name', Unicode(255))
  ordinality = Column('ordinality', Integer(1))


class Sighting(ExtendedLogingInformations, Base):
  timestamp_precision = Column('timestamp_precision', BigInteger)
  description = Column('description', UnicodeText)
  confidence = Column('confidence', Unicode(5), default=u'HIGH', nullable=False)
  dbcode = Column('code', Integer, default=0, nullable=False)
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


class IndicatorType(Base):
  name = Column('name', Unicode(255), nullable=False, unique=True)
  description = Column('description', UnicodeText)

  def to_dict(self, complete=True, inflated=False):
    if complete:
      return {'identifier': self.convert_value(self.uuid),
              'name': self.convert_value(self.name),
              'description': self.convert_value(self.description)}
    else:
      return {'identifier': self.convert_value(self.uuid),
              'name': self.convert_value(self.name)}


class ValidTimePosition(ExtendedLogingInformations, Base):
  start_time = Column('start_time', DateTime, nullable=False)
  end_time = Column('end_time', DateTime, nullable=False)
  indicator_id = Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  dbcode = Column('code', Integer, default=0, nullable=False)
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


class Indicator(ExtendedLogingInformations, Base):

  version = Column('version', BigInteger, default=u'1.0.0', nullable=False)
  title = Column('title', Unicode(255), index=True, nullable=True)
  description = Column('description', UnicodeText)
  short_description = Column('short_description', Unicode(255))
  confidence = Column('confidence', Unicode(5), default=u'HIGH', nullable=False)
  # TODO relation tables
  # TODO Markings
  event = relationship('Event', uselist=False)
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  sightings = relationship('Sighting', secondary='rel_indicator_sightings')
  killchain = relationship('KillChainPhase', secondary='rel_indicator_killchainphase')
  type_ = relationship('IndicatorType', secondary='rel_indicator_types')
  operator = Column('operator', Unicode(3), default=u'OR')
  observables = relationship('Observable', secondary='rel_indicator_observable')  # 1:*
  valid_time_positions = relationship('ValidTimePosition')  # 1:*
  # TODO add related indicators and TTP
  dbcode = Column('code', Integer, default=0, nullable=False)
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
