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

  def __init__(self, base_url=None, identifier=None):
    self.base_url = base_url
    self.identifier = identifier

  @property
  def url(self):
    if self.identifier:
      url = '{0}/{1}'.format(self.base_url, self.identifier)
    else:
      url = self.base_url
    return url
