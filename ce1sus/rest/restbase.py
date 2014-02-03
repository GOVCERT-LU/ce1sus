# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import json
from ce1sus.api.restclasses import RestClass, populate_classname_by_dict, \
                                   get_object_data
from importlib import import_module
import cherrypy
from ce1sus.controllers.base import Ce1susBaseController
from ce1sus.brokers.event.eventclasses import Event, Attribute
from dagr.db.broker import NothingFoundException
from dagr.helpers.datumzait import datumzait
from dagr.helpers.converters import ObjectConverter
from ce1sus.helpers.bitdecoder import BitValue
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                                      AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
                                                        ObjectDefinitionBroker
from dagr.helpers.hash import fileHashSHA256, hashMD5, hashSHA256
from ce1sus.common.handlers.filehandler import FileHandler
import os
from os.path import exists, dirname
from shutil import move, rmtree
import re
from ce1sus.web.helpers.protection import Protector
import base64
from os import makedirs


class RestAPIException(Exception):
  """
  Exception base for handler exceptions
  """
  def __init__(self, message):
    Exception.__init__(self, message)


class RestControllerBase(Ce1susBaseController):

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.object_definition_broker = self.broker_factory(ObjectDefinitionBroker)
    self.attribute_definition_broker = self.broker_factory(
                                                    AttributeDefinitionBroker
                                                       )
    self.base_path = WebConfig.get_instance().get('files')

  @staticmethod
  def __instantiate_class(classname):
    module = import_module('.restclasses', 'ce1sus.api')
    clazz = getattr(module, classname)
    # instantiate
    instance = clazz()
    # check if handler base is implemented
    if not isinstance(instance, RestClass):
      Protector.clearRestSession()
      raise RestAPIException(('{0} does not implement '
                              + 'RestClass').format(classname))
    return instance

  def _to_rest_object(self, obj, is_owner=False, full=True):
    classname = 'Rest' + obj.__class__.__name__
    instance = RestControllerBase.__instantiate_class(classname)

    instance.populate(obj, is_owner, full)
    return instance

  def _object_to_json(self,
                    obj,
                    is_owner=False,
                    full=False,
                    with_definition=False):
    instance = self._to_rest_object(obj, is_owner, full)

    result = dict(instance.to_dict(full=full,
                             with_definition=with_definition).items()
                 )
    return result

  def _return_list(self, array):
    result = {'list': array}
    return self._return_message(result)

  def _return_message(self, dictionary):
    result = dict(dictionary.items()
                  + self._create_status().items())
    return json.dumps(result)

  def _create_status(self, classname=None, message=None):
    result = dict()
    result['response'] = dict()
    result['response']['errors'] = list()
    if (classname is None and message is None):
      result['response']['status'] = 'OK'
    else:
      result['response']['status'] = 'ERROR'
      result['response']['errors'].append({classname: '{0}'.format(message)})
    return result

  def raise_error(self, classname, message):
    raise RestAPIException('{0}: {1}'.format(classname, message))

  def get_post_object(self):
    try:
      content_length = cherrypy.request.headers['Content-Length']
      raw = cherrypy.request.body.read(int(content_length))
      json_data = json.loads(raw)
      key, value = get_object_data(json_data)
      obj = populate_classname_by_dict(key, value, False)
      return obj
    except AttributeError as error:
      self._get_logger().error('An error occurred by getting the post object {0}'.format(error))
      self.raise_error('UnRecoverableException',
                      'JSON structure error. {0}'.format(error))
    except Exception as error:
      self._get_logger().error('An error occurred by getting the post object {0}'.format(error))
      self.raise_error('UnRecoverableException',
                      'An unrecoverable error occurred. {0}'.format(error))

  def _convert_to_attribute_definition(self,
                                   rest_attribute_definition,
                                   object_definition,
                                   commit=False):
    # get definition if existing
      try:
        attr_definition = self.attribute_definition_broker.get_defintion_by_chksum(
                                                rest_attribute_definition.chksum
                                                                            )
      except NothingFoundException:
        self.raise_error('UnknownDefinitionException',
                      'The attribute definition with CHKSUM {0} is not defined.'.format(
                                                  rest_attribute_definition.chksum))

        self.attribute_definition_broker.insert(attr_definition, commit=False)

        # update objectRelations as the attribute was not set
        object_definition.attributes.append(attr_definition)
        self.object_broker.update(attr_definition, commit=False)
        self.object_broker.do_commit(commit)

      return attr_definition

  def _create_attribute(self,
                        rest_attribute,
                        attribute_definition,
                        obj,
                        commit=False):

    user = obj.creator

    # create the actual attribute
    db_attribute = Attribute()
    db_attribute.identifier = None
    # TODO: collect definition and check if the handler uses is a filehandler...
    filename = ''
    if (re.match(r'^\{.*file.*:.*\}$', rest_attribute.value)):
      try:
        str_value = rest_attribute.value
        value = json.loads(str_value)

        json_file = value.get('file', None)
        if json_file:
          filename = json_file[0]
          str_data = json_file[1]
          value = base64.b64decode(str_data)
          # Relative position
          tmp_folder = self.base_path + '/tmp/' + hashMD5('{0}'.format(datumzait.now()))
          os.mkdir(tmp_folder)
          tmp_folder = tmp_folder + '/{0}'.format(filename)

          file_object = open(tmp_folder, "wb")
          file_object.write(value)
          file_object.close()

          # filename
          destination = FileHandler.getDestination()
          # in case the directories doesn't exist
          if not exists(self.base_path + '/' + destination):
            makedirs(self.base_path + '/' + destination)

          file_hash = fileHashSHA256(tmp_folder)
          filename = FileHandler.getFileName(file_hash, hashSHA256(filename))

          destination = destination + filename
          move(tmp_folder, self.base_path + '/' + destination)
          # delete the folder
          foldername = dirname(tmp_folder)
          rmtree(foldername)

          value = destination
      except Exception as error:
        self._get_logger().error('Error occured while saving file:{0}'.format(error))
        value = '(Corrupted File)'
    else:
      value = rest_attribute.value
    db_attribute.value = value
    db_attribute.object = obj
    db_attribute.object_id = obj.identifier
    db_attribute.definition = attribute_definition
    db_attribute.def_attribute_id = attribute_definition.identifier
    db_attribute.created = datumzait.utcnow()
    db_attribute.modified = datumzait.utcnow()
    db_attribute.creator_id = user.identifier
    db_attribute.modifier_id = user.identifier
    db_attribute.bit_value = BitValue('0', db_attribute)
    db_attribute.bit_value.is_rest_instert = True
    if rest_attribute.share == 1:
      db_attribute.bit_value.is_shareable = True
    else:
      db_attribute.bit_value.is_shareable = False
    ObjectConverter.setInteger(db_attribute,
                               'ioc',
                               rest_attribute.ioc)

    self.attribute_broker.insert(db_attribute, commit=False)

    return db_attribute

  def _convert_to_attribues(self, rest_attributes, obj, commit=False):

    result = list()
    for attribute in rest_attributes:
      if attribute.value != '(Not Provided)':
        attr_definition = self._convert_to_attribute_definition(
                                                         attribute.definition,
                                                         obj.definition,
                                                         commit)
        db_attribute = self._create_attribute(attribute,
                                           attr_definition,
                                           obj,
                                           commit)
        if (db_attribute.definition.identifier == 12
              or db_attribute.definition.identifier == 13):
          value = json.loads(attribute.value)
          json_file = value.get('file', None)
          if json_file:
            filename = json_file[0]
            # Add the same for the filename attribute
            db_attr_filename = Attribute()
            db_attr_filename.identifier = None
            db_attr_filename.value = filename
            db_attr_filename.object = obj
            db_attr_filename.object_id = obj.identifier
            attr_def = self.attribute_definition_broker.get_by_id(7)
            db_attr_filename.definition = attr_def
            db_attr_filename.def_attribute_id = attr_def.identifier
            db_attr_filename.created = datumzait.utcnow()
            db_attr_filename.modified = datumzait.utcnow()
            db_attr_filename.creator_id = obj.creator.identifier
            db_attr_filename.modifier_id = obj.creator.identifier
            db_attr_filename.bit_value = BitValue('0', db_attr_filename)
            db_attr_filename.bit_value.is_rest_instert = True
            if attribute.share == 1:
              db_attr_filename.bit_value.is_shareable = True
            else:
              db_attr_filename.bit_value.is_shareable = False
            ObjectConverter.setInteger(db_attr_filename,
                                       'ioc',
                                       attribute.ioc)
            self.attribute_broker.insert(db_attr_filename, commit=commit)
            result.append(db_attr_filename)
        result.append(db_attribute)
    return result

  def _convert_to_object_definition(self, rest_object_definition, commit=False):
    # create object

    # get definition if existing
    try:
      obj_definition = self.object_definition_broker.get_defintion_by_chksum(
                                                    rest_object_definition.chksum
                                                                      )
    except NothingFoundException:
      self.raise_error('UnknownDefinitionException',
                      'The object definition with CHKSUM {0} is not defined.'.format(
                                                  rest_object_definition.chksum))
    return obj_definition

  def _convert_to_object(self, rest_object, parent, event, commit=False):
    object_definition = self._convert_to_object_definition(rest_object.definition,
                                                        commit)

    user = parent.creator
    if isinstance(parent, Event):
      db_object = self.object_broker.build_object(None,
                                               parent,
                                               object_definition,
                                               user,
                                               None)
    else:
      db_object = self.object_broker.build_object(None,
                                               None,
                                               object_definition,
                                               user,
                                               parent.identifier)
      db_object.parent_event_id = event.identifier
    # flush to DB
    db_object.bit_value.is_rest_instert = True
    if rest_object.share == 1:
      db_object.bit_value.is_shareable = True
    else:
      db_object.bit_value.is_shareable = False
    self.object_broker.insert(db_object, commit=commit)

    return db_object
