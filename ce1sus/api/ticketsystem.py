'''
Created on Aug 28, 2013

@author: jhemp
'''

from abc import abstractmethod


class Ticket(object):

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
  def __init__(self, message):
    Exception.__init__(self, message)

class NoResponseException(TicketingException):
  def __init__(self, message):
    TicketingException.__init__(self, message)

class NoInstanceFoundException(TicketingException):
  def __init__(self, message):
    TicketingException.__init__(self, message)

class TicketSystemBase(object):
  instance = None

  def __init__(self):
    TicketSystemBase.instance = self

  @abstractmethod
  def getAllTickets(self):
    pass

  @abstractmethod
  def getTicketByID(self, identifier):
    pass

  @abstractmethod
  def getBaseTicketUrl(self):
    pass

  @classmethod
  def getInstance(cls):
    """
    Returns the instance if there is one
    """
    if TicketSystemBase.instance is None:
      raise NoInstanceFoundException('No instance found to provide')
    else:
      return TicketSystemBase.instance
