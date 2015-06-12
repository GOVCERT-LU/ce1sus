# -*- coding: utf-8 -*-

"""
(Description)

Created on Jun 12, 2015
"""

from ce1sus.helpers.common.objects import get_class

from ce1sus.controllers.base import BaseController
from ce1sus.controllers.events.event import EventController
from ce1sus.controllers.events.indicatorcontroller import IndicatorController
from ce1sus.mappers.stix.helpers.cyboxmapper import CyboxMapper
from cybox.common.object_properties import CustomProperties, Property
from cybox.core.object import Object, RelatedObject
from cybox.core.observable import Observable, ObservableComposition
from cybox.objects.process_object import Process
from cybox.objects.uri_object import URI
from stix.common import InformationSource, Identity
from stix.core import STIXPackage, STIXHeader
from stix.data_marking import Marking, MarkingSpecification
from stix.extensions.marking.tlp import TLPMarkingStructure
from stix.indicator import Indicator
from stix.indicator.valid_time import ValidTime
from cybox.objects.win_event_log_object import WinEventLog
from cybox.objects.user_account_object import UserAccount
from cybox.objects.win_service_object import WinService
from cybox.objects.win_registry_key_object import WinRegistryKey, RegistryValue, RegistryValues
from cybox.objects.network_connection_object import NetworkConnection
from cybox.objects.win_volume_object import WinVolume
from cybox.objects.win_kernel_hook_object import WinKernelHook
from cybox.objects.win_driver_object import WinDriver
from ce1sus.handlers.attributes.filehandler import FileHandler
from cybox.objects.domain_name_object import DomainName
from cybox.objects.artifact_object import Artifact, Base64Encoding
from cybox.objects.email_message_object import EmailMessage
from os.path import isfile


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susStixMapperException(Exception):
  pass


