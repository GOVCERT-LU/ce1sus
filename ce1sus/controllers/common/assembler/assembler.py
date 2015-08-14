# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 18, 2015
"""
from inspect import getargspec

from ce1sus.controllers.common.assembler.assemble.ccybox.ccybox import CyboxAssembler
from ce1sus.controllers.common.assembler.assemble.cstix import StixAssembler
from ce1sus.controllers.common.assembler.assemble.internal.event import EventAssembler
from ce1sus.controllers.common.assembler.assemble.internal.internal import Ce1susAssembler
from ce1sus.controllers.common.basecontroller import BaseChangeController, BaseChangeControllerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Assembler(BaseChangeController):

  def __init__(self, config, session=None):
    super(Assembler, self).__init__(config, session)
    self.mergers = [StixAssembler(config, session), CyboxAssembler(config, session), Ce1susAssembler(config, session), EventAssembler(config, session)]

  def assemble(self, json, clazz, parent, cache_object):

    cache_object.insert = True

    classname = clazz.get_classname()

    self.logger.debug('Assembling {0}'.format(classname))

    fctname = 'assemble_{0}'.format(self.get_fct_name(classname))
    for merger in self.mergers:
      if hasattr(merger, fctname):
        fct = getattr(merger, fctname)
        params = getargspec(fct)
        params_count = len(params.args)
        if params_count == 3:
          return fct(json, cache_object)
        elif params_count == 4:
          return fct(parent, json, cache_object)
    raise BaseChangeControllerException('Assembling for class {0} is not defined function {1} is missing'.format(classname, fctname))


