# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 8, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, Boolean, Integer, BigInteger

from ce1sus.common.checks import is_object_viewable
from ce1sus.db.classes.basedbobject import ExtendedLogingInformations, SimpleLogingInformations
from ce1sus.db.classes.common import Properties, ValueException
from ce1sus.db.common.session import Base
from ce1sus.handlers.base import HandlerBase, HandlerException
from ce1sus.helpers.common.objects import get_class


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

# Note: This is not yet part of STIX should be on 1.2


class ReferenceHandler(Base):

  module_classname = Column('moduleClassName', Unicode(255), nullable=False, unique=True, index=True)
  description = Column('description', UnicodeText, nullable=False)

  @property
  def classname(self):
    """
    Returns the class name of the handler
    """
    return self.module_classname.rsplit('.', 1)[1]

  @property
  def module(self):
    """
    Returns the module of the handler
    """
    return self.module_classname.rsplit('.', 1)[0]

  @property
  def clazz(self):
    clazz = get_class('ce1sus.handlers.references.{0}'.format(self.module), self.classname)
    return clazz

  def create_instance(self):
    """
    creates an instantiated object
    """
    # instantiate
    handler = self.clazz()
    # check if handler base is implemented
    if not isinstance(handler, HandlerBase):
      raise HandlerException((u'{0} does not implement '
                              + 'HandlerBase').format(self.module_classname))
    return handler

  def validate(self):
    # TODO: Verify validation of ReferenceHandler Object
    return True

  def to_dict(self, complete=False, inflated=False):
    return {'description': self.convert_value(self.description),
            'name': self.convert_value(self.classname),
            'identifier': self.convert_value(self.uuid)
            }


class ReferenceDefinition(SimpleLogingInformations, Base):

  name = Column('name', Unicode(45), unique=True, nullable=False, index=True)
  description = Column('description', UnicodeText)
  chksum = Column('chksum', Unicode(45), unique=True, nullable=False, index=True)
  regex = Column('regex', Unicode(255), nullable=False, default=u'^.+$')

  referencehandler_id = Column('referencehandler_id', BigInteger, ForeignKey('referencehandlers.referencehandler_id', onupdate='restrict', ondelete='restrict'), index=True, nullable=False)
  reference_handler = relationship('ReferenceHandler',
                                   primaryjoin='ReferenceHandler.identifier==ReferenceDefinition.referencehandler_id',
                                   lazy='joined',
                                   cascade='all')
  share = Column('sharable', Boolean, default=False, nullable=False)

  __handler = None

  @property
  def handler(self):
    """
    Returns the instantiatied handler
    """
    if self.__handler is None:
      self.__handler = getattr(self.reference_handler, 'create_instance')()
    return self.__handler

  def validate(self):
    # TODO: Validate
    return True

  def to_dict(self, complete=True, inflated=False):
    if complete:
      return {'identifier': self.convert_value(self.uuid),
              'name': self.convert_value(self.name),
              'description': self.convert_value(self.description),
              'referencehandler_id': self.convert_value(self.reference_handler.uuid),
              'reference_handler': self.handler.to_dict(),
              'share': self.convert_value(self.share),
              'regex': self.convert_value(self.regex),
              'chksum': self.convert_value(self.chksum),
              }
    else:
      return {'identifier': self.uuid,
              'name': self.name
              }

  def populate(self, json):
    self.name = json.get('name', None)
    self.description = json.get('description', None)
    share = json.get('share', False)
    self.share = share
    self.regex = json.get('regex', None)


