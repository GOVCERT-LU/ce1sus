# -*- coding: utf-8 -*-

"""
module used for connecting to the rt system

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from rtkit.resource import RTResource
from rtkit.authenticators import CookieAuthenticator
from rtkit.errors import RTResourceError


class NoResponseException(Exception):
    """
    No response exception
    """
    pass


# pylint: disable=R0903,R0902
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
        self.last_updated = None
        self.resolved = 'Definitely not resolved'


class RTTickets(object):
    """Container class for RTTickets"""
    def __init__(self, url, usr, pwd):
        self.__url = url
        self.__resource = RTResource(url + 'REST/1.0/',
                                     usr,
                                     pwd,
                                     CookieAuthenticator)

    def get_all_tickets(self):
        """Returns all the tickets"""
        try:
            query = ("Queue%3D'SOC'%20OR%20Queue%3D'Investigations'%20OR%20Queue%3D'"
                     + "Notifications'%20OR%20Queue%3D'Informations'%20OR%20Queue%3D'"
                     + "Sub-Incidents'")
            response = self.__resource.get(path='search/ticket?query=' + query)
            ticket_list = list()
            if len(response.parsed) > 0:
                for text_list in response.parsed:
                    for ticket_id, ticket_title in text_list:
                        ticket = Ticket(ticket_id)
                        ticket.url = (self.__url + '/Ticket/Display.html?id='
                                      + unicode(ticket_id, 'utf-8', errors='replace'))
                        ticket.title = unicode(ticket_title, 'utf-8', errors='replace')
                        ticket_list.append(ticket)
                return ticket_list
            else:
                raise NoResponseException('Nothing found!')
        except RTResourceError as error:
            raise NoResponseException(error)

    def get_ticket_by_id(self, identifier):
        """Returns a ticket with the given identifier"""
        try:
            response = self.__resource.get(path='/ticket/' + identifier + '/show')
            if len(response.parsed) > 0:
                rsp_dict = {}
                for resp in response.parsed:
                    for tick in resp:
                        rsp_dict[tick[0]] = unicode(tick[1], 'utf-8', errors='replace')
                ticket = Ticket(identifier)
                ticket.url = self.__url + '/Ticket/Display.html?id=' + identifier
                ticket.title = unicode(rsp_dict['Subject'], 'utf-8', errors='replace')
                ticket.queue = unicode(rsp_dict['Queue'], 'utf-8', errors='replace')
                ticket.owner = unicode(rsp_dict['Owner'], 'utf-8', errors='replace')
                ticket.creator = unicode(rsp_dict['Creator'],
                                         'utf-8', errors='replace')
                ticket.status = unicode(rsp_dict['Status'], 'utf-8', errors='replace')
                ticket.requestors = unicode(rsp_dict['Requestors'],
                                            'utf-8', errors='replace')
                ticket.created = unicode(rsp_dict['Created'],
                                         'utf-8', errors='replace')
                ticket.last_updated = unicode(rsp_dict['LastUpdated'],
                                              'utf-8', errors='replace')
                # froen mech waat daat mecht?
                if 'Resolved' in rsp_dict:
                    ticket.resolved = rsp_dict['Resolved']
            else:
                raise NoResponseException('Nothing found!')
        except RTResourceError as error:
            raise NoResponseException(error)

    def get_base_ticket_url(self):
        """Returns the base url of RT"""
        return self.__url + '/Ticket/Display.html?id='
