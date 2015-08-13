# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 10, 2015
"""

from ce1sus.helpers.common.config import Configuration
import cherrypy
import code
from inspect import getfile
import json
from os import remove
import os
from os.path import isfile, dirname, abspath
import requests
from requests.sessions import session
import unittest

from ce1sus.common.bootstrap import bootstrap
from ce1sus.common.dbinit import dbinit
from ce1sus.controllers.common.assembler.assembler import Assembler
from ce1sus.db.common.session import SessionManager
from ce1sus.views.web.adapters.ce1susadapter import UnkownMethodException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class HTTPError(Exception):

  def __init__(self, code=None, message=None):
    self.code = code
    self.message = message
    self.reason = None

def get_config():
  basePath = os.path.dirname(os.path.abspath(__file__))
  json_location = basePath + '/../../../scripts/install/database/'
  db_loc = basePath + '/../../../test_ce1sus.sqlite'

  ce1susConfigFile = basePath + '/../../../config/test_ce1sus.conf'

  config = Configuration(ce1susConfigFile)
  config.set('SessionManager', 'db', db_loc)
  return config, (db_loc, json_location)


class BaseTest(unittest.TestCase):

  def controller_factory(self, clazz):
    if self.__db_session is None:
      self.__db_session = self.sm.connector.get_direct_session(True)

    return clazz(self.config, self.__db_session)


  def __extract_message(self, error):
    reason = error.message
    message = error.response.text
    code = error.response.status_code
    # <p>An event with uuid "54f63b0f-0c98-4e74-ab95-60c718689696" already exists</p>
    try:
      pos = message.index('<p>') + 3
      message = message[pos:]
      pos = message.index('</p>')
      message = message[:pos]
    except ValueError:
      # In case the message is not parsable
      pass
    return code, reason, message

  def get_json(self, file_name):
    base = dirname(abspath(getfile(self.__class__)))
    f = open('{0}/{1}'.format(base, file_name), 'r')
    json_txt = f.read()
    f.close()
    return json.loads(json_txt)


  def setUp(self):
    # dbinit
    self.config, (self.db_loc, json_location) = get_config()
    if isfile(self.db_loc):
      remove(self.db_loc)

    dbinit(self.config, json_location=json_location)
    bootstrap(self.config, cherrypy_cfg='/../../config/test_cherrypy.conf')
    cherrypy.engine.start()

    self.apiUrl = 'http://127.0.0.1:8081'
    self.apiUrl = '{0}/REST/0.3.0'.format(self.apiUrl)
    self.apiKey = ''
    self.session = session()

    self.sm = SessionManager(self.config)
    self.__db_session = None
    self.controller_factory(Assembler)


  def tearDown(self):
    cherrypy.engine.exit()
    remove(self.db_loc)

  def post(self, path, clazz=None, data=None, extra_headers=None):
    return self.__request(path, 'POST', clazz, data, extra_headers)

  def put(self, path, clazz=None, data=None, extra_headers=None):
    return self.__request(path, 'PUT', clazz, data, extra_headers)

  def get(self, path, clazz=None, data=None, extra_headers=None):
    return self.__request(path, 'GET', clazz, data, extra_headers)

  def delete(self, path, clazz=None, data=None, extra_headers=None):
    return self.__request(path, 'DELETE', clazz, data, extra_headers)

  def __request(self, path, method, clazz, data=None, extra_headers=None):
    try:
      url = '{0}/{1}'.format(self.apiUrl, path)
      headers = {'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'Ce1sus API test client 0.1',
                 'key': self.apiKey}
      if extra_headers:
        for key, value in extra_headers.items():
          headers[key] = value

      if method == 'GET':
        request = self.session.get(url,
                                   headers=headers,
                                   cookies=self.session.cookies)
      elif method == 'PUT':
        request = self.session.put(url,
                                   json.dumps(data),
                                   headers=headers,
                                   cookies=self.session.cookies)
      elif method == 'DELETE':
        request = self.session.delete(url,
                                      headers=headers,
                                      cookies=self.session.cookies)
      elif method == 'POST':
        request = self.session.post(url,
                                    json.dumps(data),
                                    headers=headers,
                                    cookies=self.session.cookies)
      else:
        raise UnkownMethodException(u'Mehtod {0} is not specified can only be GET,POST,PUT or DELETE')

      if request.status_code == getattr(requests.codes, 'ok'):
        if clazz:
          dictionary = json.loads(request.text)
          if isinstance(dictionary, list):
            result = list()
            for item in dictionary:
              instance = clazz()
              instance.populate(item)
              result.append(instance)
            return result
          else:
            instance = clazz()
            instance.populate(dictionary)
            return instance
        else:
          return request.text
      else:
        try:
          request.raise_for_status()
        except requests.exceptions.HTTPError as error:
          exception = HTTPError()
          code, reason, message = self.__extract_message(error)
          exception.code = code
          exception.reason = reason
          exception.message = message
          raise exception

    except requests.exceptions.RequestException as error:
      raise Exception(error)
    except requests.ConnectionError as error:
      raise Exception('{0}'.format(error.message))

  def set_complete_inflated(self, url, complete=False, inflated=False):
    if complete and not inflated:
      url = '{0}?complete=true'.format(url)
    if not complete and inflated:
      url = '{0}?inflated=true'.format(url)
    if complete and inflated:
      url = '{0}?complete=true&inflated=true'.format(url)
    return url

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
