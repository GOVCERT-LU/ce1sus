# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.rest.handlers.restbase import RestBaseHandler
from dagr.helpers.datumzait import DatumZait
from ce1sus.controllers.events.search import SearchController
from dagr.controllers.base import ControllerException


class RestSearchHandler(RestBaseHandler):

  MAX_LIMIT = 20
  PARAMETER_MAPPER = {'attributes': 'view_attributes',
                      'events': 'view_events'}

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.serach_controller = SearchController(config)

  def __get_limit(self, options):
    limit = options.get('limit', RestSearchHandler.MAX_LIMIT / 2)
    # limit has to be between 0 and maximum value
    if limit < 0 or limit > RestSearchHandler.MAX_LIMIT:
      self._raise_error('InvalidArgument',
                      'The limit value has to be between 0 and 20')
    return limit

  def view_events(self, uuid, **options):
    try:
      # gather required parameters
      start_date = options.get('startdate', None)
      end_date = options.get('enddate', DatumZait.utcnow())
      offset = options.get('page', 0)
      limit = self.__get_limit(options)
      # serach on objecttype
      object_type = options.get('objecttype', None)
      # with the following attribtes type + value
      attributes = options.get('attributes', list())

      # check if the search should be performed on a needle
      user = self._get_user()
      events = self.serach_controller.filtered_search_for_rest(object_type,
                                                               None,
                                                               attributes,
                                                               start_date,
                                                               end_date,
                                                               user,
                                                               self._get_authorized_events_cache(),
                                                               limit,
                                                               offset)
      if not events:
        self._raise_error('NothingFoundException', msg='The search yielded no results.')

      # process events
      result = list()
      for event in events:
        result.append(self.create_rest_obj(event, user, False, False))
      result_dict = {'Results': result}
      return self.create_return_msg(result_dict)

    except ControllerException as error:
      return self._raise_error('ControllerException', error=error)

  def view_attributes(self, uuid, **options):
    try:
      # gather required parameters
      with_definition = options.get('fulldefinitions', False)
      start_date = options.get('startdate', None)
      end_date = options.get('enddate', DatumZait.utcnow())
      offset = options.get('page', 0)
      limit = self.__get_limit(options)
      # serach on objecttype
      object_type = options.get('objecttype', None)
      object_attribtues = options.get('objectattributes', list())
      # with the following attribtes type + value
      attributes = options.get('attributes', list())

      # check if the search should be performed on a needle
      events = self.serach_controller.filtered_search_for_rest(object_type,
                                                               object_attribtues,
                                                               attributes,
                                                               start_date,
                                                               end_date,
                                                               self._get_user(),
                                                               self._get_authorized_events_cache(),
                                                               limit,
                                                               offset)
      if not events:
        self._raise_error('NothingFoundException', msg='The search yielded no results.')

      # process events
      result = list()
      for event in events:
        result.append(self.create_rest_obj(event, self._get_user(), True, with_definition))
      result = {'Results': result}
      return self.create_return_msg(result)

    except ControllerException as error:
      return self._raise_error('ControllerException', error=error)

  # pylint: disable=R0201
  def get_function_name(self, parameter, action):
    if action == 'GET':
      return RestSearchHandler.PARAMETER_MAPPER.get(parameter, None)
    return None
