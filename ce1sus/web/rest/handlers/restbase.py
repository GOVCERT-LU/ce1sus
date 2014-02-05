# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 5, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController


def create_status(classname=None, message=None):
  result = dict()
  result['response'] = dict()
  result['response']['errors'] = list()
  if (classname is None and message is None):
    result['response']['status'] = 'OK'
  else:
    result['response']['status'] = 'ERROR'
    result['response']['errors'].append({classname: '{0}'.format(message)})
  return result


class RestAPIException(Exception):
  """
  Exception base for handler exceptions
  """
  pass


class RestBaseController(Ce1susBaseController):

  def __init__(self, config):
    Ce1susBaseController.__init__(config)

  def _raise_error(self, error):
    self._destroy_sess
              raise cherrypy.HTTPError(418)