'''
Created on Aug 10, 2015
'''

import json

from ce1sus.test.common.base import HTTPError
from ce1sus.test.common.loggedinbase import LoggedInBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class TestAdminCondition(LoggedInBase):

  def testExsiting(self):
    try:
      json_dict = self.get_json('conditions/existing.json')
      return_json = self.post('/condition', data=json_dict)
      return_json = json.loads(return_json)
      assert False
    except HTTPError as error:
      if error.code == 400:
        assert True
      else:
        assert False

  def testNew(self):
    try:
      json_dict = self.get_json('conditions/new.json')
      return_json = self.post('/condition', data=json_dict)
      return_json = json.loads(return_json)
      return_json = self.get('/condition/{0}?complete=true'.format(return_json.get('identifier')))
      assert True
    except HTTPError as error:
      if error.code == 400:
        assert False
      else:
        assert False

  def testNewUpdate(self):
    try:
      json_dict = self.get_json('conditions/new.json')
      return_json = self.post('/condition', data=json_dict)
      return_json = json.loads(return_json)
      if return_json:
        new_json_dict = self.get_json('conditions/update.json')
        result = self.put('/condition/{0}'.format(return_json.get('identifier')), data=new_json_dict)
        if result:
          return_json = self.get('/condition/{0}?complete=true'.format(return_json.get('identifier')))
          return_json = json.loads(return_json)
          assert return_json.get('value') == new_json_dict.get('value')
        else:
          assert False

      else:
        assert False

    except HTTPError as error:
      if error.code == 400:
        assert False
      else:
        assert False

  """
  # requests send post instead of delete
  def testRemoveNonCybox(self):
    try:
      json_dict = self.get_json('conditions/new.json')
      return_json = self.post('/condition', data=json_dict)
      return_json = json.loads(return_json)
      self.delete('/condition/{0}'.format(return_json.get('identifier')))

      assert True
    except HTTPError as error:
      if error.code == 400:
        assert True
      else:
        assert False

  def testRemoveCybox(self):
    try:
      self.delete('/condition/6d3bdd28-3f65-49a0-a457-679fed08ea53')
      assert False
    except HTTPError  as error:
      if error.code == 400:
        assert True
      else:
        assert False
  """