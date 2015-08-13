# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""
from ce1sus.db.classes.internal.event import Comment
from ce1sus.db.common.broker import BrokerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class CommentBroker(BrokerBase):

  def get_broker_class(self):
    return Comment
