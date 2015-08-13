# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 7, 2015
"""
from ce1sus.db.classes.log import ErrorMispAttribute
from ce1sus.db.common.broker import BrokerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ErrorMispBroker(BrokerBase):

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return ErrorMispAttribute
