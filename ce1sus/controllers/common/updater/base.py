# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 11, 2015
"""
from ce1sus.controllers.common.assembler.assembler import Assembler
from ce1sus.controllers.common.basechanger import BaseChangerException, BaseChanger
from ce1sus.controllers.common.merger.merger import Merger


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class UpdaterException(BaseChangerException):
  pass

class BaseUpdater(BaseChanger):

  def __init__(self, config, session=None):
    super(BaseChanger, self).__init__(config, session)
    self.assember = Assembler(config, session)
    self.merger = Merger(config, session)
