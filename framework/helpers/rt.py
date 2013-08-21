
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.helpers.config import Configuration

from rtkit.resource import RTResource
from rtkit.authenticators import CookieAuthenticator
from rtkit.errors import RTResourceError

class NoResponse(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class RTTicket(object):
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




class RTHelper(object):


  def __init__(self, configFile):
    self.__config = Configuration(configFile, 'RTHelper')
    self.__rtUser = self.__config.get('username')
    self.__rtPwd = self.__config.get('password')
    self.__rtUrl = self.__config.get('url')
    self.__resource = RTResource(self.__rtUrl + 'REST/1.0/', self.__rtUser, self.__rtPwd, CookieAuthenticator)
    RTHelper.instance = self

  def getAllTickets(self):
    try:
      query = "Queue='SOC'"
      response = self.__resource.get(path='search/ticket?query=' + query)
      ticketList = list()
      if len(response.parsed) > 0:

        for textList in response.parsed:
          for ticketID, ticketTitle in textList:
            ticket = RTTicket(ticketID)
            ticket.url = self.__rtUrl + 'Ticket/Display.html?id=' + unicode(ticketID, 'utf-8', errors='replace')
            ticket.title = unicode(ticketTitle, 'utf-8', errors='replace')
            ticketList.append(ticket)
        return ticketList
      else:
        raise NoResponse('Nothing found!')
    except RTResourceError as e:
      raise NoResponse(e)

  def getTicketByID(self, identifier):
    try:
      response = self.__resource.get(path='ticket/' + identifier + '/show')

      if len(response.parsed) > 0:
        rsp_dict = {}

        for r in response.parsed:
          for t in r:
            rsp_dict[t[0]] = unicode(t[1], 'utf-8', errors='replace')


        ticket = RTTicket(identifier)
        ticket.url = self.__rtUrl + 'Ticket/Display.html?id=' + identifier
        ticket.title = unicode(rsp_dict['Subject'], 'utf-8', errors='replace')
        ticket.queue = unicode(rsp_dict['Queue'], 'utf-8', errors='replace')
        ticket.owner = unicode(rsp_dict['Owner'], 'utf-8', errors='replace')
        ticket.creator = unicode(rsp_dict['Creator'], 'utf-8', errors='replace')
        ticket.status = unicode(rsp_dict['Status'], 'utf-8', errors='replace')
        ticket.requestors = unicode(rsp_dict['Requestors'], 'utf-8', errors='replace')
        ticket.created = unicode(rsp_dict['Created'], 'utf-8', errors='replace')
        ticket.lastUpdated = unicode(rsp_dict['LastUpdated'], 'utf-8', errors='replace')
        # froen mech waat daat mecht?
        if 'Resolved' in rsp_dict:
          ticket.resolved = rsp_dict['Resolved']
      else:
        raise NoResponse('Nothing found!')
    except RTResourceError as e:
      raise NoResponse(e)


  def getTicketUrl(self):
    return self.__rtUrl + '/Ticket/Display.html?id='

  @staticmethod
  def getInstance():
    """
    Returns the instance if there is one
    """
    if hasattr(RTHelper, 'instance'):
      return RTHelper.instance
