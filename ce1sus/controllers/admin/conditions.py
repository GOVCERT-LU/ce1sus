# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 24, 2014
"""
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.definitions.conditionbroker import ConditionBroker
from ce1sus.db.common.broker import BrokerException, NothingFoundException, ValidationException, IntegrityException
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ConditionController(BaseController):
  """Controller handling all the requests for objects"""

  def __init__(self, config, session=None):
    super(BaseController, self).__init__(config, session)
    self.condition_broker = self.broker_factory(ConditionBroker)

  def get_condition_by_id(self, identifier):
    try:
      return self.condition_broker.get_by_id(identifier)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_condition_by_uuid(self, uuid):
    try:
      return self.condition_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_conditions(self):
    try:
      return self.condition_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def insert_condition(self, condition, commit=True):
    try:
      self.condition_broker.insert(condition, False)
      self.condition_broker.do_commit(commit)
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(condition)
      raise ControllerException(u'Could not add condition due to: {0}'.format(message))
    except (BrokerException) as error:
      raise ControllerException(error)

  def update_condition(self, condition, commit=True):
    try:
      self.condition_broker.update(condition, commit)
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(condition)
      raise ControllerException(u'Could not add condition due to: {0}'.format(message))
    except (BrokerException) as error:
      raise ControllerException(error)

  def remove_condition_by_id(self, identifier):
    try:
      self.condition_broker.remove_by_id(identifier)
    except IntegrityException as error:
      raise ControllerException('Cannot delete condition. The condition is referenced by elements.')
    except BrokerException as error:
      raise ControllerException(error)

  def remove_condition_by_uuid(self, uuid):
    try:
      self.condition_broker.remove_by_uuid(uuid)
    except IntegrityException as error:
      raise ControllerException('Cannot delete condition. The condition is referenced by elements.')
    except BrokerException as error:
      raise ControllerException(error)
