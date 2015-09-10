# -*- coding: utf-8 -*-

"""
(Description)

Created on 9 Sep 2015
"""
from ce1sus.db.classes.internal.path import Path
from ce1sus.db.common.broker import BrokerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class PathBroker(BrokerBase):

  def get_broker_class(self):
    return Path
