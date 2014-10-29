# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
import cherrypy

from ce1sus.helpers.common.objects import get_methods
from ce1sus.views.web.api.version3.handlers.loginhandler import LoginHandler, LogoutHandler
from ce1sus.views.web.api.version3.handlers.misc import VersionHandler
from ce1sus.views.web.common.base import BaseView
from ce1sus.views.web.common.decorators import SESSION_KEY


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class RestController(BaseView):

  def __init__(self, config):
    BaseView.__init__(self, config)
    self.instances = dict()
    # add instances known to rest
    self.instances['login'] = LoginHandler(config)
    self.instances['logout'] = LogoutHandler(config)
    self.instances['version'] = VersionHandler(config)

  @staticmethod
  def find_default_method_name(instance):
    methods = get_methods(instance)
    for method in methods:
      function = getattr(instance, method)
      if hasattr(function, 'default_fct'):
        return method
    return None

  def __check_requirements(self, conditions):
    # requested_address = urllib.quote(cherrypy.request.request_line.split()[1])
    if conditions is not None:
      session = getattr(cherrypy, 'session')
      username = session.get(SESSION_KEY, None)
      if username:
        cherrypy.request.login = username
        for condition in conditions:
          # A condition is just a callable that returns true or false
          if not condition():
            # TODO: log why if possible
            raise cherrypy.HTTPError(403, 'No allowed')
        # TODO: redirect the user to the requested url if the url matches!! -> external view of an event
        # raise cherrypy.HTTPRedirect(requested_address)
      else:
        raise cherrypy.HTTPError(403, 'Not authenticated')

  @cherrypy.expose
  @cherrypy.tools.json_in()
  @cherrypy.tools.json_out()
  @cherrypy.tools.allow(methods=['GET', 'PUT', 'POST', 'DELETE'])
  def default(self, *vpath, **params):
    parameters = list()
    handler = None
    # the first element in vpath is the name of the handler to use
    # the remaining elements are the parameters for the handler
    first_element = True
    for node in vpath:
      if first_element:
        handler = node
        first_element = False
      else:
        parameters.append(node)

    if not handler:
      return self.raise_exception(Exception('Root requests are not allowed'))

    # check if parameters are set, when then raise an error as they are not supported
    if params:
      return self.raise_exception(Exception('Parameters are not supported'))

    # get the requested handler
    handler_instance = self.instances.get(handler, None)

    if not handler_instance:
      return self.raise_exception(Exception('Handler "{0}" is not defined'.format(handler)))

    # get default access point of the handler
    method_name = RestController.find_default_method_name(handler_instance)

    if not method_name:
      return self.raise_exception(Exception('Handler {0} has no default method'.format(handler_instance.name)))

    http_method = cherrypy.request.method

    json = {}
    if hasattr(cherrypy.request, 'json'):
      json = cherrypy.request.json

    method = getattr(handler_instance, method_name, None)

    if hasattr(method, 'rest_method'):
      # check if the is a requirement
      if hasattr(method, 'require_auth_flag'):
        conditions = method.require_auth
        self.__check_requirements(conditions)

      # check if http_method is allowed on function
      if hasattr(method, 'allowed_http_methods'):
        if http_method in method.allowed_http_methods:
          result = method(parameters=parameters, json=json)
          # execute method
          return result
        else:
          return self.raise_exception(Exception('Handler {0} \'s fucntion {1} does not support the {2} method'.format(handler_instance.name, method_name, http_method)))
      else:
        return self.raise_exception(Exception('Handler {0} \'s fucntion {1} has no http methods specified'.format(handler_instance.name, method_name)))

    else:
      return self.raise_exception(Exception('Handler {0} \'s fucntion {1} is not a rest function'.format(handler_instance.name, method_name)))
