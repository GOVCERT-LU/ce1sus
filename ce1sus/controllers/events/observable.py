# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from uuid import uuid4

from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.event.attributebroker import AttributeBroker
from ce1sus.db.brokers.event.composedobservablebroker import ComposedObservableBroker
from ce1sus.db.brokers.event.objectbroker import ObjectBroker
from ce1sus.db.brokers.event.observablebroker import ObservableBroker
from ce1sus.db.brokers.event.relatedobjects import RelatedObjectBroker
from ce1sus.db.classes.observables import Observable
from ce1sus.db.common.broker import ValidationException, IntegrityException, BrokerException, NothingFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ObservableController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.observable_broker = self.broker_factory(ObservableBroker)
    self.composed_observable_broker = self.broker_factory(ComposedObservableBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.related_object_broker = self.broker_factory(RelatedObjectBroker)

  def insert_observable(self, observable, user, commit=True):
    """
    inserts an event

    If it is invalid the event is returned

    :param event:
    :type event: Event

    :returns: Event, Boolean
    """
    self.logger.debug('User {0} inserts a new observable'.format(user.username))
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(observable, user, user.group, True)
      self.observable_broker.insert(observable, False)
      # generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.observable_broker.do_commit(commit)
      return observable, True
    except ValidationException:
      return observable, False
    except IntegrityException as error:
      self.logger.debug(error)
      self.logger.info(u'User {0} tried to insert an observable with uuid "{1}" but the uuid already exists'.format(user.username, observable.uuid))
      raise ControllerException(u'An observable with uuid "{0}" already exists'.format(observable.uuid))
    except BrokerException as error:
      raise ControllerException(error)

  def insert_related_object(self, related_object, user, commit=True):
    try:
      self.object_broker.insert(related_object, False)
      self.object_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_handler_related_objects(self, related_objects, user, commit=True, owner=False):
    # Validate children
    validated = False
    if related_objects:
      for related_object in related_objects:
                # TODO Validate related objects
                # self.__validate_object(related_object)
        self.set_extended_logging(related_object.object, user, user.group, True)
        for attribute in related_object.object.attributes:
          self.set_extended_logging(attribute, user, user.group, True)
      validated = True

    if validated:
      # for related_object in related_objects:
        # self.set_extended_logging(related_object, user, user.group, True)
      self.insert_related_object(related_object, user, False)
    self.object_broker.do_commit(commit)

  def set_extended_logging_object(self, obj, user, insert=True):
    self.set_extended_logging(obj, user, user.group, insert)
    for attribute in obj.attributes:
      self.set_extended_logging(attribute, user, user.group, insert)
    if obj.related_objects:
      for rel_obj in obj.related_objects:
        self.set_extended_logging_object(rel_obj.object, user, insert)
        # TODO: check if relobject parent is set correctly
        rel_obj.parent = obj

  def set_extended_logging_observble(self, obs, user, insert=True):
    if obs.object:
      self.set_extended_logging_object(obs.object, user, insert)
    if obs.observable_composition:
      self.set_extended_logging_observble(obs, user, insert)
    self.set_extended_logging(obs, user, user.group, insert)

  def insert_composed_observable(self, observable, user, commit=True, owner=True):
    self.logger.debug('User {0} inserts a new composed observable'.format(user.username))
    try:
      user = self.user_broker.get_by_id(user.identifier)
      for obs in observable.observable_composition.observables:
        self.set_extended_logging_observble(obs, user, True)
      self.set_extended_logging(observable, user, user.group, True)

      self.observable_broker.insert(observable, False)
      # generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.observable_broker.do_commit(commit)
      return observable, True
    except ValidationException:
      return observable, False
    except IntegrityException as error:
      self.logger.debug(error)
      self.logger.info(u'User {0} tried to insert an observable with uuid "{1}" but the uuid already exists'.format(user.username, observable.uuid))
      raise ControllerException(u'An observable with uuid "{0}" already exists'.format(observable.uuid))
    except BrokerException as error:
      raise ControllerException(error)

  def get_observable_by_id(self, identifier):
    try:
      observable = self.observable_broker.get_by_id(identifier)
      return observable
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_observable_by_uuid(self, uuid):
    try:
      observable = self.observable_broker.get_by_uuid(uuid)
      return observable
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_composed_observable_by_id(self, identifier):
    try:
      composed_observable = self.composed_observable_broker.get_by_id(identifier)
      return composed_observable
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_composed_observable_by_uuid(self, uuid):
    try:
      composed_observable = self.composed_observable_broker.get_by_uuid(uuid)
      return composed_observable
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_attribute_by_id(self, identifier):
    try:
      obj = self.attribute_broker.get_by_id(identifier)
      return obj
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_attribute_by_uuid(self, uuid):
    try:
      obj = self.attribute_broker.get_by_uuid(uuid)
      return obj
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_object_by_id(self, identifier):
    try:
      obj = self.object_broker.get_by_id(identifier)
      return obj
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_parent_object_by_object(self, obj):
    try:
      obj = self.object_broker.get_parent_object_by_object(obj)
      return obj
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_object_by_uuid(self, uuid):
    try:
      obj = self.object_broker.get_by_uuid(uuid)
      return obj
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def update_observable(self, observable, user, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(observable, user, user.group, True)
      self.observable_broker.update(observable, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def update_observable_compositon(self, observable, user, commit=True):
    try:
      self.observable_broker.update(observable, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_observable(self, observable, user, commit=True):
    try:
      self.observable_broker.remove_by_id(observable.identifier)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_observable_composition(self, compoed_observable, user, commit=True):
    try:
      for observable in compoed_observable.observables:
        self.observable_broker.remove_by_id(observable.identifier)
      self.composed_observable_broker.remove_by_id(compoed_observable.identifier)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_event_for_observable(self, observable):
    if observable.parent:
      return observable.parent
    else:
      raise ControllerNothingFoundException('Parent for observable {0} cannot be found'.format(observable.identifier))

  def get_event_for_obj(self, obj):
    try:
      return self.get_event_for_observable(obj.observable)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_object(self, obj, user, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(obj, user, user.group, True)
      self.object_broker.insert(obj, False)
      self.object_broker.do_commit(commit)
    except IntegrityException as error:
      self.logger.debug(error)
      self.logger.info(u'User {0} tried to insert an object with uuid "{1}" but the uuid already exists'.format(user.username, obj.uuid))
      raise ControllerException(u'An object with uuid "{0}" already exists'.format(obj.uuid))
    except BrokerException as error:
      raise ControllerException(error)

  def update_object(self, obj, user, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(obj, user, user.group, False)
      self.object_broker.update(obj)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_object(self, obj, user, commit=True):
    try:
      self.object_broker.remove_by_id(obj.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def get_flat_observable_objects(self, observable):
    try:
      return self.object_broker.get_all_by_observable_id(observable.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def get_related_object_by_child(self, obj):
    try:
      return self.related_object_broker.get_related_object_by_child_object_id(obj.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def update_related_object(self, related_object, user, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(related_object, user, user.group, True)
      self.related_object_broker.update(related_object, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def __validate_object(self, obj):
    # validate
    if obj.validate:
      for related_object in obj.related_objects:
        if not related_object.validate:
          raise ControllerException('Related object is invalid')
    else:
      raise ControllerException('Object is invalid')

  def insert_handler_objects(self, related_objects, user, commit=True, owner=False):
    # Validate children
    validated = False
    if related_objects:
      for related_object in related_objects:
        self.__validate_object(related_object)
        self.set_extended_logging(related_object, user, user.group, True)
      validated = True

    if validated:
      for related_object in related_objects:
        self.set_extended_logging(related_object, user, user.group, True)
        self.insert_object(related_object, user, False)
    self.object_broker.do_commit(commit)

  def get_composition_by_observable(self, observable):
    try:
      composition = self.composed_observable_broker.get_by_observable_id(observable.identifier)
      return composition
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)
