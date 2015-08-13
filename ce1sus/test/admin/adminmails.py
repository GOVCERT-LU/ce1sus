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


class TestAdminMailTemplates(LoggedInBase):

  def testNew(self):
    try:
      json_dict = self.get_json('mails/new.json')
      return_json = self.post('/mail', data=json_dict)
      return_json = json.loads(return_json)
      assert False
    except HTTPError as error:
      if error.code == 405:
        assert True
      else:
        assert False

  def testUpdate(self):
    try:
      new_json_dict = self.get_json('mails/update.json')
      result = self.put('/mail/fa6ac2c1-f504-4820-affe-d724f4817af9', data=new_json_dict)
      if result:
        return_json = self.get('/mail/fa6ac2c1-f504-4820-affe-d724f4817af9?complete=true')
        return_json = json.loads(return_json)
        assert return_json.get('subject') == new_json_dict.get('subject')
      else:
        assert False

    except HTTPError as error:
      if error.code == 400:
        assert False
      else:
        assert False
