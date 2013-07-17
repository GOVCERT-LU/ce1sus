__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

# Created on Jul 5, 2013

from ce1sus.db.broker import BrokerBase
from ce1sus.brokers.classes.definitions import DEF_Attribute, DEF_Object

class DEF_AttributeBroker(BrokerBase):

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return DEF_Attribute


class DEF_ObjectBroker(BrokerBase):

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return DEF_Object

