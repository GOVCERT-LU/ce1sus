# -*- coding: utf-8 -*-

"""
(Description)

Created on 15 Sep 2015
"""
import cherrypy

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.views.web.api.version3.handlers.adapters.base import AdapterHandlerBase
from ce1sus.views.web.api.version3.handlers.restbase import rest_method, methods, RestHandlerNotFoundException, RestHandlerException, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class Ce1susHandler(AdapterHandlerBase):

  def __init__(self, config):
    super(Ce1susHandler, self).__init__(config)

  @rest_method()
  @methods(allowed=['GET'])
  @require()
  def event(self, **args):
    try:
      cache_object = self.get_cache_object(args)
      method = args.get('method', None)
      path = args.get('path')
      requested_object = self.parse_path(path, method)
      event_id = requested_object.get('event_id', None)
      parameters = args.get('parameters')
      if event_id:
        make_file = parameters.get('file', None)
        if make_file == '':
          cherrypy.response.headers['Content-Type'] = 'application/x-download'
          cherrypy.response.headers["Content-Disposition"] = 'attachment; filename=Event_{0}_ce1sus.json'.format(event_id)

        event = self.event_controller.get_event_by_uuid(event_id)
        self.is_instance_viewable(event, cache_object)
        self.set_event_properties_cache_object(cache_object, event)
        return event.to_dict(cache_object)

      else:
        raise RestHandlerException('Cannot be called witout a valid uuid')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
