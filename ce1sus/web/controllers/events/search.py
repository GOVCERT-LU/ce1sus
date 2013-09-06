# -*- coding: utf-8 -*-

"""
module handing the search pages

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.web.controllers.base import BaseController
import cherrypy
from ce1sus.brokers.valuebroker import ValueBroker
from dagr.web.helpers.pagination import Paginator, PaginatorOptions
from ce1sus.brokers.definitionbroker import AttributeDefinition, \
                                            AttributeDefinitionBroker
from importlib import import_module
from ce1sus.web.helpers.protection import require, requireReferer

class ResultItem(object):
  """
  Container Class for displaying the search results
  """
  def __init__(self, identifier, event, objDef, attrDef, attribute, value):
    self.identifier = identifier
    self.event = event
    self.objDef = objDef
    self.attrDef = attrDef
    self.attribute = attribute
    self.value = value

class SearchController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.valueBroker = self.brokerFactory(ValueBroker)
    self.attributeDefinition = AttributeDefinition()
    self.attributeDefinitionBroker = self.brokerFactory(
                                                    AttributeDefinitionBroker)
  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the events page

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/search/index.html')
    cbDefinitions = self.attributeDefinitionBroker.getCBValuesForAll()
    return template.render(cbDefinitions=cbDefinitions)

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def searchResults(self, definitionID, needle):
    """
    Generates the page with the search results

    :param definitionID: The Id of the selected attribute definition
    :type definitionID: Integer
    :param needle: The needle to search for
    :type needle: String
    """
    template = self.mako.getTemplate('/events/search/results.html')

    result = list()
    if needle:
      # GetClass
      definition = self.attributeDefinitionBroker.getByID(definitionID)

      className = definition.className
      module = import_module('.valuebroker', 'ce1sus.brokers')
      clazz = getattr(module, className)


      foundValues = self.valueBroker.lookforValue(clazz, needle)
      # prepare displayItems

      for value in foundValues:
        obj = ResultItem(value.attribute.object.event.identifier,
                         value.attribute.object.event,
                         value.attribute.object.definition,
                         value.attribute.definition,
                         value.attribute, value)
        result.append(obj)


    # Prepare paginator
    labels = [{'event.identifier':'Event #'},
              {'event.title':'Event Name'},
              {'objDef.name':'Object'},
              {'attrDef.name':'Attribute name'},
              {'value.value':'Attribute value'},
              {'event.created':'CreatedOn'}]
    paginatorOptions = PaginatorOptions('/events/recent', 'eventsTabTabContent')
    paginatorOptions.addOption('NEWTAB',
                               'VIEW',
                               '/events/event/view/',
                               contentid='')
    paginator = Paginator(items=result,
                          labelsAndProperty=labels,
                          paginatorOptions=paginatorOptions)
    return template.render(paginator=paginator)
