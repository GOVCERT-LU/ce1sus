'''
Created on Aug 10, 2015
'''

from ce1sus.helpers.common.objects import compare_objects
import json

from ce1sus.test.common.base import HTTPError
from ce1sus.test.common.loggedinbase import LoggedInBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class TestAdminAttributes(LoggedInBase):
  


  def testExsiting(self):
    try:
      json_dict = self.get_json('attribtues/existing.json')
      return_json = self.request('attributedefinition', 'POST', None, json_dict)
      return_json = json.loads(return_json)
      assert compare_objects(json_dict, return_json, False)
    except HTTPError as error:
      if error.code == 400:
        assert True
      else:
        assert False

  def testNew(self):
    try:
      json_dict = self.get_json('attribtues/new.json')
      return_json = self.request('attributedefinition', 'POST', None, json_dict)
      return_json = json.loads(return_json)
      if return_json.get('cybox_std'):
        assert False
      else:
        assert True
    except HTTPError as error:
      if error.code == 400:
        assert True
      else:
        assert False

  """
  requests send post instead of delete
  def testRemoveNonCybox(self):
    try:
      json_dict = self.get_json('attribtues/new.json')
      return_json = self.request('attributedefinition', 'POST', None, json_dict)

      self.request('attributedefinition/{0}'.format(return_json.get('identifier')), 'DELETE', None, None)

      assert True
    except HTTPError:
      assert False

  def testRemoveCybox(self):
    try:
      self.request('attributedefinition/dfa5b0ed-9048-40cc-9e8f-e5000db655b3', 'DELETE', None, None)
      assert False
    except HTTPError  as error:
      if error.code == 400:
        assert True
      else:
        assert False
  """
