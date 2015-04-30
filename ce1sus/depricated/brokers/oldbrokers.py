# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""


from ce1sus.db.common.broker import BrokerBase
from ce1sus.depricated.classes.definitionclasses import OldAttributeDefinition, OldObjectDefinition, OldAttributeHandler
from ce1sus.depricated.classes.eventclasses import OldEvent
from ce1sus.depricated.classes.oldce1susconfig import OldCe1susConfig
from ce1sus.depricated.classes.permissionclasses import OldUser, OldGroup


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class OldEventBroker(BrokerBase):

  def get_broker_class(self):
    return OldEvent


class OldUserBroker(BrokerBase):

  def get_broker_class(self):
    return OldUser

  def get_all(self):
    users = BrokerBase.get_all(self)
    result = list()
    for user in users:
      if user.username != 'admin':
        result.append(user)
    return result


class OldGroupBroker(BrokerBase):

  def get_broker_class(self):
    return OldGroup


class OldAttributeDefinitionsBroker(BrokerBase):

  def get_broker_class(self):
    return OldAttributeDefinition


class OldObjectDefinitionsBroker(BrokerBase):

  def get_broker_class(self):
    return OldObjectDefinition


class OldConfigBroker(BrokerBase):

  def get_broker_class(self):
    return OldCe1susConfig


class OldHandlerBroker(BrokerBase):

  def get_broker_class(self):
    return OldAttributeHandler
