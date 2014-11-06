# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 6, 2014
"""
from ce1sus.db.classes.types import AttributeType, AttributeViewType
from ce1sus.db.common.broker import BrokerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributeTypeBroker(BrokerBase):
  """
  Attribute handler broker
  """

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return AttributeType


class AttributeViewTypeBroker(BrokerBase):
  """
  Attribute handler broker
  """

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return AttributeViewType