class Reference(ExtendedLogingInformations, Base):
  # Similar approach as for attributes
  report = relationship('Report', uselist=False, primaryjoin='Reference.report_id==Report.identifier')
  report_id = Column('report_id', BigInteger, ForeignKey('reports.report_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)
  definition_id = Column('definition_id', BigInteger,
                         ForeignKey('referencedefinitions.referencedefinition_id', onupdate='cascade', ondelete='restrict'), nullable=False, index=True)
  definition = relationship(ReferenceDefinition,
                            primaryjoin='ReferenceDefinition.identifier==Reference.definition_id')
  dbcode = Column('code', Integer, nullable=False, default=0)
  value = Column('value', UnicodeText, nullable=False)
  parent_id = Column('parent_id', BigInteger, ForeignKey('references.reference_id', onupdate='cascade', ondelete='SET NULL'), index=True, default=None)
  children = relationship('Reference',
                          primaryjoin='Reference.identifier==Reference.parent_id')
  __bit_code = None

  def populate(self, json, rest_insert=True):
    definition_uuid = json.get('definition_id', None)
    if not definition_uuid:
      definition = json.get('definition', None)
      if definition:
        definition_uuid = definition.get('identifier', None)
    if self.definition:
      if self.definition.uuid != definition_uuid:
        raise ValueException(u'Reference definitions cannot be updated')
    self.value = json.get('value', None)
    self.properties.populate(json.get('properties', None))
    self.properties.is_rest_instert = rest_insert
    self.properties.is_web_insert = not rest_insert

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    return {'identifier': self.convert_value(self.uuid),
            'definition_id': self.convert_value(self.definition.uuid),
            'definition': self.definition.to_dict(complete, inflated),
            'value': self.convert_value(self.value),
            'creator_group': self.creator_group.to_dict(complete, False),
            'created_at': self.convert_value(self.created_at),
            'modified_on': self.convert_value(self.modified_on),
            'modifier_group': self.modifier.group.to_dict(complete, False),
            'properties': self.properties.to_dict()
            }

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
    # TODO create validation
    return True


class Report(ExtendedLogingInformations, Base):

  title = Column('title', Unicode(255), index=True)
  description = Column('description', UnicodeText)
  short_description = Column('short_description', Unicode(255))
  parent_report_id = Column('parent_report_id', BigInteger, ForeignKey('reports.report_id', onupdate='cascade', ondelete='cascade'), index=True)
  parent_report = relationship('Report', uselist=False, primaryjoin='Report.parent_report_id==Report.identifier')
  event = relationship('Event', uselist=False, primaryjoin='Report.event_id==Event.identifier')
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)

  references = relationship('Reference')
  dbcode = Column('code', Integer, nullable=False, default=0)
  related_reports = relationship('Report', primaryjoin='Report.parent_report_id==Report.identifier', lazy='dynamic')

  __bit_code = None

  def references_count_for_permissions(self, event_permissions, user):
    return len(self.get_references_for_permissions(event_permissions, user))

  def related_reports_count_for_permissions(self, event_permissions, user):
    return len(self.get_related_reports_for_permissions(event_permissions, user))

  def get_references_for_permissions(self, event_permissions, user):
    references = list()
    for ref in self.references:
      if is_object_viewable(ref, event_permissions):
        references.append(ref)
      else:
        if ref.creator.identifier == user.identifier:
          references.append(ref)
    return references

  def get_related_reports_for_permissions(self, event_permissions, user):
    rel_reps = list()
    for rel_rep in self.related_reports:
      if is_object_viewable(rel_rep, event_permissions):
        rel_reps.append(rel_rep)
      else:
        if rel_rep.creator.identifier == user.identifier:
          rel_reps.append(rel_rep)
    return rel_reps

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    references = list()
    related_reports = list()
    for reference in self.get_references_for_permissions(event_permissions, user):
      references.append(reference.to_dict(complete, inflated, event_permissions, user))

    if references:
      references_count = len(references)
    else:
      references_count = self.references_count_for_permissions(event_permissions, user)

    if inflated:
      for related_report in self.get_related_reports_for_permissions(event_permissions, user):
        related_reports.append(related_report.to_dict(complete, inflated, event_permissions, user))
      related_count = len(related_reports)
    else:
      related_count = self.related_reports_count_for_permissions(event_permissions, user)
    if complete:
      return {'identifier': self.convert_value(self.uuid),
              'title': self.convert_value(self.title),
              'description': self.convert_value(self.description),
              'short_description': self.convert_value(self.short_description),
              'creator_group': self.creator_group.to_dict(complete, False),
              'modifier_group': self.modifier.group.to_dict(complete, False),
              # TODO references
              'references': references,
              'references_count': references_count,
              'properties': self.properties.to_dict(),
              # TODO related_reports
              'related_reports': related_reports,
              'related_reports_count': related_count,
              }
    else:
      return {'identifier': self.identifier,
              'title': self.title
              }

  def populate(self, json, rest_insert=True):
    self.title = json.get('title', None)
    self.description = json.get('description', None)
    self.properties.populate(json.get('properties', None))
    # TODO inflated
    self.short_description = json.get('short_description', None)
    self.properties.is_rest_instert = rest_insert
    self.properties.is_web_insert = not rest_insert

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
    # TODO create validation
    return True
