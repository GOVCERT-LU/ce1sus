# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 12, 2014
"""
from datetime import datetime
from os.path import dirname
from shutil import move, rmtree
from uuid import uuid4

from ce1sus.controllers.base import BaseController
from ce1sus.db.brokers.definitions.conditionbroker import ConditionBroker
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.object import Object, RelatedObject
from ce1sus.db.classes.observables import Observable, ObservableComposition
from ce1sus.handlers.attributes.filehandler import FileHandler
from ce1sus.helpers.common.hash import hashMD5, fileHashSHA1
from ce1sus.mappers.stix.helpers.common import extract_uuid, make_dict_definitions, set_extended_logging, set_properties
from cybox.common import Time
from cybox.objects.address_object import Address
from cybox.objects.artifact_object import Artifact
from cybox.objects.disk_object import Disk
from cybox.objects.domain_name_object import DomainName
from cybox.objects.file_object import File
from cybox.objects.hostname_object import Hostname
from cybox.objects.network_connection_object import NetworkConnection
from cybox.objects.process_object import Process
from cybox.objects.uri_object import URI
from cybox.objects.user_account_object import UserAccount
from cybox.objects.win_driver_object import WinDriver
from cybox.objects.win_event_log_object import WinEventLog
from cybox.objects.win_executable_file_object import PESection
from cybox.objects.win_executable_file_object import WinExecutableFile
from cybox.objects.win_kernel_hook_object import WinKernelHook
from cybox.objects.win_process_object import WinProcess
from cybox.objects.win_registry_key_object import WinRegistryKey
from cybox.objects.win_service_object import WinService
from cybox.objects.win_volume_object import WinVolume
from cybox.objects.email_message_object import EmailMessage


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class CyboxMapperException(Exception):
  pass


class CyboxMapper(BaseController):

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    # cache all definitions
    self.condition_broker = self.broker_factory(ConditionBroker)
    self.fh = FileHandler()

  def init(self):
    attr_defs = self.attr_def_broker.get_all()
    self.attr_defs = make_dict_definitions(attr_defs)
    obj_defs = self.obj_def_broker.get_all()
    self.obj_defs = make_dict_definitions(obj_defs)
    conditions = self.condition_broker.get_all()
    self.conditions = self.make_dict_conditions(conditions)

  def get_time(self, start_time=None, end_time=None, produced_time=None, received_time=None):
    return Time(start_time, end_time, produced_time, received_time)

  def make_dict_conditions(self, conditions):
    result = dict()
    for condition in conditions:
      result[condition.value] = condition
    return result

  def get_object_definition(self, instance):
    definition = None
    if isinstance(instance, Hostname):
      definition = self.obj_defs.get('Hostname')
    elif isinstance(instance, Address):
      if instance.category == 'e-mail':
        definition = self.obj_defs.get('email')
      elif instance.category == 'ipv4-addr':
        definition = self.obj_defs.get('Address')
      else:
        raise CyboxMapperException(u'Not defined')
    elif isinstance(instance, WinDriver):
      definition = self.obj_defs.get('WinDriver')
    elif isinstance(instance, WinExecutableFile):
      definition = self.obj_defs.get('WinExecutableFile')
    elif isinstance(instance, File):
      definition = self.obj_defs.get('File')
    elif isinstance(instance, URI):
      definition = self.obj_defs.get('URI')
    elif isinstance(instance, DomainName):
      definition = self.obj_defs.get('DomainName')
    elif isinstance(instance, Process):
      if isinstance(instance, WinProcess):
        definition = self.obj_defs.get('WinProcess')
      if isinstance(instance, WinService):
        definition = self.obj_defs.get('WinService')
      else:
        definition = self.obj_defs.get('Process')
    elif isinstance(instance, WinEventLog):
      definition = self.obj_defs.get('WinEventLog')
    elif isinstance(instance, UserAccount):
      definition = self.obj_defs.get('UserAccount')
    elif isinstance(instance, WinRegistryKey):
      definition = self.obj_defs.get('WindowsRegistryKey')
    elif isinstance(instance, WinVolume):
      definition = self.obj_defs.get('WinVolume')
    elif isinstance(instance, NetworkConnection):
      definition = self.obj_defs.get('NetworkConnection')
    elif isinstance(instance, Disk):
      definition = self.obj_defs.get('Disk')
    elif isinstance(instance, WinKernelHook):
      definition = self.obj_defs.get('WinKernelHook')
    elif isinstance(instance, Artifact):
      definition = self.obj_defs.get('Artifact')
    elif isinstance(instance, EmailMessage):
      definition = self.obj_defs.get('email')
    if definition:
      return definition
    else:
      raise CyboxMapperException(u'Object mapping for {0} is not defined'.format(instance))

  def get_attribute_definition(self, instance):
    definition = None
    if isinstance(instance, Hostname):
      definition = self.attr_defs.get(u'Hostname_Value')
    elif isinstance(instance, Address):
      if instance.category == 'e-mail':
        if instance.is_source:
          definition = self.attr_defs.get('email_sender')
        elif instance.is_destination:
          definition = self.attr_defs.get('email_to')
        else:
          # it can only be source that makes sense
          definition = self.attr_defs.get('email_sender')
      elif instance.category == 'ipv4-addr':
        definition = self.attr_defs.get('ipv4_addr')
      else:
        raise CyboxMapperException(u'Not defined')
    elif isinstance(instance, URI):
      if instance.type_ == 'URL':
        definition = self.attr_defs.get('url')
      else:
        raise CyboxMapperException(u'Not defined')
    elif isinstance(instance, DomainName):
      definition = self.attr_defs.get('DomainName_Value')
    if definition:
      return definition
    else:
      raise CyboxMapperException(u'Attribute mapping for {0} is not defined'.format(instance))

  def __create_attribute_by_def(self, def_name, parent, value, is_indicator, condition=None, tlp=None):
    attribute = Attribute()
    set_properties(attribute)
    attribute.object = parent
    attribute.is_ioc = is_indicator
    attribute.definition = self.attr_defs.get(def_name, None)
    db_cond = None
    if condition:
      db_cond = self.conditions[condition]

    else:
      db_cond = self.conditions['Equals']
    attribute.condition = db_cond
    attribute.condition_id = db_cond.identifier

    if not attribute.definition:
      raise CyboxMapperException('Definition {0} is not definied'.format(def_name))
    attribute.value = value
    return attribute

  def create_file_attributes(self, cybox_file, parent, is_indicator, tlp_id):
    attributes = list()
    if cybox_file.encryption_algorithm:
      attributes.append(self.__create_attribute_by_def('encryption_mechanism', parent, cybox_file.encryption_algorithm, is_indicator, None, tlp_id))
    if cybox_file.accessed_time:
      attributes.append(self.__create_attribute_by_def('Accessed_Time', parent, cybox_file.accessed_time, is_indicator, None, tlp_id))
    if cybox_file.created_time:
      attributes.append(self.__create_attribute_by_def('Created_Time', parent, cybox_file.created_time, is_indicator, None, tlp_id))
    if cybox_file.file_extension:
      attributes.append(self.__create_attribute_by_def('File_Extension', parent, cybox_file.file_extension, is_indicator, None, tlp_id))
    if cybox_file.modified_time:
      attributes.append(self.__create_attribute_by_def('Modified_Time', parent, cybox_file.modified_time, is_indicator, None, tlp_id))
    if cybox_file.file_name:
      attributes.append(self.__create_attribute_by_def('File_Name', parent, cybox_file.file_name, is_indicator, cybox_file.file_name.condition, tlp_id))
    if cybox_file.hashes:
      # TODO: clean up  when cybox implements this differently
      try:
        if cybox_file.hashes.md5:
          attributes.append(self.__create_attribute_by_def('hash_md5', parent, cybox_file.hashes.md5, is_indicator, None, tlp_id))
      except AttributeError:
        pass
      try:
        if cybox_file.hashes.sha1:
          attributes.append(self.__create_attribute_by_def('hash_sha1', parent, cybox_file.hashes.sha1, is_indicator, None, tlp_id))
      except AttributeError:
        pass
      try:
        if cybox_file.hashes.sha256:
          attributes.append(self.__create_attribute_by_def('hash_sha256', parent, cybox_file.hashes.sha256, is_indicator, None, tlp_id))
      except AttributeError:
        pass
      try:
        if cybox_file.hashes.sha384:
          attributes.append(self.__create_attribute_by_def('hash_sha384', parent, cybox_file.hashes.sha384, is_indicator, None, tlp_id))
      except AttributeError:
        pass
      try:
        if cybox_file.hashes.sha512:
          attributes.append(self.__create_attribute_by_def('hash_sha512', parent, cybox_file.hashes.sha512, is_indicator, None, tlp_id))
      except AttributeError:
        pass

    if cybox_file.full_path:
      attributes.append(self.__create_attribute_by_def('Full_Path', parent, cybox_file.full_path, is_indicator, cybox_file.full_path.condition, tlp_id))

    if cybox_file.size:
      attributes.append(self.__create_attribute_by_def('Size_In_Bytes', parent, cybox_file.size, is_indicator, None, tlp_id))
    if cybox_file.file_extension:
      attributes.append(self.__create_attribute_by_def('File_Extension', parent, cybox_file.file_extension, is_indicator, None, tlp_id))

    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for file')

  def create_process(self, process, parent, is_indicator, tlp_id):
    attributes = list()
    if process.name:
      attributes.append(self.__create_attribute_by_def('Full_Path', parent, process.name, is_indicator, process.name.condition, tlp_id))

    # check it it is not an other type of file like WinProcess
    if isinstance(process, WinProcess):
      if isinstance(process, WinService):
        if process.service_name:
          attributes.append(self.__create_attribute_by_def('Service_Name', parent, process.service_name, is_indicator, process.service_name.condition, tlp_id))

    if attributes:
      return attributes
    else:
      raise CyboxMapperException('No attribute was created for process')

  def create_wineventlog(self, wineventlog, parent, is_indicator, tlp_id):
    attributes = list()
    if wineventlog.eid:
      attributes.append(self.__create_attribute_by_def('EID', parent, wineventlog.eid, is_indicator, None, tlp_id))

    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for wineventlog')

  def create_useraccount(self, useraccount, parent, is_indicator, tlp_id):
    attributes = list()
    if useraccount.username:
      attributes.append(self.__create_attribute_by_def('Username', parent, useraccount.username, is_indicator, useraccount.username.condition, tlp_id))

    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for useraccount')

  def create_win_reg_key(self, win_reg_key, parent, is_indicator, tlp_id):
    attributes = list()
    if win_reg_key.key:
      attributes.append(self.__create_attribute_by_def('WindowsRegistryKey_Key', parent, win_reg_key.key, is_indicator, win_reg_key.key.condition, tlp_id))
    if win_reg_key.values:
      for value in win_reg_key.values:
        attributes.append(self.__create_attribute_by_def('WindowsRegistryKey_RegistryValue_Data', parent, value.data.value, is_indicator, value.data.condition, tlp_id))
    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for win_reg_key')

  def create_network_connection(self, network_connection, parent, is_indicator, tlp_id):
    attributes = list()
    if network_connection.source_socket_address:
      attributes.append(self.__create_attribute_by_def('is_type', parent, 'Source', False, None, tlp_id))
      if network_connection.source_socket_address.port:
        attributes.append(self.__create_attribute_by_def('Port', parent, network_connection.source_socket_address.port.port_value, False, None, tlp_id))

    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for win_reg_key')

  def create_win_volume(self, win_volume, parent, is_indicator, tlp_id):
    attributes = list()
    if win_volume.drive_letter:
      attributes.append(self.__create_attribute_by_def('Drive_Letter', parent, win_volume.drive_letter, False, win_volume.drive_letter.condition, tlp_id))

    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for win_reg_key')

  def create_disk(self, disk, parent, is_indicator, tlp_id):
    attributes = list()
    if disk.disk_name:
      attributes.append(self.__create_attribute_by_def('Disk_Name', parent, disk.disk_name, False, disk.disk_name.condition, tlp_id))

    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for win_reg_key')


  def create_artifact(self, artifact, parent, is_indicator, tlp_id):
    attributes = list()
    if artifact.data:
      tmp_filename = hashMD5(datetime.utcnow())
      binary_data = artifact.data
      tmp_folder = self.fh.get_tmp_folder()
      tmp_path = tmp_folder + '/' + tmp_filename

      # create file in tmp
      file_obj = open(tmp_path, "w")
      file_obj.write(binary_data)
      file_obj.close()

      sha1 = fileHashSHA1(tmp_path)
      rel_folder = self.fh.get_rel_folder()
      dest_path = self.fh.get_dest_folder(rel_folder) + '/' + sha1

      # move it to the correct place
      move(tmp_path, dest_path)
      # remove temp folder
      rmtree(dirname(tmp_path))
      value = rel_folder + '/' + sha1
      attributes.append(self.__create_attribute_by_def('Raw_Artifact', parent, value, False, None, tlp_id))

    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for win_reg_key')

  def create_emailmessage(self, cybox_email, parent, is_indicator, tlp_id):
    attribtues = list()
    if cybox_email.header:
      if cybox_email.header.bcc:
        for recipient in cybox_email.header.bcc:
          pass
      if cybox_email.header.cc:
        for recipient in cybox_email.header.cc:
          pass
      if cybox_email.header.errors_to:
        attribtues.append(self.__create_attribute_by_def('email_errors_to', parent, cybox_email.header.errors_to, is_indicator, cybox_email.header.errors_to.condition, tlp_id))
      if cybox_email.header.message_id:
        attribtues.append(self.__create_attribute_by_def('email_message_id', parent, cybox_email.header.message_id, is_indicator, None, tlp_id))
      if cybox_email.header.mime_version:
        attribtues.append(self.__create_attribute_by_def('email_mime_version', parent, cybox_email.header.mime_version, is_indicator, None, tlp_id))
      if cybox_email.header.from_:
        attribtues.append(self.__create_attribute_by_def('email_from', parent, cybox_email.header.from_.address_value, is_indicator, None, tlp_id))
      if cybox_email.header.to:
        attribtues.append(self.__create_attribute_by_def('email_to', parent, cybox_email.header.to.address_value, is_indicator, None, tlp_id))
      if cybox_email.header.x_mailer:
        attribtues.append(self.__create_attribute_by_def('email_x_mailer', parent, cybox_email.header.x_mailer.address_value, is_indicator, None, tlp_id))
      if cybox_email.header.x_originating_ip:
        attribtues.append(self.__create_attribute_by_def('email_x_originating_ip', parent, cybox_email.header.x_originating_ip, is_indicator, None, tlp_id))
      if cybox_email.header.in_reply_to:
        attribtues.append(self.__create_attribute_by_def('email_in_reply_to', parent, cybox_email.header.in_reply_to, is_indicator, None, tlp_id))
        for recipient in cybox_email.header.in_reply_to:
          pass
      if cybox_email.subject:
        attribtues.append(self.__create_attribute_by_def('email_subject', parent, cybox_email.subject, is_indicator, None, tlp_id))
      if cybox_email.header.from_:
        attribtues.append(self.__create_attribute_by_def('email_from', parent, cybox_email.header.from_.address_value, is_indicator, None, tlp_id))

    if cybox_email.raw_body:
      attribtues.append(self.__create_attribute_by_def('email_raw_body', parent, cybox_email.raw_body, is_indicator, None, tlp_id))
    if cybox_email.raw_header:
      attribtues.append(self.__create_attribute_by_def('email_raw_header', parent, cybox_email.raw_header, is_indicator, None, tlp_id))
    if cybox_email.email_server:
      attribtues.append(self.__create_attribute_by_def('email_server', parent, cybox_email.email_server, is_indicator, None, tlp_id))

      # email_link
      if attribtues:
        return attribtues
      else:
        raise CyboxMapperException('No attribute was created for email')

  def create_win_kernel_hook(self, win_kernel_hook, parent, is_indicator, tlp_id):
    attributes = list()
    if win_kernel_hook.hooked_module:
      attributes.append(self.__create_attribute_by_def('Hooked_Module', parent, win_kernel_hook.hooked_module, False, win_kernel_hook.hooked_module.condition, tlp_id))

    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for win_reg_key')

  def create_win_driver(self, win_driver, parent, is_indicator, tlp_id):
    attributes = list()
    if win_driver.driver_name:
      attributes.append(self.__create_attribute_by_def('Driver_Name', parent, win_driver.driver_name, False, win_driver.driver_name.condition, tlp_id))
    if win_driver.device_object_list:
      for do in win_driver.device_object_list:
        if do.attached_to_driver_name:
          attributes.append(self.__create_attribute_by_def('Attached_To_Driver_Name', parent, do.attached_to_driver_name, False, do.attached_to_driver_name.condition, tlp_id))
    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for win_driver')

  def create_win_executable_file(self, win_executable_file, parent, is_indicator, tlp_id):
    attributes = list()
    if hasattr(win_executable_file, 'driver_name'):
      # TODO
      attributes.append(self.__create_attribute_by_def('Driver_Name', parent, win_executable_file.driver_name, False, win_executable_file.driver_name.condition, tlp_id))
    if win_executable_file.sections:
      for section in win_executable_file.sections:
        if isinstance(section, PESection):
          if section.section_header:
            attributes.append(self.__create_attribute_by_def('Section_Header_Name', parent, section.section_header.name, False, section.section_header.name.condition, tlp_id))
    if win_executable_file.digital_signature:
      # TODO handle digital signatures
      return list()

    if attributes:
      return attributes
    else:
      # check it it is not an other type of file like WinExecutableFile
      raise CyboxMapperException('No attribute was created for win_executable_file')

  def create_attributes(self, properties, parent_object, tlp_id, is_indicator, seen_conditions):
    # TODO: Create custom properties
    attribute = Attribute()
    attribute.tlp_level_id = tlp_id
    attribute.object = parent_object
    attribute.is_ioc = is_indicator
    set_properties(attribute)
    if isinstance(properties, Hostname):
      prop = properties.hostname_value
    elif isinstance(properties, Address):
      prop = properties.address_value
    elif isinstance(properties, WinDriver):
      return self.create_win_driver(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, WinExecutableFile):
      return self.create_win_executable_file(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, File):
      return self.create_file_attributes(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, URI):
      prop = properties.value
    elif isinstance(properties, DomainName):
      prop = properties.value
    elif isinstance(properties, Process):
      return self.create_process(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, WinEventLog):
      return self.create_wineventlog(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, UserAccount):
      return self.create_useraccount(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, WinRegistryKey):
      return self.create_win_reg_key(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, NetworkConnection):
      return self.create_network_connection(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, WinVolume):
      return self.create_win_volume(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, Disk):
      return self.create_disk(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, WinKernelHook):
      return self.create_win_kernel_hook(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, Artifact):
      return self.create_artifact(properties, parent_object, is_indicator, tlp_id)
    elif isinstance(properties, EmailMessage):
      return self.create_emailmessage(properties, parent_object, is_indicator, tlp_id)
    else:
      raise CyboxMapperException('No attribute definiton defined for {0}'.format(properties))
    counter = 0
    for value in prop.values:
      # TODO Check if there are more values in hostname
      attribute.definition = self.get_attribute_definition(properties)
      attribute.value = value
      counter = counter + 1
    if counter > 1:
      raise CyboxMapperException(u'More values are present but this is not yet implemented')
    attribute.condition = self.get_condition(prop.condition, seen_conditions)

    if attribute.value:
      return [attribute]
    else:
      raise CyboxMapperException(u'Attribute mapping for {0} is not defined'.format(properties))

  def get_condition(self, value, seen_conditions):
    condition = seen_conditions.get(value, None)
    if condition:
      return condition
    else:
      condition = self.condition_broker.get_condition_by_value(value)
      seen_conditions[value] = condition
    return condition

  def create_object(self, cybox_object, observable, user, tlp_id, is_indicator, seen_conditions):
    ce1sus_object = Object()
    ce1sus_object.tlp_level_id = tlp_id
    set_properties(ce1sus_object)
    # Create the container
    ce1sus_object.observable = observable
    if hasattr(cybox_object, 'id'):
      ce1sus_object.uuid = extract_uuid(cybox_object.id_)
    else:
      # unfortenatley one must be generated
      ce1sus_object.uuid = uuid4()
    if cybox_object.properties:
      ce1sus_object.definition = self.get_object_definition(cybox_object.properties)
      attributes = self.create_attributes(cybox_object.properties, ce1sus_object, tlp_id, is_indicator, seen_conditions)
    else:
      raise CyboxMapperException('No properties found')
    set_extended_logging(ce1sus_object, user, user.group)

    # Create attributes
    if cybox_object.related_objects:
      for related_object in cybox_object.related_objects:
        rel_obj = RelatedObject()
        rel_obj.parent = ce1sus_object
        rel_obj.relation = related_object.relationship
        rel_obj.object = self.create_object(related_object, observable, user, tlp_id, is_indicator, seen_conditions)
        if rel_obj.object:
          rel_obj.object.parent = None
          rel_obj.object.parent_id = None
          ce1sus_object.related_objects.append(rel_obj)

    if attributes or ce1sus_object.related_objects:
      if attributes:
        for attribute in attributes:
          set_extended_logging(attribute, user, user.group)

        ce1sus_object.attributes = attributes

      return ce1sus_object
    else:
      return None

  def create_observable(self, observable, event, user, tlp_id, is_indicator=False, seen_conditions=None):
    if observable.idref:
      return None
    if not seen_conditions:
      seen_conditions = dict()
    ce1sus_observable = Observable()
    ce1sus_observable.tlp_level_id = tlp_id
    set_properties(ce1sus_observable)
    if observable.id_:
      ce1sus_observable.uuid = extract_uuid(observable.id_)

    set_extended_logging(ce1sus_observable, user, user.group)
    ce1sus_observable.event = event
    ce1sus_observable.parent = event
    # an observable has either a composition or a single object
    if observable.observable_composition:
      composition = ObservableComposition()
      composition.operator = observable.observable_composition.operator
      for child in observable.observable_composition.observables:
        child_observable = self.create_observable(child, event, user, tlp_id, is_indicator, seen_conditions)
        # As the observable is not on the root level remove the link to the parent
        if child_observable:
          child_observable.event = None
          composition.observables.append(child_observable)
      ce1sus_observable.observable_composition = composition
      return ce1sus_observable
    else:

      ce1sus_observable.uuid = extract_uuid(observable.id_)
      # create a cybox object
      obj = self.create_object(observable.object_, ce1sus_observable, user, tlp_id, is_indicator, seen_conditions)
      ce1sus_observable.object = obj
      # TODO
      if obj:
        return ce1sus_observable
      else:
        return None
