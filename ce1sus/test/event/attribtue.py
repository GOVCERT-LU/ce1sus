'''
Created on Aug 10, 2015
'''

import json
from inspect import getfile

from ce1sus.test.common.base import HTTPError
from ce1sus.test.common.loggedinbase import LoggedInBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class TestAttribute(LoggedInBase):

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

  def __add_object(self):
    observable_id = self.__add_observable()
    try:
      json_dict = self.get_json('objects/new.json')
      return_json = self.post('/observable/{0}/object'.format(observable_id), data=json_dict)
      return_json = json.loads(return_json)
      return return_json['identifier']
    except HTTPError:
      assert False

  def testNewGenericHandler(self):
    object_id = self.__add_object()
    try:
      json_dict = self.get_json('attributes/new.json')
      return_json = self.post('attributes{0}/attribute?complete=true'.format(object_id), data=json_dict)
      return_json = json.loads(return_json)
      assert True
    except HTTPError as error:
      if error.code == 400:
        assert True
      else:
        assert False

  def testNewMultiHandler(self):
    pass

  def testNewFileHandler(self):
    pass

  def testNewEmailHandler(self):
    pass

  def testUpdate(self):
    pass

  def testExisting(self):
    pass

