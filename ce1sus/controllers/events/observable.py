# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""

from datetime import datetime
from uuid import uuid4

from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.event.attributebroker import AttributeBroker
from ce1sus.db.brokers.event.composedobservablebroker import ComposedObservableBroker
from ce1sus.db.brokers.event.objectbroker import ObjectBroker
from ce1sus.db.brokers.event.observablebroker import ObservableBroker
from ce1sus.db.brokers.event.relatedobjects import RelatedObjectBroker
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition
from ce1sus.db.common.broker import ValidationException, IntegrityException, BrokerException, NothingFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ObservableController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    super(ObservableController, self).__init__(config, session)
    self.observable_broker = self.broker_factory(ObservableBroker)
    self.composed_observable_broker = self.broker_factory(ComposedObservableBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.related_object_broker = self.broker_factory(RelatedObjectBroker)

  def insert_observable(self, observable, cache_object, commit=True):
    """
    inserts an event

    If it is invalid the event is returned

    :param event:
    :type event: Event

    :returns: Event, Boolean
    """
    try:
      self.insert_set_base(observable, cache_object)
      self.observable_broker.insert(observable, False)
      # TODO: generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.observable_broker.do_commit(commit)
      return observable, True
    except ValidationException:
      return observable, False
    except BrokerException as error:
      raise ControllerException(error)

  def insert_related_object(self, related_object, commit=True):
    try:
      self.object_broker.insert(related_object, False)
      self.object_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_handler_related_objects(self, related_objects, commit=True):
    # Validate children
    validated = False
    if validated:
      for related_object in related_objects:
        self.insert_related_object(related_object, False)
    self.object_broker.do_commit(commit)

  def insert_composed_observable(self, observable, commit=True):
    try:

      self.observable_broker.insert(observable, False)
      # TODO: generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.observable_broker.do_commit(commit)
      return observable, True
    except ValidationException:
      return observable, False
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

  def update_observable(self, observable, commit=True):
    try:
      self.observable_broker.update(observable, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def update_observable_compositon(self, observable, commit=True):
    try:
      self.observable_broker.update(observable, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_observable(self, observable, commit=True):
    try:
      self.observable_broker.remove_by_id(observable.identifier)
      self.observable_broker.do_commit(commit)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_observable_composition(self, compoed_observable, commit=True):
    try:
      for observable in compoed_observable.observables:
        self.observable_broker.remove_by_id(observable.identifier)
      self.composed_observable_broker.remove_by_id(compoed_observable.identifier)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_event_for_observable(self, observable):
    if len(observable.event) > 0:
      return observable.event[0]
    else:
      raise ControllerNothingFoundException('Parent for observable {0} cannot be found'.format(observable.identifier))

  def get_event_for_obj(self, obj):
    try:
      return self.get_event_for_observable(obj.observable)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_object(self, obj, commit=True):
    try:
      self.object_broker.insert(obj, False)
      self.object_broker.do_commit(commit)
    except IntegrityException as error:
      self.logger.debug(error)
    except BrokerException as error:
      raise ControllerException(error)

  def __set_logging(self, instance1, instance2, user):
    instance1.tlp_level_id = instance2.tlp_level_id
    instance1.dbcode = instance2.dbcode

    instance1.created_at = datetime.utcnow()
    instance1.modified_on = datetime.utcnow()

    instance1.creator = user
    instance1.modifier = user

    instance1.creator_group_id = user.group.identifier

  def insert_composed_observable_object(self, obj, observable, cache_object, commit=True):

    # remove relation from event and observable
    event = observable.event[0]
    event.observables.remove(observable)

    # create containers
    obs = Observable()
    obs.uuid = uuid4()
    obs.event = [event]
    self.__set_logging(obs, observable, cache_object.user)

    comp_obs = ObservableComposition()
    self.__set_logging(comp_obs, observable, cache_object.user)
    comp_obs.observable = obs

    obs.observable_composition = comp_obs

    child_obs = Observable()
    child_obs.uuid = uuid4()
    child_obs.event = [event]
    self.__set_logging(child_obs, observable, cache_object.user)
    child_obs.object = obj

    comp_obs.observables.append(child_obs)
    comp_obs.observables.append(observable)

    self.insert_observable(obs, cache_object, commit)

    return obs

  def update_object(self, obj, commit=True):
    try:
      self.object_broker.update(obj, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_object(self, obj, commit=True):
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

  def update_related_object(self, related_object, commit=True):
    try:
      self.related_object_broker.update(related_object, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_handler_objects(self, related_objects, commit=True, owner=False):
    for related_object in related_objects:
      self.insert_object(related_object, False)
    self.object_broker.do_commit(commit)

  def get_composition_by_observable(self, observable):
    try:
      composition = self.composed_observable_broker.get_by_observable_id(observable.identifier)
      return composition
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)
