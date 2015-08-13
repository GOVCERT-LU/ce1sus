# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 20, 2013
"""

from ce1sus.db.classes.internal.definitions import AttributeHandler
from ce1sus.db.common.broker import BrokerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributeHandlerBroker(BrokerBase):
  """
  Attribute handler broker
  """

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return AttributeHandler
