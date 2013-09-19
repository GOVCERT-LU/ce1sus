'''
Created on Jul 5, 2013

@author: jhemp
'''
import unittest
from dagr.db.session import SessionManager
from ce1sus.brokers.permissionbroker import GroupBroker
from dagr.helpers.config import ConfigException

# pylint:disable=R0904, C0111, R0201, W0612, W0613
class TestSession(unittest.TestCase):

  def testSetupFound(self):
    try:
      session = SessionManager('../ce1susFoo.cfg')
      session.close()
      assert False
    except:
      assert True

      session = SessionManager('../ce1sus.cfg')
      session.close()
      assert True

      session = SessionManager('../ce1sus.cfg')
      session.brokerFactory(GroupBroker)
      assert True


if __name__ == "__main__":
  # import sys;sys.argv = ['', 'Test.testConfigNotFound']
  unittest.main()
