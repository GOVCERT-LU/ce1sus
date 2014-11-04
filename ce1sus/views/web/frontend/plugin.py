# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 28, 2014
"""
import cherrypy

from ce1sus.helpers.common.config import ConfigSectionNotFoundException
from ce1sus.helpers.common.objects import get_class
from ce1sus.helpers.pluginfunctions import is_plugin_available, get_plugin_function
from ce1sus.plugins.base import PLUGIN_ROOT, PluginException, BasePlugin
from ce1sus.views.web.common.base import BaseView
from ce1sus.views.web.common.common import create_response
from ce1sus.views.web.common.decorators import require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class GuiPlugins(BaseView):

  @require()
  @cherrypy.expose
  @cherrypy.tools.json_out()
  @cherrypy.tools.allow(methods=['GET'])
  def is_plugin_avaibable(self, *vpath, **params):
    try:
      return create_response(is_plugin_available(vpath[0], self.config))
    except PluginException:
      return create_response(False)

  def __get_parameters(self, http_method, **params):
    parameters = None
    if http_method == 'GET':
      parameters = params
    elif http_method == 'POST':
      parameters = cherrypy.request.json
    elif http_method == 'PUT':
      pass
    elif http_method == 'DELETE':
      pass
    else:
      raise PluginException('Method {0} is not defined'.format(http_method))
    if any(parameters):
      return parameters
    else:
      return None

  @require()
  @cherrypy.expose
  @cherrypy.tools.json_in()
  @cherrypy.tools.json_out()
  @cherrypy.tools.allow(methods=['GET', 'PUT', 'POST', 'DELETE'])
  def default(self, *vpath, **params):
    # TODO check if http method is legal
    http_method = cherrypy.request.method
    try:
      method = get_plugin_function(vpath[0], vpath[1], self.config, 'web_plugin')
      return create_response(method(http_method, self.__get_parameters(http_method, **params)))
    except (ImportError, AttributeError, PluginException) as error:
      return self.raise_exception(error)
