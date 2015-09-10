# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, lazyload, joinedload, lazyload_all
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import Integer, DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.campaign.campaign import Campaign
from ce1sus.db.classes.cstix.common.related import RelatedPackage
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
from ce1sus.db.classes.internal.relations import _REL_EVENT_OBSERVABLE, _REL_EVENT_RELATED_PACKAGES, _REL_EVENT_INDICATOR
from ce1sus.db.classes.internal.report import Report
from ce1sus.db.classes.internal.usrmgt.group import EventPermissions
from ce1sus.db.common.session import Base
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventGroupPermission(ExtendedLogingInformations, Base):
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
  group_id = Column('group_id', BigIntegerType, ForeignKey('groups.group_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  group = relationship('Group', primaryjoin='EventGroupPermission.group_id==Group.identifier')
  UniqueConstraint('event_id', 'group_id')

  event = relationship('Event', uselist=False)

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
  stix_header = relationship(STIXHeader, uselist=False)
  campaigns = relationship(Campaign)
  # TODO: courses_of_action
  courses_of_action = None
  exploit_targets = relationship(ExploitTarget)
  observables = relationship(Observable, secondary=_REL_EVENT_OBSERVABLE, back_populates='event')
  indicators = relationship(Indicator, secondary=_REL_EVENT_INDICATOR, back_populates='event')
  incidents = relationship(Incident)
  threat_actors = relationship(ThreatActor)
  ttps = relationship(TTP)
  related_packages = relationship('RelatedPackage', secondary=_REL_EVENT_RELATED_PACKAGES)

  # reports are not in 1.1.5 -> custom one
  reports = relationship(Report)
  
  # custom attributes
  status_id = Column('status_id', Integer, default=0, nullable=False)
  risk_id = Column('risk_id', Integer, nullable=False, default=0)
  analysis_id = Column('analysis_id', Integer, nullable=False, default=0)
  comments = relationship('Comment')
  last_seen = Column(DateTime, default=datetime.utcnow(), nullable=False)
  first_seen = Column(DateTime, default=datetime.utcnow(), nullable=False)
  last_publish_date = Column('last_publish_date', DateTime)

  #ce1sus specific
  groups = relationship('EventGroupPermission')
  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')
  errors = relationship(ErrorBase)

  _PARENTS = ['related_package']
  related_package = relationship(RelatedPackage, primaryjoin='RelatedPackage.child_id==Event.identifier', uselist=False)

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
    instance = self.get_instance([Event.stix_header], cache_object)

    if cache_object.permission_controller.is_instance_owner(self, cache_object):
      comments = instance.attributelist_to_dict('comments', cache_object)
    else:
      comments = list()

    if cache_object.complete:

      result = {'id_':instance.convert_value(instance.id_),
                'int_id': instance.convert_value(instance.identifier),
                'analysis': instance.convert_value(instance.analysis),
                'campaigns':instance.attributelist_to_dict('campaigns', cache_object),
                'comments':comments,
                'courses_of_action':instance.attributelist_to_dict('courses_of_action', cache_object),
                'exploit_targets':instance.attributelist_to_dict('exploit_targets', cache_object),
                'last_seen': instance.convert_value(instance.last_seen),
                'first_seen': instance.convert_value(instance.first_seen),
                'groups': instance.attributelist_to_dict('groups', cache_object),
                'idref':instance.convert_value(instance.idref),
                'incidents':instance.attributelist_to_dict('incidents', cache_object),
                'indicators':instance.attributelist_to_dict('indicators', cache_object),
                'last_publish_date': instance.convert_value(instance.last_publish_date),
                'observables':instance.attributelist_to_dict('observables', cache_object),
                'related_packages':instance.attributelist_to_dict('related_packages', cache_object),
                'reports':instance.attributelist_to_dict('reports', cache_object),
                'risk': instance.convert_value(instance.risk),
                'status': instance.convert_value(instance.status),
                'stix_header': instance.attribute_to_dict(instance.stix_header, cache_object),
                'published': instance.convert_value(instance.properties.is_shareable),
                'threat_actors':instance.attributelist_to_dict('threat_actors', cache_object),
                'ttps':instance.attributelist_to_dict('ttps', cache_object),
                'version':instance.convert_value(instance.version_db),
                'errors':instance.attributelist_to_dict('errors', cache_object)
                }
    else:
      result = {'id_':instance.convert_value(instance.id_),
                'int_id': instance.convert_value(instance.identifier),
                'analysis': instance.convert_value(instance.analysis),
                'comments':comments,
                'last_seen': instance.convert_value(instance.last_seen),
                'first_seen': instance.convert_value(instance.first_seen),
                'idref':instance.convert_value(instance.idref),
                'last_publish_date': instance.convert_value(instance.last_publish_date),
                'risk': instance.convert_value(instance.risk),
                'status': instance.convert_value(instance.status),
                'stix_header': instance.attribute_to_dict(instance.stix_header, cache_object),
                'published': instance.convert_value(instance.properties.is_shareable),
                'version':instance.convert_value(instance.version_db),
                'errors':instance.attributelist_to_dict('errors', cache_object)
                }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


class Comment(ExtendedLogingInformations, Base):
  event_id = Column(BigIntegerType, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  comment = Column('comment', UnicodeTextType(), nullable=False)
  event = relationship('Event', uselist=False)

  def to_dict(self, cache_object):
    result = {
              'comment': self.convert_value(self.comment),
              }
    parent_dict = ExtendedLogingInformations.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

  def validate(self):
    # TODO: Validation of comments
    return True
