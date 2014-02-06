# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 20, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'
from dagr.db.broker import BrokerBase
from ce1sus.brokers.definition.definitionclasses import AttributeHandler


class AttributeHandlerBroker(BrokerBase):

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return AttributeHandler

  def get_all_cb_values(self):
    """
    Returns all the values ready for comboboxes
    """
    result = dict()
    definitions = self.get_all()
    for definition in definitions:
      result[definition.classname] = definition.identifier

    return result
