# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 28, 2015
"""
from ce1sus.db.classes.ccybox.common.time import CyboxTime
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.related import RelatedIdentity
from ce1sus.db.classes.cstix.common.statement import Statement
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.tools import ToolInformation
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.common.broker import BrokerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class StructuredTextBroker(BrokerBase):

  def get_broker_class(self):
    return StructuredText

class IdentityBroker(BrokerBase):

  def get_broker_class(self):
    return StructuredText

class RelatedIdentityBroker(BrokerBase):

  def get_broker_class(self):
    return RelatedIdentity

class InformationSourceBroker(BrokerBase):

  def get_broker_class(self):
    return InformationSource

class DateTimeWithPrecisionBroker(BrokerBase):

  def get_broker_class(self):
    return DateTimeWithPrecision

class CyboxTimeBroker(BrokerBase):

  def get_broker_class(self):
    return CyboxTime

class ToolInformationBroker(BrokerBase):

  def get_broker_class(self):
    return ToolInformation

class MarkingSpecificationBroker(BrokerBase):

  def get_broker_class(self):
    return MarkingSpecification

class StatementBroker(BrokerBase):

  def get_broker_class(self):
    return Statement

class STIXHeaderBroker(BrokerBase):

  def get_broker_class(self):
    return STIXHeader
