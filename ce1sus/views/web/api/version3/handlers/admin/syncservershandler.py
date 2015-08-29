# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 2, 2015
"""
from ce1sus.controllers.admin.syncserver import SyncServerController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.db.classes.internal.backend.servers import SyncServer
from ce1sus.views.web.adapters.ce1susadapter import Ce1susAdapter, Ce1susAdapterException
from ce1sus.views.web.adapters.misp.misp import MISPAdapter, MISPAdapterException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.decorators import privileged


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SyncServerHandler(RestBaseHandler):

  def __init__(self, config):
    super(SyncServerHandler, self).__init__(config)
    self.sync_server_controller = self.controller_factory(SyncServerController)

    self.ce1sus_adapter = Ce1susAdapter(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'POST', 'PUT', 'DELETE'])
  @require(privileged())
  def syncservers(self, **args):
    method = args.get('method')
    path = args.get('path')
    json = args.get('json')
    cache_object = self.get_cache_object(args)
    try:
      if method == 'GET':
        if len(path) > 0:
                    # if there is a uuid as next parameter then return single mail
          uuid = path.pop(0)
          server = self.sync_server_controller.get_server_by_uuid(uuid)
          return server.to_dict(cache_object)
        else:
          servers = self.sync_server_controller.get_all_servers()
          result = list()

          for server in servers:
            result.append(server.to_dict(cache_object))
          return result
      elif method in ['PUT', 'DELETE']:
        if len(path) > 0:
          uuid = path.pop(0)
          server = self.sync_server_controller.get_server_by_uuid(uuid)
          if method == 'PUT':
            # assemble
            self.updater.update(server, json, cache_object)
            self.sync_server_controller.update_server(server, self.get_user())
            return server.to_dict(cache_object)
          else:
            self.sync_server_controller.remove_server(server, self.get_user())
            return 'OK'
        else:
          raise RestHandlerException(u'No id was specified in the json post')
      elif method == 'POST':
        # assemble
        server = self.assembler.assemble(json, SyncServer, None, cache_object)
        self.sync_server_controller.insert_server(server, self.get_user())
        return server.to_dict(cache_object)
      else:
        raise RestHandlerException(u'Unrecoverable error')

    except ControllerException as error:
      raise RestHandlerException(error)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require(privileged())
  def push(self, **args):
    try:
      path = args.get('path')
      if len(path) > 0:
        uuid = path.pop(0)
        server = self.sync_server_controller.get_server_by_uuid(uuid)
        if server.type == 'MISP':
          return self.misp_adapter.push(server)
        elif server.type == 'Ce1sus':
          return self.ce1sus_adapter.push(server)
        else:
          raise RestHandlerException('Not Implemented')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except (MISPAdapterException, ControllerException, Ce1susAdapterException) as error:
      raise RestHandlerException(error)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require(privileged())
  def pull(self, **args):
    try:
      path = args.get('path')
      if len(path) > 0:
        uuid = path.pop(0)
        server = self.sync_server_controller.get_server_by_uuid(uuid)
        if server.type == 'MISP':
          return self.misp_adapter.pull(server)
        elif server.type == 'Ce1sus':
          return self.ce1sus_adapter.pull(server)
        else:
          raise RestHandlerException('Not Implemented')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except (MISPAdapterException, ControllerException, Ce1susAdapterException) as error:
      raise RestHandlerException(error)
