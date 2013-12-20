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

