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


class TestReport(LoggedInBase):

  def __add_event(self):
    try:
      json_dict = self.get_json('events/new.json')
      return_json = self.post('/event', data=json_dict)
      return_json = json.loads(return_json)
      return return_json['identifier']
    except HTTPError as errror:
      assert False

  def testNew(self):
    event_id = self.__add_event()
    try:
      json_dict = self.get_json('reports/new.json')
      return_json = self.post('/event/{0}/report?complete=true'.format(event_id), data=json_dict)
      return_json = json.loads(return_json)
      assert compare_objects(json_dict, return_json, False)
    except HTTPError as error:
      if error.code == 400:
        assert True
      else:
        assert False

  def testExsiting(self):
    event_id = self.__add_event()
    try:
      json_dict = self.get_json('reports/new.json')
      self.post('/event/{0}/report?complete=true'.format(event_id), data=json_dict)
      try:
        self.post('/event/{0}/report?complete=true'.format(event_id), data=json_dict)
      except HTTPError as error:
        if error.code == 400:
          assert True
        else:
          assert False

    except HTTPError as error:
      assert False

  def testUpdate(self):
    event_id = self.__add_event()
    try:
      json_dict = self.get_json('reports/new.json')
      return_json = self.post('/event/{0}/report?complete=true'.format(event_id), data=json_dict)
      return_json = json.loads(return_json)
      try:
        if return_json:
          new_json_dict = self.get_json('reports/update.json')
          result = self.put('/event/{0}/report/{1}?complete=true'.format(event_id, return_json.get('identifier')), data=new_json_dict)
          if result:
            return_json = self.get('/event/{0}/report/{1}?complete=true'.format(event_id, return_json.get('identifier')))
            return_json = json.loads(return_json)
            assert return_json.get('title') == new_json_dict.get('title')

          else:
            assert False

        else:
          assert False
      except HTTPError as error:
        if error.code == 400:
          assert True
        else:
          assert False
      
    except HTTPError as error:
      assert False
