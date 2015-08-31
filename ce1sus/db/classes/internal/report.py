# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 8, 2015
"""
from base64 import b64encode
from ce1sus.helpers.common.objects import get_class
from os.path import isfile
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Boolean

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.core import SimpleLoggingInformations, BaseElement
from ce1sus.db.classes.internal.corebase import BaseObject, UnicodeType, UnicodeTextType, BigIntegerType
from ce1sus.db.classes.internal.relations import _REL_REPORT_STRUCTUREDTEXT, _REL_REPORT_STRUCTUREDTEXT_SHORT
from ce1sus.db.common.session import Base
from ce1sus.handlers.base import HandlerBase, HandlerException
from ce1sus.helpers.common.hash import fileHashSHA1


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

# Note: This is not yet part of STIX should be on 1.2


class ReferenceHandler(BaseObject, Base):

  module_classname = Column('moduleClassName', UnicodeType(255), nullable=False, unique=True, index=True)
  description = Column('description', UnicodeTextType(), nullable=False)

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

  def to_dict(self, cache_object):

    result = {'description': self.convert_value(self.description),
            'name': self.convert_value(self.classname),
            }

    parent_dict = BaseObject.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


class ReferenceDefinition(SimpleLoggingInformations, Base):

  name = Column('name', UnicodeType(45), unique=True, nullable=False, index=True)
  description = Column('description', UnicodeTextType())
  chksum = Column('chksum', UnicodeType(45), unique=True, nullable=False, index=True)
  regex = Column('regex', UnicodeType(255), nullable=False, default=u'^.+$')

  referencehandler_id = Column('referencehandler_id', BigIntegerType, ForeignKey('referencehandlers.referencehandler_id', onupdate='restrict', ondelete='restrict'), index=True, nullable=False)
  reference_handler = relationship('ReferenceHandler',
                                   primaryjoin='ReferenceHandler.identifier==ReferenceDefinition.referencehandler_id',
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

  def to_dict(self, cache_object):

    if cache_object.complete:
      result= {
              'name': self.convert_value(self.name),
              'description': self.convert_value(self.description),
              'referencehandler_id': self.convert_value(self.reference_handler.uuid),
              'reference_handler': self.handler.to_dict(),
              'share': self.convert_value(self.share),
              'regex': self.convert_value(self.regex),
              'chksum': self.convert_value(self.chksum),
              }
    else:
      result= {
              'name': self.name
              }

    parent_dict = SimpleLoggingInformations.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


class Reference(Entity, Base):
  # Similar approach as for attributes
  report_id = Column('report_id', BigIntegerType, ForeignKey('reports.report_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)
  definition_id = Column('definition_id', BigIntegerType,
                         ForeignKey('referencedefinitions.referencedefinition_id', onupdate='cascade', ondelete='restrict'), nullable=False, index=True)
  definition = relationship(ReferenceDefinition,
                            primaryjoin='ReferenceDefinition.identifier==Reference.definition_id')
  value = Column('value', UnicodeTextType(), nullable=False)
  parent_id = Column('parent_id', BigIntegerType, ForeignKey('references.reference_id', onupdate='cascade', ondelete='SET NULL'), index=True, default=None)
  children = relationship('Reference',
                          primaryjoin='Reference.identifier==Reference.parent_id')

  _PARENTS = ['report']
  report = relationship('Report', uselist=False)

  def to_dict(self, cache_object):
    value = self.convert_value(self.value)

    handler_uuid = '{0}'.format(self.definition.reference_handler.uuid)
    if handler_uuid in ['0be5e1a0-8dec-11e3-baa8-0800200c9a66']:
      split = value.split('|')
      fh = self.definition.handler
      filepath = fh.get_base_path() + '/' + split[0]
      data = 'File is MIA'
      if isfile(filepath):
        with open(filepath, "rb") as data_file:
          data = b64encode(data_file.read())

      if len(split) == 2:
        value = {'filename': split[1], 'data': b64encode(data)}
      else:
        if isfile(filepath):
          value = {'filename': fileHashSHA1(filepath), 'data': b64encode(data)}
        else:
          value = {'filename': None, 'data': b64encode(data)}

    result = {'definition_id': self.convert_value(self.definition.uuid),
            'definition': self.definition.to_dict(cache_object),
            'value': value,
            }

    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

  def validate(self):
    # TODO create validation
    return True


class Report(Entity, Base):

  title = Column('title', UnicodeType(255), index=True)
  description = relationship(StructuredText, secondary=_REL_REPORT_STRUCTUREDTEXT, uselist=False, back_populates="report_description", lazy='joined')
  short_description = relationship(StructuredText, secondary=_REL_REPORT_STRUCTUREDTEXT_SHORT, uselist=False, back_populates="report_short_description", lazy='joined')
  parent_report_id = Column('parent_report_id', BigIntegerType, ForeignKey('reports.report_id', onupdate='cascade', ondelete='cascade'), index=True)
  report = relationship('Report', uselist=False, primaryjoin='Report.parent_report_id==Report.identifier')
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)
  event = relationship('Event', uselist=False)

  references = relationship('Reference')
  related_reports = relationship('Report', primaryjoin='Report.parent_report_id==Report.identifier', lazy='dynamic')

  _PARENTS = ['event', 'report']

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
              'title': self.convert_value(self.title),
              'description': self.attribute_to_dict(self.description, cache_object),
              'short_description': self.attribute_to_dict(self.short_description, cache_object),
              # TODO references
              'references': self.attributelist_to_dict(self.references, cache_object),
              # TODO related_reports
              'related_reports': self.attributelist_to_dict(self.related_reports, cache_object),
              }
    else:
      result = {
              'title': self.title,
              }

    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

  def validate(self):
    # TODO create validation
    return True
