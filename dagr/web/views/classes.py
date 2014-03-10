# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 6, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'



class Link(object):
  """Class representing a link"""

  def __init__(self, url_base='', identifier=''):
    self.url_base = url_base
    self.identifier = identifier

  @property
  def url(self):
    if self.identifier:
      url = u'{0}{1}'.format(self.url_base, self.identifier)
    else:
      url = self.url_base
    return url
