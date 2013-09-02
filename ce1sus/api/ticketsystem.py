# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for accessing a ticketing system.

Created on Aug 28, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from abc import abstractmethod

class Ticket(object):
  """
  Ticket container class.
  """
  def __init__(self, identifier):
    self.identifier = identifier
    self.title = None
    self.url = None
    self.queue = None
    self.owner = None
    self.creator = None
    self.status = None
    self.requestors = None
    self.created = None
    self.lastUpdated = None
    self.resolved = 'Definitely not resolved'

class TicketingException(Exception):
  """
  Base exception for the ticketing api
  """
  def __init__(self, message):
    Exception.__init__(self, message)

class NoResponseException(TicketingException):
  """
  No response exception
  """
  def __init__(self, message):
    TicketingException.__init__(self, message)

class NoInstanceFoundException(TicketingException):
  """
  No instance exception
  """
  def __init__(self, message):
    TicketingException.__init__(self, message)

class NotImplementedException(TicketingException):
  """
  Not implemented exception
  """
  def __init__(self, message):
    TicketingException.__init__(self, message)

class TicketSystemBase(object):
  """
  API for accessing the ticketing system.
  """

  instance = None

  def __init__(self):
    TicketSystemBase.instance = self

  @abstractmethod
  def getAllTickets(self):
    """
    Return all the tickets

    :returns: List of tickets
    """
    raise NotImplementedException(('{0}.getAllTickets'
                                   + ' is not implemented').format(
                                                     self.__class__.__name__))

  @abstractmethod
  def getTicketByID(self, identifier):
    """
    Returns a Ticket with the given ID

    :returns: Ticket
    """

    raise NotImplementedException(('{0}.getTicketByID({1})'
                                   + ' is not implemented').format(
                                                     self.__class__.__name__),
                                                     identifier)

  @abstractmethod
  def getBaseTicketUrl(self):
    """
    Returns the base url for accessing a single ticket.

    I.e: http://localhost:81/rt/Ticket/Display.html?id=

    :returns: String
    """
    raise NotImplementedException(('{0}.getBaseTicketUrl'
                                   + ' is not implemented').format(
                                                     self.__class__.__name__))

  @classmethod
  def getInstance(cls):
    """
    Returns the instance if there is one

    :returns: instance extending TicketSystem
    """
    if TicketSystemBase.instance is None:
      raise NoInstanceFoundException('No instance found to provide')
    else:
      return TicketSystemBase.instance
