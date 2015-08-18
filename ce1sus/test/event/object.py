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


class TestObject(LoggedInBase):
  
  def __add_event(self):
    try:
      json_dict = self.get_json('events/new.json')
      return_json = self.post('/event', data=json_dict)
      return_json = json.loads(return_json)
      return return_json['identifier']
    except HTTPError:
      assert False

  def __add_observable(self):
    event_id = self.__add_event()
    try:
      json_dict = self.get_json('observables/new.json')
      return_json = self.post('/event/{0}/observable'.format(event_id), data=json_dict)
      return_json = json.loads(return_json)
      return return_json['identifier']
    except HTTPError:
      assert False

  def testNew(self):
    observable_id = self.__add_observable()
    try:
      json_dict = self.get_json('objects/new.json')
      return_json = self.post('/observable/{0}/object?complete=true'.format(observable_id), data=json_dict)
      return_json = json.loads(return_json)
      assert True
    except HTTPError as error:
      if error.code == 400:
        assert True
      else:
        assert False

  def testExsiting(self):
    observable_id = self.__add_observable()
    try:
      json_dict = self.get_json('objects/new.json')
      self.post('/observable/{0}/object?complete=true'.format(observable_id), data=json_dict)
      try:
        self.post('/observable/{0}/object?complete=true'.format(observable_id), data=json_dict)
      except HTTPError as error:
        if error.code == 400:
          assert True
        else:
          assert False

    except HTTPError as error:
      assert False

  def testUpdate(self):
    observable_id = self.__add_observable()
    try:
      json_dict = self.get_json('objects/new.json')
      return_json = self.post('/observable/{0}/object?complete=true'.format(observable_id), data=json_dict)
      return_json = json.loads(return_json)
      try:
        if return_json:
          new_json_dict = self.get_json('objects/update.json')
          result = self.put('/observable/{0}/object/{1}?complete=true'.format(observable_id, return_json.get('identifier')), data=new_json_dict)
          if result:
            return_json = self.get('/observable/{0}/object/{1}?complete=true'.format(observable_id, return_json.get('identifier')))
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

  def testRelatedTest(self):
    observable_id = self.__add_observable()
    try:
      json_dict = self.get_json('objects/new.json')
      result_json = self.post('/observable/{0}/object?complete=true'.format(observable_id), data=json_dict)
      result_json = json.loads(result_json)
      try:
        json_dict = self.get_json('objects/new_related.json')
        result_json = self.post('/object/{0}/related_object?complete=true'.format(result_json.get('identifier')), data=json_dict)
        result_json = json.loads(result_json)
        assert True
      except HTTPError:
        assert False

    except HTTPError:
      assert False

  def testComposedTest(self):
    observable_id = self.__add_observable()
    try:
      json_dict = self.get_json('objects/new.json')
      result_json = self.post('/observable/{0}/object?complete=true'.format(observable_id), data=json_dict)
      result_json = json.loads(result_json)
      try:
        json_dict = self.get_json('objects/new_composed.json')
        result_json = self.post('/observable/{0}/object?complete=true'.format(observable_id), data=json_dict)
        result_json = json.loads(result_json)
        assert result_json.get('observable_composition', None) is not None
      except HTTPError:
        assert False

    except HTTPError:
      assert False

  def testNewError(self):
    observable_id = self.__add_observable()
    try:
      json_dict = self.get_json('objects/new_error.json')
      self.post('/observable/{0}/object?complete=true'.format(observable_id), data=json_dict)
      assert False
    except HTTPError as error:
      if error.code == 400:
        json_dict = self.get_json('events/new.json')
        event_id = json_dict['identifier']
        return_json = self.get('/event/{0}?complete=true&inflated=true'.format(event_id))
        return_json = json.loads(return_json)
        if len(return_json.get('errors')) == 1:
          assert True
        else:
          assert False
      else:
        assert False

