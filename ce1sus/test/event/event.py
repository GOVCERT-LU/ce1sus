'''
Created on Aug 10, 2015
'''

import json

from ce1sus.helpers.version import Version
from ce1sus.test.common.base import HTTPError
from ce1sus.test.common.loggedinbase import LoggedInBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class TestEvent(LoggedInBase):

  def testExsiting(self):
    try:
      json_dict = self.get_json('events/existing.json')
      return_json = self.post('/event', data=json_dict)
      try:
        return_json = self.post('/event', data=json_dict)
      except HTTPError as error:
        if error.code == 400:
          assert True
        else:
          assert False
    except HTTPError as error:
      assert False

  def testNew(self):
    try:
      json_dict = self.get_json('events/new.json')
      return_json = self.post('/event', data=json_dict)
      return_json = json.loads(return_json)
      return_json = self.get('/event/{0}?complete=true'.format(return_json.get('identifier')))
      assert True
    except HTTPError as error:
      if error.code == 400:
        assert False
      else:
        assert False

  def testNewUpdate(self):
    try:
      json_dict = self.get_json('events/new.json')
      return_json = self.post('/event', data=json_dict)
      return_json = json.loads(return_json)
      if return_json:
        new_json_dict = self.get_json('events/update.json')
        result = self.put('/event/{0}'.format(return_json.get('identifier')), data=new_json_dict)
        if result:
          return_json = self.get('/event/{0}?complete=true'.format(return_json.get('identifier')))
          return_json = json.loads(return_json)
          assert return_json.get('stix_header').get('title') == new_json_dict.get('stix_header').get('title')
          version1 = Version(json_dict.get('version'))
          version2 = Version(new_json_dict.get('version'))
          assert version1.compare(version2) > 0

        else:
          assert False

      else:
        assert False

    except HTTPError as error:
      if error.code == 400:
        assert False
      else:
        assert False
