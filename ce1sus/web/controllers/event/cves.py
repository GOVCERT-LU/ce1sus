"""module holding all controllers needed for the event handling"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.web.controllers.base import BaseController
import cherrypy
from framework.web.helpers.pagination import Paginator, PaginatorOptions
from ce1sus.brokers.eventbroker import EventBroker, CVE, CVEBroker
from ce1sus.web.helpers.protection import require
from framework.db.broker import BrokerException
from datetime import datetime

class CVEsController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.cveBroker = self.brokerFactory(CVEBroker)


  @cherrypy.expose
  @require()
  def cves(self, eventID):
    """
    Lists all event cves and cves

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/event/cves/cves.html')
    event = self.eventBroker.getByID(eventID)

    # right checks
    self.checkIfViewable(event.groups, self.getUser().identifier ==
                         event.creator.identifier)


    cveLabels = [{'identifier':'#'},
              {'cve_number':'CVE Number'},
              {'creator.username':'Created by'},
              {'created':'CreatedOn'}]

    paginatorOptions = PaginatorOptions(('/events/event/'
                                         + 'cves/cves/{0}').format(
                                                                      eventID),
                                        'eventTabs{0}TabContent'.format(
                                                                      eventID))
    paginatorOptions.addOption('DIALOG',
                               'REMOVE',
                               ('/events/event/cves/modifyCVE'
                                + '?action=remove&eventID={0}&'
                                + 'cveID=').format(eventID),
                               contentid='',
                               refresh=True)



    cvePaginator = Paginator(items=event.cves,
                          labelsAndProperty=cveLabels,
                          paginatorOptions=paginatorOptions)



    return template.render(eventID=eventID,
                           cvePaginator=cvePaginator,
                           cveUrl=self.getConfigVariable('cveurl'))


  @cherrypy.expose
  @require()
  def modifyCVE(self,
                eventID,
                cveNumber,
                action):
    """
    Processes the modifications of an event
    """
    event = self.eventBroker.getByID(eventID)

    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)
    try:
      if action == 'insert':
        # create and insert tickets
        cve = CVE()
        cve.event_id = eventID
        cve.cve_number = cveNumber
        cve.created = datetime.now()
        cve.creator = self.getUser()
        cve.creator_id = cve.creator.identifier
        self.cveBroker.insert(cve)

      return self.returnAjaxOK()
    except BrokerException as e:
      self.getLogger().critical(e)
      return e


  @cherrypy.expose
  @require()
  def addCVE(self, eventID):
    """
     renders the file for displaying the add an attribute form

    :returns: generated HTML
    """
    template = self.getTemplate('/events/event/cves/cveModal.html')
    return template.render(eventID=eventID,
                           errorMsg=None)



