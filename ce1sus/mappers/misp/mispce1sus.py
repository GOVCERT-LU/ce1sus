# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 20, 2015
"""
from ce1sus.helpers.common.validator.valuevalidator import ValueValidator
from datetime import datetime
from dateutil import parser
import json
from lxml import etree
from uuid import uuid4

from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.controllers.common.assembler.assembler import Assembler
from ce1sus.db.brokers.definitions.referencesbroker import ReferenceDefintionsBroker
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.information_source import InformationSource, InformationSourceRole
from ce1sus.db.classes.cstix.common.names import Name
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader, PackageIntent
from ce1sus.db.classes.cstix.exploit_target.exploittarget import ExploitTarget
from ce1sus.db.classes.cstix.exploit_target.vulnerability import Vulnerability
from ce1sus.db.classes.cstix.extensions.test_mechanism.snort_test_mechanism import SnortTestMechanism, SnortRule
from ce1sus.db.classes.cstix.extensions.test_mechanism.yara_test_mechanism import YaraTestMechanism
from ce1sus.db.classes.cstix.ttp.behavior import Behavior
from ce1sus.db.classes.cstix.ttp.malware_instance import MalwareInstance
from ce1sus.db.classes.cstix.ttp.ttp import TTP
from ce1sus.db.classes.internal.attributes.attribute import Attribute, Condition
from ce1sus.db.classes.internal.common import Properties
from ce1sus.db.classes.internal.definitions import AttributeDefinition, ObjectDefinition
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.report import Report, Reference
from ce1sus.db.classes.internal.usrmgt.group import Group
from ce1sus.db.common.broker import BrokerException
from ce1sus.mappers.misp.common import get_container_object_attribute, get_tlp, ANALYSIS_MAP, RISK_MAP
from ce1sus.controllers.events.indicatorcontroller import IndicatorController


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class MispConverter(BaseController):
  

  NAMESPACE = 'MISP'

  def __init__(self, config, session=None):
    super(MispConverter, self).__init__(config, session)
    self.assembler = Assembler(config, session=session)
    self.refernce_defintion_broker = self.broker_factory(ReferenceDefintionsBroker)
    self.indicator_controller = IndicatorController(config, session)

  @staticmethod
  def get_xml_parser(encoding=None):
    """Returns an ``etree.ETCompatXMLParser`` instance."""
    parser = etree.ETCompatXMLParser(
                               huge_tree=True,
                               remove_comments=True,
                               strip_cdata=False,
                               remove_blank_text=True,
                               resolve_entities=False,
                               encoding=encoding
                               )
    return parser
  
  @staticmethod
  def get_xml_root(string, encoding=None):
    parser = MispConverter.get_xml_parser(encoding=encoding)
    root = etree.fromstring(string, parser=parser)
    return root

  @staticmethod
  def __get_value(xml_element, tagname):
    element = xml_element.find(tagname)
    if element is None:
      return None
    else:
      return element.text

  def set_base(self, xml_element, instance, cache_object):
    
    distribution = MispConverter.__get_value(xml_element, 'distribution')
    timestamp = MispConverter.__get_value(xml_element, 'timestamp')
    uuid = MispConverter.__get_value(xml_element, 'uuid')
    date = MispConverter.__get_value(xml_element, 'date')

    timestamp = datetime.utcfromtimestamp(int(timestamp))
    tlp = get_tlp(distribution)

    if not date:
      date = timestamp

    instance.tlp = tlp
    instance.uuid = uuid
    instance.creator = cache_object.user
    instance.creator_group = Group()
    instance.creator_group.name = cache_object.org
    instance.creator_group.tlp_lvl = 3

    instance.created_at = date
    instance.modified_on = timestamp
    instance.modifier = cache_object.user
    instance.properties = Properties('0', instance)
    instance.properties.is_shareable = True
    instance.properties.is_validated = True

    if hasattr(instance, 'version_db'):
      instance.version_db = '0.0.0'

    if hasattr(instance, 'namespace'):
      instance.namespace = MispConverter.NAMESPACE


  def __parse_attributes(self, xml_event, event, cache_object):
    self.logger.debug('Mapping MISP Attributes')
    
    xml_attributes = xml_event.iter(tag='Attribute')
    for xml_attribute in xml_attributes:
      self.__parse_misp_attribute(xml_attribute, event, cache_object)

  def __assemble_text(self, xml_element, json, value, cache_object):
    st = StructuredText()
    self.set_base(xml_element, st, cache_object)
    st.value = value
    self.set_base(st, json, cache_object)
    return st

  def __parse_misp_attribute(self, xml_attribute, event, cache_object):
    self.logger.debug('Mapping Attribute properties')

    category = MispConverter.__get_value(xml_attribute, 'category')
    type_ = MispConverter.__get_value(xml_attribute, 'type')

    container, obj_def_name, attr_def_name = get_container_object_attribute(category, type_)
    if container and obj_def_name and attr_def_name:
      if container == 'Observable':
        obs = self.__assemble_observable(obj_def_name, attr_def_name, xml_attribute, event, cache_object)
        event.observables.append(obs)
      elif container == 'Report':
        report = self.__assemble_report(attr_def_name, xml_attribute, cache_object)
        event.reports.append(report)
      else:
        # This case should not happen as the converter is rigid
        raise ControllerException('Container {0} cannot be found'.format(container))
      
    elif container and obj_def_name:
      #special cases like ip addresses
      if container == 'Observable':
        if 'ip' in type_:
          obs = self.__assemble_ip_address(obj_def_name, type_, xml_attribute, event, cache_object)
        else:
          raise ControllerException('No special case defined for container {0} and object {1}'.format(container, obj_def_name))
      elif container == 'TTP':
        ttp = self.__assemble_ttp(type_, xml_attribute, event, cache_object)
        event.ttps.append(ttp)
      elif container == 'Indicator':
        indicator = self.__assemble_test_mechanism_indicator(obj_def_name, xml_attribute, event, cache_object)
        event.indicators.append(indicator)
      else:
        raise ControllerException('Container {0} cannot be found for special cases'.format(container))

    else:
      # log this as error
      self.__assemble_errornous_observable(xml_attribute, event, cache_object)

  def __assemble_test_mechanism_indicator(self, obj_def_name, xml_attribute, event, cache_object):
    value = MispConverter.__get_value(xml_attribute, 'value')
    
    if obj_def_name == 'SnortTestMechanism':
      snort = SnortTestMechanism()
      self.set_base(xml_attribute, snort, cache_object)

      snort.producer = self.get_information_source(xml_attribute, cache_object)
      
      
      snort_rule = SnortRule()
      self.set_base(xml_attribute, snort_rule, cache_object)
      snort_rule.uuid = uuid4()

      snort_rule.rule = value 
      snort.rules.append(snort_rule)
      
    elif obj_def_name == 'YaraTestMechanism':
      yara = YaraTestMechanism()
      self.set_base(xml_attribute, yara, cache_object)

      yara.producer = self.get_information_source(xml_attribute, cache_object)

      yara.rule = value

    else:
      raise ControllerException('Undefined Test Mechanism')

  def __assemble_ttp(self, type_, xml_attribute, event, cache_object):
    timestamp = MispConverter.__get_value(xml_attribute, 'timestamp')
    timestamp = datetime.utcfromtimestamp(int(timestamp))

    ttp = TTP()
    self.set_base(xml_attribute, ttp, cache_object)
    ttp.timestamp = timestamp
    if type_ == 'vulnerability':
      vulnerability = Vulnerability()
      self.set_base(xml_attribute, vulnerability, cache_object)
      vulnerability.uuid = uuid4()

      # add the vulnerability to the root

      exploit_target = ExploitTarget()
      self.set_base(xml_attribute, exploit_target, cache_object)
      exploit_target.uuid = uuid4()
      exploit_target.timestamp = timestamp
      exploit_target.vulnerabilities.append(vulnerability)

      event.exploit_targets.append(exploit_target)

      ttp_exploit_target = ExploitTarget()
      self.set_base(xml_attribute, ttp_exploit_target, cache_object)
      ttp_exploit_target.uuid = uuid4()
      ttp_exploit_target.idref = exploit_target.id_

      ttp.exploit_targets.append(ttp_exploit_target)

    else:
      value = MispConverter.__get_value(xml_attribute, 'value')

      malware = MalwareInstance()
      self.set_base(xml_attribute, malware, cache_object)
      malware.uuid = uuid4()
      name = Name()
      self.set_base(xml_attribute, name, cache_object)
      name.name = value

      malware.names.append(name)

      ttp.behavior = Behavior()
      self.set_base(xml_attribute, ttp.behavior, cache_object)
      ttp.behavior.uuid = uuid4()
      ttp.behavior.malware_instances.append(malware)
    event.ttps.append(ttp)

  def __assemble_ip_address(self, obj_def_name, type_, xml_attribute, parent, cache_object):
    value = MispConverter.__get_value(xml_attribute, 'value')

    # determine if is network
    # determine if it is ip4 or ip6
    if ValueValidator.validateRegex(value, r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ''):
      attr_def_name = 'ipv4_addr'
    elif ValueValidator.validateRegex(value, r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$', ''):
      attr_def_name = 'ipv4_net'
    elif ValueValidator.validateRegex(value, r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'):
      attr_def_name = 'ipv6_addr'
    else:
      attr_def_name = 'ipv6_net'

    obs = self.__assemble_observable(obj_def_name, attr_def_name, xml_attribute, parent, cache_object)


    is_type = None
    if 'dst' in type_:
      is_type = 'Source'
    elif 'src' in type_:
      is_type = 'Destination'

    if is_type:
      attribute = self.__assemble_attribute(obs.object, xml_attribute, 'is_type', cache_object)
      attribute.uuid = uuid4()
      attribute.value = is_type
      obs.object.attributes.append(attribute)

    return obs

  def get_reference_definition(self, def_name, cache_object):
    self.logger.debug('Getting reference definition for {0}'.format(def_name))
    od = cache_object.seen_ref_defs.get(def_name, None)
    if od:
      return od
    else:
      try:
        definition = self.refernce_defintion_broker.get_definition_by_name(def_name)
        cache_object.seen_ref_defs[def_name] = definition
        return definition
      except BrokerException as error:
        self.logger.error(error)
        raise ControllerException('Cannot find the correct object definition for {0}'.format(def_name))

  
  def __assemble_report(self, ref_def_name, xml_attribute, cache_object):
    comment = MispConverter.__get_value(xml_attribute, 'comment')
    category = MispConverter.__get_value(xml_attribute, 'category')
    value = MispConverter.__get_value(xml_attribute, 'value')
    data = MispConverter.__get_value(xml_attribute, 'data')
    type_ = MispConverter.__get_value(xml_attribute, 'type')

    report = Report()
    self.set_base(xml_attribute, report, cache_object)
    report.uuid = uuid4()

    if comment:
      report.description = comment
      
    reference = self.__assemble_reference(xml_attribute, ref_def_name, cache_object)
    if data:
      # set for files as this is a data element
      reference.value = {'name': value, 'data': data}
    else:
      if type_ == 'link':
        reference2 = self.__assemble_reference(xml_attribute, 'comment', cache_object)
        reference2.value = category
        report.references.append(reference2)
        reference.value = value
      else:
        reference.value = u'{0}{1}'.format(category, value)
    
    report.references.append(reference)

    return report
  
  def __assemble_reference(self, xml_attribute, ref_def_name, cache_object):
    reference = Reference()
    self.set_base(xml_attribute, reference, cache_object)
    reference.uuid = uuid4()
    reference.definition = self.get_reference_definition(ref_def_name, cache_object)
    return reference

  def get_object_definition(self, def_name, cache_object):
    self.logger.debug('Getting object definition for {0}'.format(def_name))
    od = cache_object.seen_obj_defs.get(def_name, None)
    if od:
      return od
    else:
      try:
        definition = self.obj_def_broker.get_defintion_by_name(def_name)
        cache_object.seen_obj_defs[def_name] = definition
        return definition
      except BrokerException as error:
        self.logger.error(error)
        raise ControllerException('Cannot find the correct object definition for {0}'.format(def_name))

  def get_condition(self, condition_name, cache_object):
    self.logger.debug('Getting condition definition for {0}'.format(condition_name))
    definition = cache_object.seen_conditions.get(condition_name, None)
    if definition:
      return definition
    else:
      try:
        definition = self.condition_broker.get_
        cache_object.seen_conditions[condition_name] = definition
        return definition
      except BrokerException as error:
        self.logger.error(error)
        raise ControllerException('Cannot find the correct condition definition for {0}'.format(condition_name))

  def get_attribute_definition(self, def_name, cache_object):
    self.logger.debug('Getting attribute definition for {0}'.format(def_name))
    od = cache_object.seen_attr_defs.get(def_name, None)
    if od:
      return od
    else:
      try:
        definition = self.attr_def_broker.get_defintion_by_name(def_name)
        cache_object.seen_attr_defs[def_name] = definition
        return definition
      except BrokerException as error:
        self.logger.error(error)
        raise ControllerException('Cannot find the correct attribute definition for {0}'.format(def_name))

  def __assemble_structured_text(self, xml_element, value, cache_object):
    st = StructuredText()
    self.set_base(xml_element, st, cache_object)
    st.value = value
    return None
  
  def __assemble_errornous_observable(self, xml_attribute, parent, cache_object):
    self.logger.debug('Assembling Observable for a MISP Event')

    comment = MispConverter.__get_value(xml_attribute, 'comment')
    type_ = MispConverter.__get_value(xml_attribute, 'type')
    category = MispConverter.__get_value(xml_attribute, 'category')
    
    observable = Observable()
    self.set_base(xml_attribute, observable, cache_object)
    observable.uuid = uuid4()
    observable.parent = parent
    if comment:
      observable.description = self.__assemble_structured_text(xml_attribute, comment, cache_object)


    obj = Object()
    self.set_base(xml_attribute, obj, cache_object)
    obj.uuid = uuid4()
    # definition
    obj.definition = ObjectDefinition()
    obj.definition.uuid = uuid4()
    observable.object = obj
    obj.observable = observable


      # get_attribute definition
    attribute = Attribute()
    self.set_base(xml_attribute, attribute, cache_object)
    attribute_definition = self.get_attribute_definition('comment', cache_object)
    attribute.definition = attribute_definition
    attribute.object = obj

    ioc = MispConverter.__get_value(xml_attribute, 'to_ids')
    value = MispConverter.__get_value(xml_attribute, 'value')

    attribute.value = u'[{0}{1}]: {2}'.format(category, type_, value)
    attribute.definition = AttributeDefinition()
    attribute.definition.uuid = uuid4()
    attribute.is_ioc = ioc == '1'
    obj.attributes.append(attribute)

    return observable

  def __assemble_observable(self, obj_def_name, attr_def_name, xml_attribute, parent, cache_object):
    self.logger.debug('Assembling Observable for a MISP Event')

    comment = MispConverter.__get_value(xml_attribute, 'comment')
    type_ = MispConverter.__get_value(xml_attribute, 'type')
    
    observable = Observable()
    self.set_base(xml_attribute, observable, cache_object)
    observable.uuid = uuid4()
    observable.parent = parent
    if comment:
      observable.description = self.__assemble_structured_text(xml_attribute, comment, cache_object)


    obj = Object()
    self.set_base(xml_attribute, obj, cache_object)
    obj.uuid = uuid4()
    # definition
    obj.definition = self.get_object_definition(obj_def_name, cache_object)
    observable.object = obj
    obj.observable = observable

    #check if pipe in type_
    if '|' in type_:
      # create 2 attributes
      type1 = type_.split('|')[0]
      
      if type1 == 'filename':
        additional_attr_def_name = 'File_Name'
      elif type1 == 'regkey':
        additional_attr_def_name = 'WindowsRegistryKey_Key'
      else:
        raise ControllerException('Fist element {0} in piped definition is unkown'.format(type1))
      
      attribute1 = self.__assemble_attribute(obj, xml_attribute, additional_attr_def_name, cache_object)
      obj.attributes.append(attribute1)
      attribute2 = self.__assemble_attribute(obj, xml_attribute, attr_def_name, cache_object)
      obj.attributes.append(attribute2)

    else:
      # get_attribute definition
      attribute = self.__assemble_attribute(obj, xml_attribute, attr_def_name, cache_object)
      obj.attributes.append(attribute)
    return observable


  def __assemble_attribute(self, obj, xml_attribute, attr_def_name, cache_object):
    ioc = MispConverter.__get_value(xml_attribute, 'to_ids')
    value = MispConverter.__get_value(xml_attribute, 'value')
    data = MispConverter.__get_value(xml_attribute, 'data')
    
    attribute_definition = self.get_attribute_definition(attr_def_name, cache_object)
    attribute = Attribute()
    self.set_base(xml_attribute, attribute, cache_object)
    attribute.definition = attribute_definition
    attribute.object = obj
    attribute.condition = Condition()
    attribute.condition.value = 'Equals'
    if data:
      # set for files as this is a data element
      attribute.value = {'name': value, 'data': data}
    else:
      attribute.value = value
    attribute.is_ioc = ioc == '1'
    return attribute

  def __assemble_information_source(self, name, role_name, xml_element, cache_object):
    identity = Identity()
    self.set_base(xml_element, identity, cache_object)
    identity.uuid = uuid4()
    identity.name = name
    information_source = InformationSource()
    self.set_base(xml_element, information_source, cache_object)
    information_source.uuid = uuid4()
    information_source.identity = identity
    if role_name:
      role = self.__assemble_role(role_name, xml_element, cache_object)
      information_source.roles.append(role)
    return information_source
    
  def __assemble_role(self, role_name, xml_element, cache_object):
    role = InformationSourceRole()
    self.set_base(xml_element, role, cache_object)
    role.uuid = uuid4()
    role.role = role_name
    return role
  
  def get_information_source(self, xml_element, cache_object):
    infromation_source = cache_object.information_source
    
    isref = self.__assemble_information_source(infromation_source.identity.name, None, xml_element, cache_object)
    isref.identity.name = None
    isref.identity.uuid = uuid4()
    isref.identity.idref = infromation_source.identity.id_

    for role in infromation_source.roles:
      isrefrole = self.__assemble_role(role.role, xml_element, cache_object)
      isref.roles.append(isrefrole)

    for contributing_source in infromation_source.contributing_sources:
      csref = self.__assemble_information_source(contributing_source.identity.name, None, xml_element, cache_object)
      csref.identity.name = None
      csref.identity.idref = infromation_source.identity.id_
      for role in contributing_source.roles:
        csrefrole = self.__assemble_role(role.role, xml_element, cache_object)
        csref.roles.append(csrefrole)

    return isref

  def __set_event(self, xml_event, transformer_group, cache_object):
    self.logger.debug('Mapping Event properties')
    misp_id = MispConverter.__get_value(xml_event, 'id')
    org = MispConverter.__get_value(xml_event, 'org')
    setattr(cache_object, 'org', org)

    risk = MispConverter.__get_value(xml_event, 'risk')
    if not risk:
      risk = MispConverter.__get_value(xml_event, 'threat_level_id')

    info = MispConverter.__get_value(xml_event, 'info')
    published = MispConverter.__get_value(xml_event, 'published')
    analysis = MispConverter.__get_value(xml_event, 'analysis')
    orgc = MispConverter.__get_value(xml_event, 'orgc')
    publish_timestamp = MispConverter.__get_value(xml_event, 'publish_timestamp')
    date = MispConverter.__get_value(xml_event, 'date')

    


    event = Event()
    self.set_base(xml_event, event, cache_object)

    # event.title = u'{0}Event {1} - {2}'.format(title_prefix, misp_id, info)
      
    event.stix_header = STIXHeader()
    self.set_base(xml_event, event.stix_header, cache_object)

    event.stix_header.title = u'{0} Event {1} - {2}'.format(MispConverter.NAMESPACE, misp_id, info)
    event.stix_header.description = self.__assemble_structured_text(xml_event, info, cache_object)
    event.stix_header.short_description = self.__assemble_structured_text(xml_event, info, cache_object)

    # org = provenance, this group will also get an entry in the event permissions with all the rights

    if orgc:
      information_source = self.__assemble_information_source(orgc, 'Initial Author', xml_event, cache_object)
      if org != orgc:
        information_source.contributing_sources.append(self.__assemble_information_source(org, None, xml_event, cache_object))
    else:
      information_source = self.__assemble_information_source(org, 'Initial Author', xml_event, cache_object)
    
    if transformer_group:
      # add the owner due to the transformations
      information_source.contributing_sources.append(self.__assemble_information_source(transformer_group.name, 'Transformer/Translator', xml_event, cache_object))


    setattr(cache_object, 'information_source', information_source)

    event.stix_header.information_source = information_source

    # Set package intent to "Threat Report"
    package_intent = PackageIntent()
    package_intent.intent = 'Threat Report'
    self.set_base(xml_event, package_intent, cache_object)
    event.stix_header.package_intents.append(package_intent)

    event.properties.is_shareable = published == '1'
    event.last_publish_date = datetime.utcfromtimestamp(int(publish_timestamp))
    
    event.analysis = ANALYSIS_MAP.get(analysis, 'None')
    event.risk = RISK_MAP.get(risk, 'None')


    if date:
      event.first_seen = parser.parse(date)
    else:
      event.first_seen = datetime.utcnow()

    event.status = u'Confirmed'

    self.__parse_attributes(xml_event, event, cache_object)
    
    # Create a sorted indicator list
    # self.__create_indicators(event.observables, cache_object)
    
    #remove douplicates
    self.__remove_doublicates(event)
    
    #assemble the event via the assembler
    cache_object_copy = cache_object.make_copy()
    cache_object_copy.complete = True
    cache_object_copy.inflated = True

    # generate generic indicators
    indicators = self.indicator_controller.get_generic_indicators(event, cache_object)
    for indicator in indicators:
      self.set_base(xml_event, indicator, cache_object)
      # indicator.information_source = self.get_information_source(xml_event, cache_object)
      indicator.producer = self.get_information_source(xml_event, cache_object)

    event.indicators = indicators

    pump = json.dumps(event.to_dict(cache_object_copy), sort_keys=True, indent=4, separators=(',', ': '))
    f = open('/home/jhemp/dump.json', 'w+')
    f.write(pump)
    f.close()
    event = self.assembler.assemble(event.to_dict(cache_object_copy), Event, None, cache_object)
   

    return event
    
  def __remove_doublicates(self, event):
    # make observable flat
    
    #remove the observables which are only contain one attribute
    
    #check if the removed attribute was IOC, if it was set IOC to the remaining
    
    pass
    
  def convert_misp_xml_string(self, xml_string, cache_object, transformer_group=None):
    #load xml
    # remove last newlines

    cache_object.insert = True
    cache_object.owner = True
    xml = MispConverter.get_xml_root(xml_string)
    self.logger.debug('Loaded xml')
    # remove the response around the event
    xml_event = xml[0]
    return self.__set_event(xml_event, transformer_group, cache_object)
    
    
    
    




