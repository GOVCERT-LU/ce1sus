# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 8, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Unicode, UnicodeText, BigInteger, Boolean

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations, SimpleLogingInformations
from ce1sus.db.common.session import Base
from ce1sus.handlers.base import HandlerBase, HandlerException
from ce1sus.helpers.common.objects import get_class


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

# Note: This is not yet part of STIX should be on 1.2

_REL_REPORT_RELATONS = Table('rel_reports_reports', Base.metadata,
                             Column('rrr_id', BigInteger, primary_key=True, nullable=False, index=True),
                             Column('report_id', Unicode(40), ForeignKey('references.reference_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                             Column('child_id', Unicode(40), ForeignKey('references.reference_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
                             )


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
  report_id = Column('event_id', Unicode(40), ForeignKey('reports.report_id', onupdate='cascade', ondelete='cascade'), index=True)
  definition_id = Column('definition_id', Unicode(40),
                         ForeignKey('referencedefinitions.referencedefinition_id', onupdate='cascade', ondelete='restrict'), nullable=False, index=True)
  definition = relationship(ReferenceDefinition,
                            primaryjoin='ReferenceDefinition.identifier==Reference.definition_id')
  share = Column('sharable', Boolean, default=False, nullable=False)


class Report(ExtendedLogingInformations, Base):

  title = Column('title', Unicode(255), index=True)
  description = Column('description', UnicodeText)
  short_description = Column('short_description', Unicode(255))

  event = relationship('Event', uselist=False, primaryjoin='Report.event_id==Event.identifier')
  event_id = Column('event_id', Unicode(40), ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), index=True)

  references = relationship('Reference')
  share = Column('sharable', Boolean, default=False, nullable=False)
