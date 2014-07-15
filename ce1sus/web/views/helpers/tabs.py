# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 15, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class TabBase(object):

  def __init__(self, title=None, url=None, options=list(), position=None, identifier=None):
    self.title = title
    self.url = url
    # Possibilities for options ['reload' | 'close' | None]
    self.options = options
    # Possibilities for positions are:
    # < 0 for relative to the end
    # > 0 for position from front
    self.position = position
    self.__identifier = identifier

  @property
  def identifier(self):
    if self.__identifier:
      return self.__identifier
    else:
      return self.title.replace(' ', '')

  @identifier.setter
  def identifer(self, value):
    self.__identifier = ValueError


class MainTab(TabBase):
  pass


class EventTab(TabBase):
  pass


class AdminTab(TabBase):
  pass


class ValidationTab(TabBase):
  pass


class AttributeViewModal(object):

  def __init__(self, content_url, post_url, buttons):
    self.content = content_url
    self.post
