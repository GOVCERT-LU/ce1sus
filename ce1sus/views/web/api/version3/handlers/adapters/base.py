# -*- coding: utf-8 -*-

"""
(Description)

Created on 7 Sep 2015
"""

from ce1sus.helpers.common.config import Configuration, ConfigSectionNotFoundException
from datetime import datetime
from os import makedirs, remove
from os.path import dirname, abspath, isdir, isfile

from ce1sus.controllers.admin.group import GroupController
from ce1sus.controllers.base import ControllerException
from ce1sus.controllers.common.merger.merger import Merger
from ce1sus.handlers.base import HandlerException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class AdapterHandlerException(HandlerException):
  pass


class AdapterHandlerBase(RestBaseHandler):

  def __init__(self, config):
    super(AdapterHandlerBase, self).__init__(config)
    self.merger = Merger(config)
    try:
      basePath = dirname(abspath(__file__))
      self.adapter_config = Configuration(basePath + '/../../../../../../../config/mappers.conf')
    except ConfigSectionNotFoundException as error:
      raise ControllerException(error)
    self.group_controller = GroupController(config)
    self.dump_location = None


  def __get_dump_path(self):
    sub_path = '{0}/{1}/{2}'.format(datetime.now().year,
                                    datetime.now().month,
                                    datetime.now().day)
    if self.dump_location:
      path = '{0}/{1}/{2}'.format(self.dump_location, sub_path, self.dump_location)
      if not isdir(path):
        makedirs(path)
      return path
    else:
      message = 'Dumping of files was activated but no file location was specified'
      self.logger.error(message)
      raise HandlerException(message)

  def dump_file(self, filename, data):
    path = self.__get_dump_path()
    full_path = '{0}/{1}'.format(path, filename)
    if isfile(full_path):
      remove(full_path)
    f = open(full_path, 'w+')
    f.write(data)
    f.close()
