# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 20, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'
from dagr.db.broker import BrokerBase
from importlib import import_module
from ce1sus.web.helpers.handlers.base import HandlerBase

class AttributeHandlerBroker(BrokerBase):

  __handlerDefinitions = {0: 'generichandler.GenericHandler',
                          1: 'filehandler.FileWithHashesHandler',
                          2: 'tickethandler.TicketHandler',
                          3: 'tickethandler.CVEHandler',
                          5: 'multiplegenerichandler.MultipleGenericHandler',
                          6: 'filehandler.FileHandler',
                          7: 'datehandler.DateHandler',
                          8: 'cbvaluehandler.CBValueHandler',
                          9: 'texthandler.TextHandler'}

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return None

  def getHandlerDefinitions(self):
    """ returns the table definitions where the key is the value and value the
    index of the tables.

    Note: Used for displaying the definitions of the tables in combo boxes

    :returns: Dictionary
    """
    result = dict()
    for index, handlerName in (AttributeHandlerBroker.
                                        __handlerDefinitions.iteritems()):
      key = handlerName.split('.')[1]
      value = index
      result[key] = value
    return result

  def getHandlerName(self, index):
    """
    returns the handler name

    :param index: index of the class name
    :type index: Integer

    :returns: String
    """
    # Test if the index is
    if index < 0 and index >= len(self.__handlerDefinitions):
      raise Exception('Invalid input "{0}"'.format(index))
    return self.__handlerDefinitions[index]

  def getHandler(self, definition):
    """
    Returns the handler instance of the given definition

    :param definition: The definition
    :type definition: AttributeDefinition

    :returns: Instance extending HandlerBase
    """
    # GethandlerClass
    handlerName = self.getHandlerName(definition.handlerIndex)
    temp = handlerName.rsplit('.', 1)
    module = import_module('.' + temp[0], 'ce1sus.web.helpers.handlers')
    clazz = getattr(module, temp[1])
    # instantiate
    handler = clazz()
    # associate definition to handler
    handler.definition = definition
    # check if handler base is implemented
    if not isinstance(handler, HandlerBase):
      raise HandlerException(('{0} does not implement '
                              + 'HandlerBase').format(handlerName))
    return handler
