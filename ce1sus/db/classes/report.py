# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 8, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, Boolean, Integer

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
            'identifier': self.convert_value(self.identifier)
            }


class ReferenceDefinition(SimpleLogingInformations, Base):

  name = Column('name', Unicode(45), unique=True, nullable=False, index=True)
  description = Column('description', UnicodeText)
  chksum = Column('chksum', Unicode(45), unique=True, nullable=False, index=True)
  regex = Column('regex', Unicode(255), nullable=False, default=u'^.+$')

  referencehandler_id = Column('referencehandler_id', Unicode(40), ForeignKey('referencehandlers.referencehandler_id', onupdate='restrict', ondelete='restrict'), index=True, nullable=False)
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
      return {'identifier': self.convert_value(self.identifier),
              'name': self.convert_value(self.name),
              'description': self.convert_value(self.description),
              'referencehandler_id': self.convert_value(self.referencehandler_id),
              'reference_handler': self.handler.to_dict(),
              'share': self.convert_value(self.share),
              'regex': self.convert_value(self.regex),
              'chksum': self.convert_value(self.chksum),
              }
    else:
      return {'identifier': self.identifier,
              'name': self.name
              }

  def populate(self, json):
    self.name = json.get('name', None)
    self.description = json.get('description', None)
    self.referencehandler_id = json.get('referencehandler_id', None)
    share = json.get('share', False)
    self.share = share
    self.regex = json.get('regex', None)


class Reference(ExtendedLogingInformations, Base):
  # Similar approach as for attributes
  report = relationship('Report', uselist=False, primaryjoin='Reference.report_id==Report.identifier')
  report_id = Column('event_id', Unicode(40), ForeignKey('reports.report_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)
  definition_id = Column('definition_id', Unicode(40),
                         ForeignKey('referencedefinitions.referencedefinition_id', onupdate='cascade', ondelete='restrict'), nullable=False, index=True)
  definition = relationship(ReferenceDefinition,
                            primaryjoin='ReferenceDefinition.identifier==Reference.definition_id')
  dbcode = Column('code', Integer, nullable=False, default=0)
  value = Column('value', Unicode(255), nullable=False, index=True)
  parent_id = Column('parent_id', Unicode(40), ForeignKey('references.reference_id', onupdate='cascade', ondelete='SET NULL'), index=True, default=None)
  children = relationship('Reference',
                          primaryjoin='Reference.identifier==Reference.parent_id')
  __bit_code = None

  def populate(self, json):
    definition_id = json.get('definition_id', None)
    if not definition_id:
      definition = json.get('definition', None)
      if definition:
        definition_id = definition.get('identifier', None)
    if self.definition_id:
      if self.definition_id != definition_id:
        raise ValueException(u'Reference definitions cannot be updated')
    if definition_id:
      self.definition_id = definition_id
    self.value = json.get('value', None)
    self.properties.populate(json.get('properties', None))

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    return {'identifier': self.convert_value(self.identifier),
            'definition_id': self.convert_value(self.definition_id),
            'definition': self.definition.to_dict(complete, inflated),
            'value': self.convert_value(self.value),
            'creator_group': self.creator_group.to_dict(complete, inflated),
            'created_at': self.convert_value(self.created_at),
            'modified_on': self.convert_value(self.modified_on),
            'modifier_group': self.convert_value(self.modifier.group.to_dict(complete, inflated)),
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
  parent_report_id = Column('parent_report_id', Unicode(40), ForeignKey('reports.report_id', onupdate='cascade', ondelete='cascade'), index=True)
  parent_report = relationship('Report', uselist=False, primaryjoin='Report.parent_report_id==Report.identifier')
  event = relationship('Event', uselist=False, primaryjoin='Report.event_id==Event.identifier')
  event_id = Column('event_id', Unicode(40), ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)

  references = relationship('Reference', lazy='dynamic')
  dbcode = Column('code', Integer, nullable=False, default=0)
  related_reports = relationship('Report', primaryjoin='Report.parent_report_id==Report.identifier', lazy='dynamic')

  __bit_code = None

  def references_count_for_permissions(self, event_permissions):
    if event_permissions:
      if event_permissions.can_validate:
        return self.references.count()
      else:
        # count validated ones
        return self.references.filter(Reference.dbcode.op('&')(1) == 1).count()
    else:
      # count shared and validated
      return self.references.filter(Reference.dbcode.op('&')(3) == 3).count()

  def related_reports_count_for_permissions(self, event_permissions):
    if event_permissions:
      if event_permissions.can_validate:
        return self.related_reports.count()
      else:
        # count validated ones
        return self.related_reports.filter(Report.dbcode.op('&')(1) == 1).count()
    else:
      # count shared and validated
      return self.related_reports.filter(Report.dbcode.op('&')(3) == 3).count()

  def get_references_for_permissions(self, event_permissions):
    if event_permissions:
      if event_permissions.can_validate:
        return self.references.all()
      else:
        # count validated ones
        return self.references.filter(Reference.dbcode.op('&')(1) == 1).all()
    else:
      # count shared and validated
      return self.references.filter(Reference.dbcode.op('&')(3) == 3).all()

  def get_related_reports_for_permissions(self, event_permissions):
    if event_permissions:
      if event_permissions.can_validate:
        return self.related_reports.all()
      else:
        # count validated ones
        return self.related_reports.filter(Report.dbcode.op('&')(1) == 1).all()
    else:
      # count shared and validated
      return self.related_reports.filter(Report.dbcode.op('&')(3) == 3).all()

  def to_dict(self, complete=True, inflated=False, event_permissions=None):
    references = list()
    related_reports = list()
    for reference in self.get_references_for_permissions(event_permissions):
      references.append(reference.to_dict(complete, inflated, event_permissions))

    if references:
      references_count = len(references)
    else:
      references_count = self.references_count_for_permissions(event_permissions)

    if inflated:
      for related_report in self.get_related_reports_for_permissions(event_permissions):
        related_reports.append(related_report.to_dict(complete, inflated, event_permissions))
      related_count = len(related_reports)
    else:
      related_count = self.related_reports_count_for_permissions(event_permissions)
    if complete:
      return {'identifier': self.convert_value(self.identifier),
              'title': self.convert_value(self.title),
              'description': self.convert_value(self.description),
              'short_description': self.convert_value(self.short_description),
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

  def populate(self, json):
    self.title = json.get('title', None)
    self.description = json.get('description', None)
    self.properties.populate(json.get('properties', None))
    # TODO inflated
    self.short_description = json.get('short_description', None)

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