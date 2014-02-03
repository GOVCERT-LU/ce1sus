# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Nov 13, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.web.helpers.protection import require, privileged, require_referer
from dagr.db.broker import BrokerException
from ce1sus.brokers.event.eventbroker import EventBroker
from dagr.web.helpers.pagination import Paginator, PaginatorOptions
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk
from ce1sus.brokers.definition.attributedefinitionbroker import \
                  AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
                  ObjectDefinitionBroker
from dagr.helpers.datumzait import datumzait
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.relationbroker import RelationBroker
from ce1sus.web.controllers.event.event import Relation


class ValidationController(Ce1susBaseController):

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.event_broker = self.broker_factory(EventBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.def_attributes_broker = self.broker_factory(AttributeDefinitionBroker)
    self.def_object_broker = self.broker_factory(ObjectDefinitionBroker)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.relation_broker = self.broker_factory(RelationBroker)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the user page

    :returns: generated HTML
    """
    template = self._get_template('/admin/validation/validationBase.html')

    return self.clean_html_code(template.render())

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def unvalidated(self):
    template = self.mako._get_template('/admin/validation/recent.html')

    labels = [{'identifier':'#'},
              {'title':'Title'},
              {'analysis': 'Analysis'},
              {'risk':'Risk'},
              {'status': 'Status'},
              {'tlp':'TLP'},
              {'modified':'Last modification'},
              {'last_seen':'Last seen'},
              {'creatorGroup.name': 'Created By'}]
    # get only the last 200 events to keep the page small

    lists = self.event_broker.get_all_unvalidated(200, 0)
    paginatorOptions = PaginatorOptions('/admin/validation/unvalidated',
                                        'validationTabsTabContent')
    paginatorOptions.add_option('NEWTAB',
                               'VIEW',
                               '/admin/validation/event/',
                               contentid='',
                               auto_reload=True,
                               tab_title='Event')
    paginator = Paginator(items=lists,
                          labelsAndProperty=labels,
                          paginatorOptions=paginatorOptions)
    paginator.items_per_page = 100
    return self.clean_html_code(template.render(paginator=paginator))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def event(self, event_id):
    """
    renders the base page for displaying events

    :returns: generated HTML
    """
    # right checks

    template = self.mako._get_template('/admin/validation/eventValBase.html')
    return self.clean_html_code(template.render(event_id=event_id))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def eventDetails(self, eventID):
    """
    renders the event page for displaying a single event

    :returns: generated HTML
    """
    template = self.mako._get_template('/admin/validation/eventDetails.html')
    event = self.event_broker.get_by_id(eventID)
    # right checks

    relation_labels = [{'eventID':'Event #'},
                      {'eventName':'Event Name'},
                      {'eventFirstSeen':'First Seen'},
                      {'eventLastSeen':'Last Seen'}]

    relations_paginator_options = PaginatorOptions('/events/recent',
                                                 'validationTabsTabContent')
    relations_paginator_options.add_option('NEWTAB',
                               'VIEW',
                               '/events/event/view/',
                               contentid='',
                               auto_reload=True,
                               tab_title='Event')

    relation_paginator = Paginator(items=list(),
                          labelsAndProperty=relation_labels,
                          paginatorOptions=relations_paginator_options)

    try:
      # get for each object
      # prepare list
      #
      seen_events = list()
      relations = self.relation_broker.get_relations_by_event(event, True, True)
      for event_rel in relations:
        temp = Relation()
        rel_event = event_rel.rel_event
        try:
          temp.eventID = rel_event.identifier
          temp.identifier = rel_event.identifier
          temp.eventName = rel_event.title
          temp.eventFirstSeen = rel_event.first_seen
          temp.eventLastSeen = rel_event.last_seen
          if not temp in relation_paginator.list:
            if temp.eventID not in seen_events:
              relation_paginator.list.append(temp)
              seen_events.append(temp.eventID)
        except cherrypy.HTTPError:
          self._get_logger().debug(('User {0} is not '
                                    + 'authorized').format(self.get_user(True)))

    except BrokerException as error:
      self._get_logger().error(error)

    return self.clean_html_code(template.render(objectList=event.objects,
                           relation_paginator=relation_paginator,
                           event=event,
                           comments=event.comments,
                           cbStatusValues=Status.get_definitions(),
                           cbTLPValues=TLPLevel.get_definitions(),
                           cbAnalysisValues=Analysis.get_definitions(),
                           cbRiskValues=Risk.get_definitions()))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def eventobject(self, eventid, objectid=None):
    """
     renders the file with the base layout of the main object page

    :param objectid: the identifier of the object (only set if the details
                     should be displayed of this object)
    :type objectid: Integer

    :returns: generated HTML
    """
    template = self._get_template('/admin/validation/eventValobjects.html')
    event = self.event_broker.get_by_id(eventid)
    # if event has objects

    labels = [{'identifier':'#'},
              {'sharedIcon':'S'},
              {'key':'Type'},
              {'value':'Value'},
              {'iocIcon': 'IOC'}]
    # mako will append the missing url part
    paginator_options = PaginatorOptions(('/events/event/objects/'
                                         + 'objects/{0}/%(objectid)s/').format(
                                                                      eventid),
                                      'eventTabs{0}TabContent'.format(eventid))
    # mako will append the missing url part
    paginator_options.add_option('MODAL',
                               'VIEW',
                               ('/admin/validation/'
                                + 'view_attribute_details/{0}/%(objectid)s/'
                                ).format(eventid),
                               modal_title='View Attribute')
    # will be associated in the view!!! only to keep it simple!
    paginator = Paginator(items=list(),
                          labelsAndProperty=labels,
                          paginator_options=paginator_options)
    # fill dictionary of attribute definitions but only the needed ones
    paginator.add_td_style('sharedIcon', css='width: 5px;', use_raw_html=True)
    paginator.add_td_style('iocIcon', css='width: 5px;', use_raw_html=True)
    paginator.max_column_length = 90
    try:
      if len(event.objects) > 0:
        for obj in event.objects:
          cb_attribute_defintiions_dict = self.def_attributes_broker.get_cb_values(
                                                    obj.definition.identifier)
      else:
        cb_attribute_defintiions_dict = dict()
    except BrokerException:
      cb_attribute_defintiions_dict = dict()

    objects = event.objects
    if objectid is None:
      try:
        objectid = getattr(cherrypy, 'session')['instertedObject']
        getattr(cherrypy, 'session')['instertedObject'] = None
      except KeyError:
        objectid = None

    return self.clean_html_code(template.render(eventid=eventid,
                        objectList=objects,
                        cbObjDefinitions=self.def_object_broker.get_cb_values(),
                        cb_attribute_defintiions_dict=cb_attribute_defintiions_dict,
                        paginator=paginator,
                        objectid=objectid))

  def __validate_objects(self, objects):
    for obj in objects:
      obj.bit_value.is_validated = True
      # perfom validation of object attribtues
      for attribtue in obj.attributes:
        attribtue.bit_value.is_validated = True
      self.__validate_objects(obj.children)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def validate_event(self, event_id):

    try:
      event = self.event_broker.get_by_id(event_id)
      # perfom validation of event
      event.bit_value.is_validated = True
      # update modifier
      event.modifier = self.get_user()
      event.modifier_id = event.modifier.identifier
      event.modified = datumzait.utcnow()
      event.published = 1
      # check if the event has a group
      if event.creator_group is None:
        # if not add the default group of the validating user
        event.creator_group = self.get_user().default_group

      # perform validation of objects
      self.__validate_objects(event.objects)
      self.event_broker.update(event)
      return self._return_ajax_ok()
    except BrokerException as error:
      return '{0}'.format(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def view_attribute_details(self, eventid, objectid, attributeid):
    """
     renders the file with the requested attribute
    :returns: generated HTML
    """
    # right checks

    template = self._get_template('/events/event/attributes/attributesModal.html'
                                )
    obj = self.object_broker.get_by_id(objectid)
    cb_definitions = self.def_attributes_broker.get_cb_values(
                                                    obj.definition.identifier)
    attribute = self.attribute_broker.get_by_id(attributeid)
    return self.clean_html_code(template.render(eventid=eventid,
                           objectid=objectid,
                           attribute=attribute,
                           cb_definitions=cb_definitions,
                           enabled=False))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def delete_unvalidated_event(self, eventid):
    try:
      self.event_broker.remove_by_id(eventid)
      return self._return_ajax_ok()
    except BrokerException as error:
      return '{0}'.format(error)
