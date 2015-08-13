# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 23, 2014
"""
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.definitions.referencesbroker import ReferencesBroker, ReferenceDefintionsBroker
from ce1sus.db.classes.internal.report import ReferenceHandler
from ce1sus.db.common.broker import BrokerException, ValidationException, NothingFoundException
from ce1sus.helpers.common.hash import hashSHA1
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def gen_reference_chksum(reference_definition):
  key = '{0}{1}{2}'.format(reference_definition.name,
                           reference_definition.regex,
                           reference_definition.referencehandler_id)
  return hashSHA1(key)


class ReferencesController(BaseController):
  """Controller handling all the requests for groups"""

  def __init__(self, config, session=None):
    super(BaseController, self).__init__(config, session)
    self.reference_broker = self.broker_factory(ReferencesBroker)
    self.reference_definition_broker = self.broker_factory(ReferenceDefintionsBroker)

  def get_reference_definitions_all(self):
    try:
      return self.reference_definition_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_reference_all(self):
    try:
      return self.reference_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_reference_by_id(self, reference_id):
    try:
      return self.reference_broker.get_by_id(reference_id)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_reference_by_uuid(self, uuid):
    try:
      return self.reference_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def update_reference(self, reference, commit=True):
    try:
      reference_definition = self.reference_broker.update(reference, commit)
      return reference_definition
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(reference_definition)
      raise ControllerException(u'Could not update reference due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_handlers(self):
    try:
      return self.reference_broker.get_all_handlers()
    except BrokerException as error:
      raise ControllerException(error)

  def get_reference_definitions_by_id(self, identifier):
    try:
      return self.reference_definition_broker.get_by_id(identifier)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_reference_definitions_by_uuid(self, uuid):
    try:
      return self.reference_definition_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def update_reference_definition(self, reference_definition):
    try:
      reference_definition = self.reference_definition_broker.update(reference_definition)
      return reference_definition
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(reference_definition)
      raise ControllerException(u'Could not update reference due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def insert_reference_definition(self, reference_definition, commit=True):
    try:
      reference_definition = self.reference_definition_broker.insert(reference_definition, False)
      self.reference_definition_broker.do_commit(commit)
      return reference_definition
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(reference_definition)
      raise ControllerException(u'Could not update reference due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def remove_reference_definition_by_id(self, identifier):
    try:
      return self.reference_definition_broker.remove_by_id(identifier)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_reference_definition_by_uuid(self, uuid):
    try:
      return self.reference_definition_broker.remove_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def register_handler(self, uuid, module, description):
    try:
      reference_handler = ReferenceHandler()
      reference_handler.uuid = uuid
      reference_handler.description = description
      reference_handler.module_classname = module
      self.reference_definition_broker.insert(reference_handler, True)
    except BrokerException as error:
      raise ControllerException(error)
