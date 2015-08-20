# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.util import with_polymorphic
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint, Table
from sqlalchemy.types import Integer, DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.common.checks import is_event_owner
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.campaign.campaign import Campaign
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader
from ce1sus.db.classes.cstix.exploit_target.exploittarget import ExploitTarget
from ce1sus.db.classes.cstix.incident.incident import Incident
from ce1sus.db.classes.cstix.indicator.indicator import Indicator
from ce1sus.db.classes.cstix.threat_actor.threatactor import ThreatActor
from ce1sus.db.classes.cstix.ttp.ttp import TTP
from ce1sus.db.classes.internal.common import Status, Risk, Analysis
from ce1sus.db.classes.internal.core import ExtendedLogingInformations
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.classes.internal.errors.errorbase import ErrorBase
from ce1sus.db.classes.internal.report import Report
from ce1sus.db.classes.internal.usrmgt.group import EventPermissions
from ce1sus.db.common.session import Base
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_EVENT_RELATED_PACKAGES = Table('rel_event_relpackage', getattr(Base, 'metadata'),
                                    Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('event_id', BigIntegerType, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                    Column('relatedpackage_id', BigIntegerType, ForeignKey('relatedpackages.relatedpackage_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                    )

_REL_EVENT_OBSERVABLE = Table('rel_event_observable', getattr(Base, 'metadata'),
                                    Column('reo_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('event_id', BigIntegerType, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                    Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                    )

class EventGroupPermission(ExtendedLogingInformations, Base):
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
  group_id = Column('group_id', BigIntegerType, ForeignKey('groups.group_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  group = relationship('Group', primaryjoin='EventGroupPermission.group_id==Group.identifier')
  UniqueConstraint('event_id', 'group_id')

  @property
  def permissions(self):
    if self.dbcode:
      self.__bit_code = EventPermissions(self.dbcode, self)
    else:
      self.__bit_code = EventPermissions('0', self)
    return self.__bit_code

  @permissions.setter
  def permissions(self, value):
    self.__bit_code = value
    self.dbcode = value.bit_code
    self.__bit_code.parent = self

  def validate(self):
    # TODO: validate
    return True

  def to_dict(self, cache_object):
    return {'identifier': self.convert_value(self.uuid),
            'permissions': self.attribute_to_dict(self.permissions, cache_object),
            'group': self.group.to_dict(cache_object)}


class Event(Entity, Base):
  
  @hybrid_property
  def id_(self):
    return u'{0}:package-{1}'.format(self.namespace, self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  idref = Column(u'idref', UnicodeType(255), nullable=True, index=True)
  version_db = Column('version', UnicodeType(40), default=u'0.0.0', nullable=False)
  stix_header = relationship(STIXHeader, uselist=False, backref='event')
  campaigns = relationship(Campaign, backref='event')
  # TODO: courses_of_action
  courses_of_action = None
  exploit_targets = relationship(ExploitTarget, backref='event')
  observables = relationship(Observable, secondary=_REL_EVENT_OBSERVABLE, backref='event')
  indicators = relationship(Indicator, backref='event')
  incidents = relationship(Incident, backref='event')
  threat_actors = relationship(ThreatActor, backref='event')
  ttps = relationship(TTP, backref='event')
  related_packages = relationship('RelatedPackage', secondary=_REL_EVENT_RELATED_PACKAGES, backref='event')

  # reports are not in 1.1.5 -> custom one
  reports = relationship(Report, backref='event')
  
  # custom attributes
  status_id = Column('status_id', Integer, default=0, nullable=False)
  risk_id = Column('risk_id', Integer, nullable=False, default=0)
  analysis_id = Column('analysis_id', Integer, nullable=False, default=0)
  comments = relationship('Comment', backref='event')
  last_seen = Column(DateTime, default=datetime.utcnow(), nullable=False)
  first_seen = Column(DateTime, default=datetime.utcnow(), nullable=False)
  last_publish_date = Column('last_publish_date', DateTime)

  #ce1sus specific
  groups = relationship('EventGroupPermission', backref='event')
  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')
  errors = relationship(ErrorBase, backref='event')

  _PARENTS = ['related_package']

  @property
  def status(self):
    """
    returns the status

    :returns: String
    """
    return Status.get_by_id(self.status_id)

  @status.setter
  def status(self, status_text):
    """
    returns the status

    :returns: String
    """
    self.status_id = Status.get_by_value(status_text)

  @property
  def risk(self):
    """
    returns the status

    :returns: String
    """
    return Risk.get_by_id(self.risk_id)

  @risk.setter
  def risk(self, risk_text):
    """
    returns the status

    :returns: String
    """
    self.risk_id = Risk.get_by_value(risk_text)

  @property
  def analysis(self):
    """
    returns the status

    :returns: String
    """
    return Analysis.get_by_id(self.analysis_id)

  @analysis.setter
  def analysis(self, text):
    """
    returns the status

    :returns: String
    """
    self.analysis_id = Analysis.get_by_value(text)

  __version = None
  @property
  def version(self):
    if self.__version is None:
      self.__version = Version(self.version_db, self)
    return self.__version

  @version.setter
  def version(self, value):
    if self.__version is None:
      self.__version = Version(self.version_db, self)
    self.__version.version = value

  def validate(self):
    # TODO validation of an event
    return True

  def to_dict(self, cache_object):
    if is_event_owner(self, cache_object.user):
      comments = self.attributelist_to_dict(self.comments, cache_object)
    else:
      comments = list()
    
    if cache_object.complete:
      result = {'id_':self.convert_value(self.id_),
                'int_id': self.convert_value(self.identifier),
                'analysis': self.convert_value(self.analysis),
                'campaigns':self.attributelist_to_dict(self.campaigns, cache_object),
                'comments':comments,
                'courses_of_action':self.attributelist_to_dict(self.courses_of_action, cache_object),
                'exploit_targets':self.attributelist_to_dict(self.exploit_targets, cache_object),
                'last_seen': self.convert_value(self.last_seen),
                'first_seen': self.convert_value(self.first_seen),
                'groups': self.attributelist_to_dict(self.groups, cache_object),
                'idref':self.convert_value(self.idref),
                'incidents':self.attributelist_to_dict(self.incidents, cache_object),
                'indicators':self.attributelist_to_dict(self.indicators, cache_object),
                'last_publish_date': self.convert_value(self.last_publish_date),
                'observables':self.attributelist_to_dict(self.observables, cache_object),
                'related_packages':self.attributelist_to_dict(self.related_packages, cache_object),
                'reports':self.attributelist_to_dict(self.reports, cache_object),
                'risk': self.convert_value(self.risk),
                'status': self.convert_value(self.status),
                'stix_header': self.attribute_to_dict(self.stix_header, cache_object),
                'published': self.convert_value(self.properties.is_shareable),
                'threat_actors':self.attributelist_to_dict(self.threat_actors, cache_object),
                'ttps':self.attributelist_to_dict(self.ttps, cache_object),
                'version':self.convert_value(self.version_db),
                'errors':self.attributelist_to_dict(self.errors, cache_object)
                }
    else:
      result = {'id_':self.convert_value(self.id_),
                'int_id': self.convert_value(self.identifier),
                'analysis': self.convert_value(self.analysis),
                'comments':comments,
                'last_seen': self.convert_value(self.last_seen),
                'first_seen': self.convert_value(self.first_seen),
                'idref':self.convert_value(self.idref),
                'last_publish_date': self.convert_value(self.last_publish_date),
                'risk': self.convert_value(self.risk),
                'status': self.convert_value(self.status),
                'stix_header': self.attribute_to_dict(self.stix_header, cache_object),
                'published': self.convert_value(self.properties.is_shareable),
                'version':self.convert_value(self.version_db),
                'errors':self.attributelist_to_dict(self.errors, cache_object)
                }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


class Comment(ExtendedLogingInformations, Base):
  event_id = Column(BigIntegerType, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  comment = Column('comment', UnicodeTextType(), nullable=False)

  def to_dict(self, cache_object):
    result = {
              'comment': self.convert_value(self.comment),
              }
    parent_dict = ExtendedLogingInformations.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

  def validate(self):
    # TODO: Validation of comments
    return True
