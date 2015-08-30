# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 26, 2015
"""
import json
from inspect import getfile
from os.path import dirname, abspath
from requests.exceptions import HTTPError

from ce1sus.test.common.loggedinbase import LoggedInBase
from base64 import b64encode


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class TestMisp(LoggedInBase):

  def testNewGenericHandler(self):
    try:
      filename = 'misp.event2847.export.xml'
      base = dirname(abspath(getfile(self.__class__)))
      f = open('{0}/{1}'.format(base, filename), 'r')
      json_txt = f.read()
      f.close()
      json_dict = {'data': b64encode(json_txt), 'name':filename}
      return_json = self.post('/MISP/0.1/upload_xml?complete=true&infated=true', data=json_dict)
      return_json = json.loads(return_json)
      assert True
    except HTTPError as error:
      if error.code == 400:
        assert True
      else:
        assert False
