# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""
from ce1sus.controllers.base import BaseController
from ce1sus.controllers.common.assembler.assembler import Assembler
from ce1sus.controllers.common.merger.merger import Merger


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class Updater(BaseController):

  def __init__(self, config, session=None):
    super(Updater, self).__init__(config, session)
    self.assembler = Assembler(config, session)
    self.merger = Merger(config, session)

  def update(self, instance, json, cache_object):
    cache_object.insert = False
    classname = instance.get_classname()
    self.logger.debug('Updating {0}'.format(classname))

    new_instance = self.assembler.assemble(json, instance.__class__, None, cache_object)
    version = self.merger.merge(instance, new_instance, cache_object)
    return version
