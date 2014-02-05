# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 24, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.rest.restbase import RestControllerBase
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                                      AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
                                                      ObjectDefinitionBroker
from ce1sus.brokers.definition.handlerdefinitionbroker import \
                                                      AttributeHandlerBroker


class RestDefinitionController(RestControllerBase):

  PARAMETER_INSERT_MAPPER = {'attribute': 'update_attribute_definitions',
                             'object': 'update_object_definitions'}

  def __init__(self):
    RestControllerBase.__init__(self)
    self.attribute_definition_broker = self.broker_factory(
                                                    AttributeDefinitionBroker
                                                       )
    self.object_definition_broker = self.broker_factory(ObjectDefinitionBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)

  def get_function_name(self, parameter, action):
    if action == 'POST':
      return RestDefinitionController.PARAMETER_INSERT_MAPPER.get(parameter,
                                                                   None)
    return None

  def update_attribute_definitions(self, identifier, api_key, **options):
    self.checkIfPriviledged(self.getUserByAPIKey(api_key))
    full_definition = options.get('fulldefinitions', False)
    rest_definition = self.get_post_object()
    try:
      definition = self.attribute_definition_broker.build_attribute_definition(
                               identifier=None,
                               name=rest_definition.name,
                               description=rest_definition.description,
                               regex=rest_definition.regex,
                               class_index=rest_definition.class_index,
                               action='insert',
                               handler_index=rest_definition.handler_index,
                               share=1,
                               relation=1)
      self.attribute_definition_broker.insert(definition, True)
      obj = self._object_to_json(definition,
                               True,
                               full_definition,
                               False)
      return self._return_message(obj)
    except BrokerException as error:
        return self.raise_error('BrokerException', error)

  def update_object_definitions(self, identifier, api_key, **options):
    self.checkIfPriviledged(self.getUserByAPIKey(api_key))
    full_definition = options.get('fulldefinitions', False)
    rest_definition = self.get_post_object()
    try:
      definition = self.object_definition_broker.build_object_definition(
                               identifier=None,
                               name=rest_definition.name,
                               description=rest_definition.description,
                               action='insert',
                               share=1,
                               )
      # check if existing
      try:
        # continue
        definition = self.object_definition_broker.get_defintion_by_chksum(definition.chksum)
      except NothingFoundException:
        # insert
        self.object_definition_broker.insert(definition, False)

      # insert attributes if there are:
      for rest_attribtue in rest_definition.attributes:
        attribute = self.attribute_definition_broker.build_attribute_definition(identifier=None,
                               name=rest_attribtue.name,
                               description=rest_attribtue.description,
                               regex=rest_attribtue.regex,
                               class_index=rest_attribtue.class_index,
                               action='insert',
                               handler_index=rest_attribtue.handler_index,
                               share=1,
                               relation=rest_attribtue.relation)
        # check if attribute exists
        try:
          # continue
          attribute = self.attribute_definition_broker.get_defintion_by_chksum(attribute.chksum)
        except NothingFoundException:
          # insert
          # check if handler and class index exist
          if not attribute.is_class_index_existing(attribute.class_index):
            self.raise_error('UnknownDefinitionException', 'Cannot Insert Attribute as ClassIndex {0} does not exist'.format(attribute.class_index))
          if not self.handler_broker.is_handler_index_existing(attribute.handler_index):
            self.raise_error('UnknownDefinitionException', 'Cannot Insert Attribute as HanlderIndex {0} does not exist'.format(attribute.handler_index))
          self.attribute_definition_broker.insert(attribute, False)

        definition.attributes.append(attribute)

      self.object_definition_broker.do_commit(True)
      obj = self._object_to_json(definition,
                               True,
                               full_definition,
                               False)
      return self._return_message(obj)
    except BrokerException as error:
        return self.raise_error('BrokerException', error)
