# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 30, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.views.base import Ce1susBaseView
from ce1sus.controllers.events.search import SearchController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.helpers.strings import InputException
from dagr.controllers.base import ControllerException


class SearchView(Ce1susBaseView):
  """
  View handler for searches
  """

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.search_controller = SearchController(config)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def index(self):
    """
    renders the events page

    :returns: generated HTML
    """
    cb_definitions = self.search_controller.get_cb_def_values_for_all()
    cb_definitions['Any'] = 'Any'
    return self._render_template('/events/search/index.html', cb_definitions=cb_definitions)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def search_results(self, definition_id, needle, operant):
    """
    Generates the page with the search results

    :param definitionID: The Id of the selected attribute definition
    :type definitionID: Integer
    :param needle: The needle to search for
    :type needle: String
    """
    try:
      user = self._get_user()
      cache = self._get_authorized_events_cache()
      results = self.search_controller.search_results(needle, definition_id, operant, user, cache)
      # Prepare paginator
      return self._return_ajax_ok() + self._render_template('/events/search/results.html',
                                                              results=results
                                                              )
    except (InputException, ControllerException) as error:
      return '{0}'.format(error)
