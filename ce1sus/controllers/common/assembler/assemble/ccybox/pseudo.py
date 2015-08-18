# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""

import base64
from datetime import datetime
from os.path import dirname
from shutil import move, rmtree

from ce1sus.controllers.common.basechanger import BaseChanger, AssemblerException
from ce1sus.db.brokers.definitions.conditionbroker import ConditionBroker
from ce1sus.db.brokers.definitions.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.db.brokers.definitions.typebrokers import AttributeTypeBroker
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.object import Object, RelatedObject
from ce1sus.db.common.broker import NothingFoundException, BrokerException
from ce1sus.handlers.attributes.filehandler import FileHandler
from ce1sus.helpers.common.hash import hashMD5, fileHashSHA1


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class PseudoCyboxAssembler(BaseChanger):

  def __init__(self, config, session=None):
    super(PseudoCyboxAssembler, self).__init__(config, session)
    self.condition_broker = self.broker_factory(ConditionBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)
    self.value_type_broker = self.broker_factory(AttributeTypeBroker)

  def get_object_definition(self, json, cache_object):
    uuid = json.get('definition_id', None)
    if not uuid:
      definition = json.get('definition', None)
      if definition:
        uuid = definition.get('identifier', None)
    if uuid:
      od = cache_object.seen_obj_defs.get(uuid, None)
      if od:
        return od
      else:
        try:
          definition = self.obj_def_broker.get_by_uuid(uuid)
        except BrokerException as error:
          raise AssemblerException(error)
        cache_object.seen_obj_defs[uuid] = definition
        return definition
    raise AssemblerException('Could not find a definition in the object')

  def assemble_object(self, observable, json, cache_object, set_observable=True):
    if json:
      obj = Object()
      self.set_base(obj, json, cache_object, observable)

      # set definition
      definition = self.get_object_definition(json, cache_object)
      # obj.definition = definition
      obj.definition = definition

      if set_observable:
        obj.observable = [observable]

      rel_objs = json.get('related_objects', None)
      if rel_objs:
        for rel_obj in rel_objs:
          rel_obj_inst = self.assemble_related_object(obj, rel_obj, cache_object)
          obj.related_objects.append(rel_obj_inst)

      attributes = json.get('attributes')
      if attributes:
        for attribute in attributes:
          attr = self.assemble_attribute(obj, attribute, cache_object)
          if attr:
            obj.attributes.append(attr)

      return obj

  def assemble_related_object(self, obj, json, cache_object):
    if json:
      child_obj_json = json.get('object')
      # TODO: findout why observable is unset afterwards
      # observable = obj.observable[0]
      child_obj = self.assemble_object(obj.parent, child_obj_json, cache_object, set_observable=False)

      # update parent
      related_object = RelatedObject()
      # the properties of the child are the same as for the related object as this is in general only a container
      self.set_base(related_object, json, cache_object, obj)

      # Properties should be the same as the one from the related object except they are not in the json
      if child_obj_json.get('properties', None) is None:
        child_obj.dbcode = related_object.dbcode
      if child_obj_json.get('tlp', None) is None:
        child_obj.tlp_level_id = related_object.tlp_level_id

      # also check the other way round
      if json.get('properties', None) is None:
        related_object.dbcode = child_obj.dbcode
      if json.get('tlp', None) is None:
        related_object.tlp_level_id = child_obj.tlp_level_id

      related_object.parent = obj
      related_object.object = child_obj
      related_object.relationship = json.get('relationship', None)
      if related_object.relationship == 'None':
        related_object.relationship = None
      obj.related_objects.append(related_object)

      return related_object

  def get_attribute_definition(self, json, cache_object):
    uuid = json.get('definition_id', None)
    if not uuid:
      definition = json.get('definition', None)
      if definition:
        uuid = definition.get('identifier', None)
    if uuid:
      ad = cache_object.seen_attr_defs.get(uuid, None)
      if ad:
        return ad
      else:
        try:
          definition = self.attr_def_broker.get_by_uuid(uuid)
        except NothingFoundException as error:
          raise AssemblerException(error)
        except BrokerException as error:
          raise AssemblerException(error)
        cache_object.seen_attr_defs[uuid] = definition
        return definition
    raise AssemblerException('Could not find a definition in the attribute')


  def assemble_attribute(self, obj, json, cache_object):

    if json:
      attribute = Attribute()
      self.set_base(attribute, json, cache_object, obj)

      definition = self.get_attribute_definition(json, cache_object)

      attribute.definition = definition

      attribute.object = obj

      # attention to raw_artefacts!!!
      value = json.get('value', None)
      handler_uuid = '{0}'.format(definition.attribute_handler.uuid)
      if handler_uuid in ['0be5e1a0-8dec-11e3-baa8-0800200c9a66', 'e8b47b60-8deb-11e3-baa8-0800200c9a66']:

        fh = FileHandler()

        tmp_filename = hashMD5(datetime.utcnow())

        binary_data = base64.b64decode(value)
        tmp_folder = fh.get_tmp_folder()
        tmp_path = tmp_folder + '/' + tmp_filename

        file_obj = open(tmp_path, "w")
        file_obj.write(binary_data)
        file_obj.close()

        sha1 = fileHashSHA1(tmp_path)
        rel_folder = fh.get_rel_folder()
        dest_path = fh.get_dest_folder(rel_folder) + '/' + sha1

        # move it to the correct place
        move(tmp_path, dest_path)
        # remove temp folder
        rmtree(dirname(tmp_path))

        attribute.value = rel_folder + '/' + sha1
      else:
        attribute.value = value

      condition_uuid = json.get('condition_id', None)
      if not condition_uuid:
        condition = json.get('condition', None)
        if condition:
          condition_uuid = condition.get('identifier', None)
      if condition_uuid:
        condition = self.get_condition(condition_uuid, cache_object)
        attribute.condition_id = condition.identifier

      attribute.is_ioc = json.get('ioc', 0)

      return attribute

  def get_condition(self, uuid, cache_object):
    definition = cache_object.seen_conditions.get(uuid, None)
    if definition:
      return definition
    else:
      definition = self.condition_broker.get_by_uuid(uuid)
      cache_object.seen_conditions[uuid] = definition
      return definition
