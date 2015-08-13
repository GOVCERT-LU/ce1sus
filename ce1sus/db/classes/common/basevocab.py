# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class BaseVocab(object):

  def __init__(self, instance, attr_name):
    self.instance = instance
    self.attr_name = attr_name

  @property
  def name(self):
    return self.get_dictionary().get(getattr(self.instance, self.attr_name), None)

  @name.setter
  def name(self, name):
    id_ = None
    for key, value in self.get_dictionary().iteritems():
      if value == name:
        id_ = key
        break
    if id_ is None:
      raise ValueError('Value {0} does not exit in {1}'.format(name, self.__class__.__name__))
    else:
      setattr(self.instance, self.attr_name, id_)

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    return self.name
