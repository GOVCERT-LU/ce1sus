# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 9, 2015
"""

from ce1sus.db.classes.internal.report import Report, Reference
from ce1sus.db.common.broker import BrokerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ReportBroker(BrokerBase):

  def get_broker_class(self):
    return Report


class ReferenceBroker(BrokerBase):

  def get_broker_class(self):
    return Reference