class Ce1susStixMapper(BaseController):

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.cybox_mapper = CyboxMapper(config, session)
    self.indicator_controller = IndicatorController(config, session)
    self.event_controller = EventController(config, session)
    self.fh = FileHandler()

  def init(self):
    self.seen_groups = list()
    self.seen_observables = list()

  def __map_stix_header(self, event):
    self.init()
    stix_header = STIXHeader(title=event.title)
    stix_header.description = event.description
    stix_header.short_description = event.title
    identifiy = self.create_stix_identity(event)
    time = self.cybox_mapper.get_time(produced_time=event.created_at, received_time=event.modified_on)
    info_source = InformationSource(identity=identifiy, time=time)
    stix_header.information_source = info_source

    # Add TLP
    marking = Marking()
    marking_spec = MarkingSpecification()
    marking.add_marking(marking_spec)

    tlp_marking_struct = TLPMarkingStructure()
    tlp_marking_struct.color = event.tlp.upper()
    tlp_marking_struct.marking_model_ref = 'http://govcert.lu/en/docs/POL_202_V2.2_rfc2350.pdf'
    marking_spec.marking_structures = list()
    marking_spec.marking_structures.append(tlp_marking_struct)
    stix_header.handling = marking


    return stix_header

  def create_stix_identity(self, obj):
    idenfitier = 'ce1sus:Group-{0}'.format(obj.creator_group.uuid)
    if idenfitier in self.seen_groups:
      identity = Identity()
      identity.idref = idenfitier
    else:
      identity = Identity()
      identity.id_ = idenfitier
      identity.name = obj.creator_group.name
      self.seen_groups.append(idenfitier)
    return identity

  def add_custom_property(self, instance, attribute):
    if not instance.custom_properties:
      cust_props = CustomProperties()
      instance.custom_properties = cust_props

    custom_prop = Property()
    custom_prop.name = attribute.definition.name
    custom_prop.description = attribute.definition.description
    custom_prop._value = attribute.value
    if hasattr(custom_prop._value, 'condition'):
      custom_prop._value.condition = self.get_condition(attribute)
    if hasattr(custom_prop, 'condition'):
      custom_prop.condition = self.get_condition(attribute)
    instance.custom_properties.append(custom_prop)

  def map_attribtue(self, instance, attribute):
    definition_name = attribute.definition.name
    if hasattr(instance, definition_name.lower()):
      setattr(instance, definition_name.lower(), attribute.value)
      value = getattr(instance, definition_name.lower())
      value.condition = self.get_condition(attribute)
    else:
      if 'hash' in definition_name:
        instance.add_hash(attribute.value)

      elif definition_name == 'url':
        instance.type_ = URI.TYPE_URL
        instance.value = attribute.value
        instance.value.condition = self.get_condition(attribute)
      elif 'Full_Path' and isinstance(instance, Process):
        # TODO: check why this is set?!?
        pass
      elif definition_name == 'WindowsRegistryKey_Key':
        instance.key = attribute.value
        instance.key.condition = self.get_condition(attribute)
      elif definition_name == 'WindowsRegistryKey_Hive':
        instance.hive = attribute.value
        instance.hive.condition = self.get_condition(attribute)
      elif 'WindowsRegistryKey_RegistryValue' in definition_name:
        value = RegistryValue()
        if definition_name == 'WindowsRegistryKey_RegistryValue_Data':
          value.data = attribute.value
          value.data.condition = self.get_condition(attribute)
        elif definition_name == 'WindowsRegistryKey_RegistryValue_Data':
          value.name = attribute.value
          value.name.condition = self.get_condition(attribute)
        if not instance.values:
          instance.values = RegistryValues()

        instance.values.append(value)
        instance.data = attribute.value
      elif definition_name == 'ipv4_addr':
        instance.category = definition_name.replace('_', '-')
        instance.address_value = attribute.value
        instance.address_value.condition = self.get_condition(attribute)
      elif definition_name == 'DomainName_Value':
        instance.value = attribute.value
      elif definition_name == 'Raw_Artifact':
        path = '{0}/{1}'.format(self.fh.get_base_path(), attribute.value)
        if isfile(path):
          with open(path, 'r') as f:
            bin_string = f.read()
          instance.data = bin_string
          # TODO find the corect type
          instance.type_ = Artifact.TYPE_GENERIC
          instance.packaging.append(Base64Encoding())
        else:
          instance.data = 'MIA'
        instance.type_ = Artifact.TYPE_GENERIC
        instance.packaging.append(Base64Encoding())
      elif definition_name == 'content_type':
        instance.type_ = attribute.value
      elif definition_name == 'URIType':
        instance.type_ = attribute.value
      elif not attribute.definition.cybox_std:
        self.add_custom_property(instance, attribute)
      elif isinstance(instance, NetworkConnection) and definition_name in ['is_type', 'Port']:
        # TODO: check why this is set?!?
        pass
      else:
        raise Ce1susStixMapperException('Cannot map {1} on object type {0}'.format(instance.__class__.__name__, definition_name))

  def get_condition(self, attribute):
    if attribute.condition:
      return attribute.condition.value
    else:
      # default condition is equals
      return 'Equals'

  def create_object(self, ce1sus_object, event_permissions, user):
    definition_name = ce1sus_object.definition.name
    obj = Object()
    identifier = 'ce1sus:Object-{0}'.format(ce1sus_object.uuid)
    obj.id_ = identifier
    # try to find automatic the object container
    try:
      clazz = get_class('cybox.objects.{0}_object'.format(definition_name.lower()), definition_name)
      instance = clazz()
      if definition_name == 'Disk':
        # TODO: check why this must be set stix bug?
        setattr(instance, 'type_', None)
    except ImportError:
      if definition_name == 'WinEventLog':
        instance = WinEventLog()
        # TODO: check why this must be set stix bug?
        setattr(instance, 'type_', None)
      elif definition_name == 'UserAccount':
        instance = UserAccount()
      elif definition_name == 'WinService':
        instance = WinService()
      elif definition_name == 'WindowsRegistryKey':
        instance = WinRegistryKey()
      elif definition_name == 'NetworkConnection':
        instance = NetworkConnection()
      elif definition_name == 'WinVolume':
        instance = WinVolume()
        # TODO: check why this must be set stix bug?
        setattr(instance, 'drive_type', None)
      elif definition_name == 'WinKernelHook':
        instance = WinKernelHook()
      elif definition_name == 'WinDriver':
        instance = WinDriver()
      elif definition_name == 'DomainName':
        instance = DomainName()
      # TODO: try to map it manually
      elif definition_name == 'email':
        instance = EmailMessage()
      else:
        raise Ce1susStixMapperException('Required to map manually {0}'.format(definition_name))

    obj.properties = instance

    attributes = ce1sus_object.get_attributes_for_permissions(event_permissions, user)
    for attribute in attributes:
      self.map_attribtue(instance, attribute)

    rel_objects = ce1sus_object.get_related_objects_for_permissions(event_permissions, user)
    for rel_object in rel_objects:
      ob = self.create_object(rel_object.object, event_permissions, user)
      if ob:
        cybox_rel_object = RelatedObject(ob.properties, rel_object.relation)
        cybox_rel_object.id_ = ob.id_
        obj.related_objects.append(cybox_rel_object)
    return obj

  def create_composed_observable(self, ce1sus_composition, event_permissions, user):
    composition = ObservableComposition()
    composition.operator = ce1sus_composition.operator
    ce1sus_obs = ce1sus_composition.get_observables_for_permissions(event_permissions, user)
    for ce1sus_ob in ce1sus_obs:
      obs = self.create_observable(ce1sus_ob, event_permissions, user)
      composition.observables.append(obs)
    return composition

  def create_observable(self, ce1sus_obs, event_permissions, user):
    identifier = 'ce1sus:Observable-{0}'.format(ce1sus_obs.uuid)
    cybox_observable = Observable()
    if identifier in self.seen_observables:
      # if I've seen the uuid then make a reference insead
      cybox_observable.idref = identifier
    else:
      self.seen_observables.append(identifier)
      cybox_observable.id_ = identifier
      cybox_observable.title = ce1sus_obs.title
      cybox_observable.description = ce1sus_obs.description
      if ce1sus_obs.object:
        cybox_obj = self.create_object(ce1sus_obs.object, event_permissions, user)
        cybox_observable.object_ = cybox_obj
      elif ce1sus_obs.observable_composition:
        cybox_obj_composition = self.create_composed_observable(ce1sus_obs.observable_composition, event_permissions, user)
        cybox_observable.observable_composition = cybox_obj_composition

    return cybox_observable

  def create_indicator(self, ce1sus_indicator, event_permissions, user):
    indicator = Indicator()
    indicator.id_ = 'ce1sus:Indicator-{0}'.format(ce1sus_indicator.uuid)
    indicator.title = ce1sus_indicator.title
    indicator.description = ce1sus_indicator.description
    indicator.short_description = ce1sus_indicator.short_description
    if ce1sus_indicator.confidence:
      indicator.confidence = ce1sus_indicator.confidence.title()
    else:
      indicator.confidence = 'Low'
    # TODO: handling
    # TODO: markings
    for type_ in ce1sus_indicator.types:
      indicator.add_indicator_type(type_.name)


    if ce1sus_indicator.operator:
      indicator.observable_composition_operator = ce1sus_indicator.operator
    # Todo Add confidence
    # indicator_attachment.confidence = "Low"
    creator = self.create_stix_identity(ce1sus_indicator)
    time = self.cybox_mapper.get_time(produced_time=ce1sus_indicator.created_at)
    info_source = InformationSource(identity=creator, time=time)
    indicator.producer = info_source
    observables = ce1sus_indicator.get_observables_for_permissions(event_permissions, user)
    for obs in observables:
      cybox_obs = self.create_observable(obs, event_permissions, user)
      indicator.add_observable(cybox_obs)
    valid_time = ValidTime(start_time=ce1sus_indicator.created_at, end_time=ce1sus_indicator.created_at)
    indicator.add_valid_time_position(valid_time)
    return indicator

  def create_stix(self, event, user):
    stix_package = STIXPackage()

    stix_package.id_ = 'ce1sus:Event-{0}'.format(event.uuid)
    stix_header = self.__map_stix_header(event)
    stix_package.stix_header = stix_header
    event_permissions = self.event_controller.get_event_user_permissions(event, user)
    # observables
    if event.observables:
      for observable in event.get_observables_for_permissions(event_permissions, user):
        cybox_obs = self.create_observable(observable, event_permissions, user)
        stix_package.add_observable(cybox_obs)
    # indicators
    if event.indicators:
      indicators = event.get_indicators_for_permissions(event_permissions, user)
    else:
      # generate indicators
      indicators = self.indicator_controller.get_generic_indicators(event, user)

    for indicator in indicators:
      stix_indicator = self.create_indicator(indicator, event_permissions, user)
      stix_package.add_indicator(stix_indicator)
    return stix_package
