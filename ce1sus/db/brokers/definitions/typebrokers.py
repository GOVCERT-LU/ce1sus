# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 6, 2014
"""
from ce1sus.db.classes.types import AttributeType
from ce1sus.db.common.broker import BrokerBase, IntegrityException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributeTypeBroker(BrokerBase):

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return AttributeType

  def remove_by_id(self, identifier, commit=True):
    type_ = self.get_by_id(identifier)
    if type_.table_id:
      try:
        BrokerBase.remove_by_id(self, identifier, commit)
      except IntegrityException:
        raise IntegrityException('Item is still referenced cannot delete it')
    else:
      raise IntegrityException('Cannot remove the None element')

  def update(self, instance, commit=True, validate=True):
    type_ = self.get_by_id(instance.identifier)
    if type_.table_id:
      BrokerBase.update(self, instance, commit)
    else:
      raise IntegrityException('Cannot update the None element')
