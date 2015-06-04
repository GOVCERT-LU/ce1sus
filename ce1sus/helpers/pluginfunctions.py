# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 30, 2014
"""
from ce1sus.helpers.common.config import ConfigSectionNotFoundException
from ce1sus.helpers.common.objects import get_class
from ce1sus.plugins.base import PLUGIN_ROOT, PluginException, BasePlugin


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def __get_module_classname(name):
  module = u'{0}.{1}plugin'.format(PLUGIN_ROOT, name)
  classname = u'{0}Plugin'.format(name.title())
  return module, classname


def is_plugin_available(name, config):
  module, classname = __get_module_classname(name)
  try:
        # first check if enabled
    plugin_config = config.get_section('Plugins')
    if plugin_config.get(classname.lower(), False):
            # else check if instanciable
      get_class(module, classname)
      return True
    else:
      return False
  except (ImportError, ConfigSectionNotFoundException, PluginException) as error:
    raise PluginException(error)


def get_plugin_function(name, method_name, config, type_):
  module, classname = __get_module_classname(name)
  try:
    clazz = get_class(module, classname)
    instance = clazz(config)
    if isinstance(instance, BasePlugin):
      method = getattr(instance, method_name)
      if hasattr(method, type_):
        return method

      else:
        raise PluginException('Method {0}.{1} is not defined as to be called from web applications'.format(classname, method_name))
    else:
      raise PluginException('Class {0} does not implement BasePlugin'.format(classname))
  except (ImportError, AttributeError) as error:
    raise PluginException(error)
