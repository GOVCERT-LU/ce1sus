# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
from abc import ABCMeta, abstractmethod
from ce1sus.helpers.common.objects import get_methods
import cherrypy
from cherrypy.lib import file_generator
from json import dumps
from uuid import UUID

from ce1sus.views.web.api.version3.handlers.restbase import RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.base import BaseView
from ce1sus.views.web.common.decorators import SESSION_KEY


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AbstractRestController(BaseView):
  __metaclass__ = ABCMeta


  def __init__(self, config):
    super(AbstractRestController, self).__init__(config)
    self.instances = dict()
    self.catch_errors = self.config.get('ce1sus', 'catcherrors', False)
    # add instances known to rest and their first URL
    self.set_instances(config)

  @abstractmethod
  def set_instances(self, config):
    raise RestHandlerException('Instances are not defined')

  @staticmethod
  def find_default_method_name(instance, probable_name=None):
    # TODO: find why this is not always working?
    if probable_name:
      if hasattr(instance, probable_name):
                # try deducting from the first call
        function = getattr(instance, probable_name)
        if hasattr(function, 'default_fct'):
          return probable_name

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
  @cherrypy.tools.allow(methods=['GET', 'PUT', 'POST', 'DELETE'])
  def default(self, *vpath, **params):
    path = list()
    handler = None
    # the first element in vpath is the name of the handler to use
    # the remaining elements are the parameters for the handler
    first_element = True
    for node in vpath:
      if first_element:
        handler = node
        first_element = False
      else:
        path.append(node)

    if not handler:
      raise cherrypy.HTTPError(status=405, message='Root requests are not allowed')

    # get the requested handler
    handler_instance = self.instances.get(handler, None)

    if not handler_instance:
      raise cherrypy.HTTPError(status=404, message='Handler "{0}" is not defined'.format(handler))

    default_method = True
    if len(path) > 0:
      uuid_string = path[0]
      # check if it is a uuid
      try:
        UUID(uuid_string, version=4)
      except ValueError:
        # it is not a uuid therefore it must be a method name
        method_name = path.pop(0)
        default_method = False

    if default_method:
      # get default access point of the handler
      method_name = AbstractRestController.find_default_method_name(handler_instance, handler)

    if not method_name:
      raise RestHandlerException('Handler {0} has no default method'.format(handler_instance.name))

    http_method = cherrypy.request.method

    json = self.get_json()

    method = getattr(handler_instance, method_name, None)

    if hasattr(method, 'rest_method'):
      # check if the is has requriements
      if hasattr(method, 'require_auth_flag'):
        conditions = method.require_auth
        self.__check_requirements(conditions)

      # check if http_method is allowed on function
      if hasattr(method, 'allowed_http_methods'):
        if http_method in method.allowed_http_methods:
          try:
            headers = cherrypy.request.headers
            result = method(path=path, json=json, method=http_method, headers=headers, parameters=params)
            # execute method
            # set the correct headers
            cherrypy.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
            if isinstance(result, file_generator):
              return result
            else:
              return dumps(result)
          except RestHandlerException as error:
            message = u'{0}'.format(error.message)
            self.logger.error(message)
            if isinstance(error, RestHandlerNotFoundException):
              raise cherrypy.HTTPError(status=404, message=message)
            raise cherrypy.HTTPError(status=400, message=message)
        else:
          message = u'Handler {0} \'s fucntion {1} does not support the {2} method'.format(handler_instance.name, method_name, http_method)
          self.logger.error(message)
          raise cherrypy.HTTPError(status=405, message=message)
      else:
        message = u'Handler {0} \'s fucntion {1} has no http methods specified'.format(handler_instance.name, method_name)
        self.logger.error(message)
        raise cherrypy.HTTPError(status=418, message=message)

    else:
      message = u'Handler {0} does not provide a function {1}'.format(handler_instance.name, method_name)
      self.logger.error(message)
      raise cherrypy.HTTPError(status=417, message=message)
  default._cp_config = {'methods_with_bodies': ("POST", "PUT", "DELETE")}
