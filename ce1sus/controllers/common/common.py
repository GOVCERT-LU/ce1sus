# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 28, 2015
"""
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.brokers.common.common import StructuredTextBroker, IdentityBroker, RelatedIdentityBroker, InformationSourceBroker, DateTimeWithPrecisionBroker, \
  CyboxTimeBroker, ToolInformationBroker, MarkingSpecificationBroker, StatementBroker
from ce1sus.db.brokers.common.path import PathBroker
from ce1sus.db.classes.cstix.extensions.marking.simple_markings import SimpleMarkingStructure
from ce1sus.db.common.broker import BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class CommonController(BaseController):

  def __init__(self, config, session=None):
    super(CommonController, self).__init__(config, session)
    self.structured_text_broker = self.broker_factory(StructuredTextBroker)
    self.identity_broker = self.broker_factory(IdentityBroker)
    self.related_identity_broker = self.broker_factory(RelatedIdentityBroker)
    self.information_source_broker = self.broker_factory(InformationSourceBroker)
    self.datetime_with_precision_broker = self.broker_factory(DateTimeWithPrecisionBroker)
    self.cybox_time_broker = self.broker_factory(CyboxTimeBroker)
    self.tool_information_broker = self.broker_factory(ToolInformationBroker)
    self.marking_specification_broker = self.broker_factory(MarkingSpecificationBroker)
    self.statement_broker = self.broker_factory(StatementBroker)
    self.path_broker = self.broker_factory(PathBroker)

  def remove_structured_text(self, structured_text, cache_object, commit=True):
    try:
      self.remove_set_base(structured_text, cache_object)
      self.remove_path(structured_text.path, cache_object, False)
      self.structured_text_broker.remove_by_id(structured_text.identifier, False)
      self.structured_text_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_identity(self, identity, cache_object, commit=True):
    try:
      self.remove_set_base(identity, cache_object)
      self.remove_path(identity.path, cache_object, False)
      for related_identity in identity.related_identities:
        self.remove_realated_identity(related_identity, cache_object, False)

      self.identity_broker.remove_by_id(identity.identifier, False)
      self.identity_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_realated_identity(self, related_identity, cache_object, commit=True):
    try:
      self.remove_set_base(related_identity, cache_object)
      self.remove_path(related_identity.path, cache_object, False)
      self.remove_path(related_identity, cache_object, False)
      if related_identity.child:
        self.remove_identity(related_identity.child, cache_object, False)
      self.related_identity_broker.remove_by_id(related_identity.identifier, False)
      self.related_identity_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_datetime_with_precision(self, datetime_with_precision, cache_object, commit=True):
    try:
      self.remove_set_base(datetime_with_precision, cache_object)
      self.remove_path(datetime_with_precision.path, cache_object, False)
      self.datetime_with_precision_broker.remove_by_id(datetime_with_precision.identifier, False)
      self.datetime_with_precision_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_cybox_time(self, time, cache_object, commit=True):
    try:
      self.remove_set_base(time, cache_object)
      self.remove_path(time.path, cache_object, False)
      if time.start_time:
        self.remove_datetime_with_precision(time.start_time, cache_object, False)
      if time.end_time:
        self.remove_datetime_with_precision(time.end_time, cache_object, False)
      if time.produced_time:
        self.remove_datetime_with_precision(time.produced_time, cache_object, False)
      if time.received_time:
        self.remove_datetime_with_precision(time.received_time, cache_object, False)

      self.cybox_time_broker.remove_by_id(time.identifier, False)
      self.cybox_time_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_tool_information(self, toolinformation, cache_object, commit=True):
    try:
      self.remove_set_base(toolinformation, cache_object)
      self.remove_path(toolinformation.path, cache_object, False)
      if toolinformation.description:
        self.remove_structured_text(toolinformation.description, cache_object, False)
      if toolinformation.short_description:
        self.remove_structured_text(toolinformation.short_description, cache_object, False)

      self.tool_information_broker.remove_by_id(toolinformation.identifier, False)
      self.tool_information_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_confidence(self, confidence, cache_object, commit=True):
    try:
      self.remove_set_base(confidence, cache_object)
      self.remove_path(confidence.path, cache_object, False)
      if confidence.description:
        self.remove_structured_text(confidence.description, cache_object, False)
      if confidence.source:
        self.remove_information_source(confidence.source, cache_object, False)

      self.confidence_broker.remove_by_id(confidence.identifier, False)
      self.confidence_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_information_source(self, information_source, cache_object, commit=True):
    try:
      self.remove_set_base(information_source, cache_object)
      self.remove_path(information_source.path, cache_object, False)
      if information_source.description:
        self.remove_structured_text(information_source.description, cache_object, False)
      if information_source.identity:
        self.remove_identity(information_source.identity, cache_object, False)
      for contributing_source in information_source.contributing_sources:
        self.remove_information_source(contributing_source, cache_object, False)

      if information_source.time:
        self.remove_cybox_time(information_source.time, cache_object, False)
      for tool in information_source.tools:
        self.remove_tool_information(tool, cache_object, False)

      if information_source.confidence:
        self.remove_confidence(information_source.confidence, cache_object, False)

      self.structured_text_broker.remove_by_id(information_source.identifier, False)
      self.structured_text_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_statement(self, statement, cache_object, commit=True):
    try:
      self.remove_set_base(statement, cache_object)
      self.remove_path(statement.path, cache_object, False)
      if statement.description:
        self.remove_structured_text(statement.description, cache_object, False)
      if statement.source:
        self.remove_information_source(statement.source, cache_object, False)
      if statement.confidence:
        self.remove_confidence(statement.confidence, cache_object, False)

      self.statement_broker.remove_by_id(statement.identifier, False)
      self.statement_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)
  
  def remove_path(self, path, cache_object, commit=True):
    try:
      self.path_broker.remove_by_id(path.identifier, False)
      self.path_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_marking_specification(self, marking_specification, cache_object, commit=True):
    try:
      self.remove_set_base(marking_specification, cache_object)
      self.remove_path(marking_specification.path, cache_object, False)
      self.remove_path(marking_specification, cache_object, False)

      for marking_structure in marking_specification.marking_structures:
        if isinstance(marking_structure, SimpleMarkingStructure):
          self.remove_statement(marking_structure.statement, cache_object, False)

      self.remove_information_source(marking_specification.information_source, cache_object, False)
      self.marking_specification_broker.remove_by_id(marking_specification.identifier, False)
      self.marking_specification_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_handling(self,handling, cache_object, commit=True):
    for item in handling:
      self.remove_marking_specification(item, cache_object, False)
      
