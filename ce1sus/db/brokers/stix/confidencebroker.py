# -*- coding: utf-8 -*-

"""
(Description)

Created on 4 Sep 2015
"""

from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.common.broker import BrokerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ConfidenceBroker(BrokerBase):

  def get_broker_class(self):
    return Confidence
