'''
Created on Jul 5, 2013

@author: jhemp
'''
import unittest
from dagr.db.session import SessionManager
from ce1sus.brokers.permissionbroker import GroupBroker
from dagr.helpers.config import ConfigException


class TestSession(unittest.TestCase):


    def testConfigNotFound(self):
      try:
        session = SessionManager('../ce1susFoo.cfg')
        session.close()
        assert False
      except ConfigException:
        assert True

    def testConfigLoaded(self):
      session = SessionManager('../ce1sus.cfg')
      session.close()
      assert True

    def testInitBroker(self):
      session = SessionManager('../ce1sus.cfg')
      session.brokerFactory(GroupBroker)
      assert True


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testConfigNotFound']
    unittest.main()
