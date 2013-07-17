from twisted.test.test_hook import BaseClass
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

# Created on Jul 9, 2013

from ce1sus.db.broker import BrokerBase
from ce1sus.brokers.classes.event import Comment, Object, Attribute, Ticket, \
  Event, StringValue, DateValue, TextValue, NumberValue
import sqlalchemy.orm.exc
from ce1sus.db.dbexceptions import NothingFoundException, TooManyResultsFoundException



class CommentBroker(BrokerBase):

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Comment

class ObjectBroker(BrokerBase):

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Object

class ValueBroker(BrokerBase):
  """
  This broker is used internally to serparate the values to their corresponding tables
  
  Note: Only used by the AttributeBroker
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.__clazz = StringValue

  @property
  def clazz(self):
    return self.__clazz

  @clazz.setter
  def clazz(self, clazz):
    self.__clazz = clazz

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return self.__clazz

  def __setClassByAttribute(self, attribute):
    """
    sets class for the attribute
    
    :param attribute: the attribute incontext
    :type attribute: Attribute
    """
    className = attribute.definition.className
    self.__clazz = globals()[className]

  def __convertAttriuteValueToValue(self, attribute):
    """
    converts an Attribute to a XXXXXValue object
    
    :param attribute: the attribute incontext
    :type attribute: Attribute
    
    :returns: XXXXXValue
    """
    valueInstance = self.__clazz()
    valueInstance.value = attribute.value
    valueInstance.attribute_id = attribute.identifier

    return valueInstance

  def getByAttribute(self, attribute):
    """
    fetches one XXXXXValue instance with the information of the given attribute
    
    :param attribute: the attribute incontext
    :type attribute: Attribute
    
    :returns : XXXXXValue
    """

    self.__setClassByAttribute(attribute)

    try:

      result = self.session.query(self.getBrokerClass()).filter(self.getBrokerClass().attribute_id == attribute.identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No value found with ID :{0} in {1}'.format(attribute.identifier, self.getBrokerClass()))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many value found for ID :{0} in {1}'.format(attribute.identifier, self.getBrokerClass()))

    return result

  def inserByAttribute(self, attribute):
    """
    Inserts one XXXXXValue instance with the information of the given attribute
    
    :param attribute: the attribute incontext
    :type attribute: Attribute
    
    :returns : XXXXXValue
    """
    self.__setClassByAttribute(attribute)
    value = self.__convertAttriuteValueToValue(attribute)
    BrokerBase.insert(self, value)

  def updateByAttribute(self, attribute):
    """
    updates one XXXXXValue instance with the information of the given attribute
    
    :param attribute: the attribute incontext
    :type attribute: Attribute
    
    :returns : XXXXXValue
    """
    self.__setClassByAttribute(attribute)
    value = self.__convertAttriuteValueToValue(attribute)
    BrokerBase.update(self, value)


class AttributeBroker(BrokerBase):
  """
  This broker handles all operations on attribute objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.valueBroker = ValueBroker(session)

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Attribute

  def getSetValues(self, attribute):
    """sets the real values for the given attribute"""

    # execute select for the values
    try:
      value = self.valueBroker.getByAttribute(attribute)
      # value is an object i.e. StringValue and the value of the attribute is the value of the value object
      attribute.value = value.value
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No value found for attribute :{0}'.format(attribute.definition.name))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for attribute :{0}'.format(attribute.definition.name))


  def getByID(self, identifier):
    """
    overrides BrokerBase.getByID
    """
    attribute = BrokerBase.getByID(self, identifier)
    return self.getSetValues(attribute)

  def insert(self, instance):
    """
    overrides BrokerBase.insert
    """
    BrokerBase.insert(self, instance)
    # insert value for value table
    self.valueBroker.inserByAttribute(instance)

  def update(self, instance):
    """
    overrides BrokerBase.update
    """
    BrokerBase.update(self, instance)
    # updates the value of the value table
    self.valueBroker.updateByAttribute(instance)



class TicketBroker(BrokerBase):
  """
  This broker handles all operations on ticket objects
  """
  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Ticket

class EventBroker(BrokerBase):
  """
  This broker handles all operations on event objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.attributeBroker = AttributeBroker(session)

  def getByID(self, identifier):
    """
    overrides BrokerBase.getByID
    """
    event = BrokerBase.getByID(self, identifier)
    for object in event.objects:
      for attribute in object.attributes:
        self.attributeBroker.getSetValues(attribute)
    return event

  def insert(self, instance):
    """
    overrides BrokerBase.insert
    """
    BrokerBase.insert(self, instance)
    # insert value for value table
    for object in instance.objects:
      for attribute in object.attributes:
        self.attributeBroker.insert(attribute)

  def update(self, instance):
    """
    overrides BrokerBase.update
    """
    BrokerBase.update(self, instance)
    # insert value for value table
    for object in instance.objects:
      for attribute in object.attributes:
        self.valueBroker.updateByAttribute(attribute)

  def getBrokerClass(self):
    return Event



