"""
module containing all informations about attribute values
"""

from framework.db.broker import BrokerBase, ValidationException, \
NothingFoundException, TooManyResultsFoundException, OperationException, \
BrokerException
import sqlalchemy.orm.exc
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from framework.db.session import BASE
from sqlalchemy.types import DateTime
from framework.helpers.validator import ObjectValidator
from os.path import isfile
import os.path as path
import framework.helpers.hash as hasher



class StringValue(BASE):
  """This is a container class for the STRINGVALUES table."""
  def __init__(self):
    pass

  __tablename__ = "StringValues"

  identifier = Column('StringValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateAlNum(self,
                                         'value',
                                         minLength=1,
                                         withSpaces=True,
                                         withSymbols=True)

class FileNotFoundException(BrokerException):
  """Broker Exception"""
  def __init__(self, message):
    BrokerException.__init__(self, message)

class FileValue(BASE):
  """This is a container class for the STRINGVALUES table."""
  def __init__(self):
    pass

  __tablename__ = "FileValues"

  identifier = Column('FileValue_id', Integer, primary_key=True)
  location = Column('location', String)
  md5 = Column('md5', String)
  sha1 = Column('sha1', String)
  sha256 = Column('sha256', String)
  sha384 = Column('sha384', String)
  sha512 = Column('sha512', String)
  name = Column('filename', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def setValuesByFile(self, baseFile):
    """
    Sets the values required for a file
    """
    if not isfile(baseFile):
      # set attributes
      function = getattr(path, 'filename')
      self.name = function(path.basename(baseFile))
      self.md5 = hasher.fileHashMD5(baseFile)
      self.sha1 = hasher.fileHashSHA1(baseFile)
      self.sha256 = hasher.fileHashSHA256(baseFile)
      self.sha384 = hasher.fileHashSHA384(baseFile)
      self.sha512 = hasher.fileHashSHA512(baseFile)
      self.location = baseFile
    else:
      raise FileNotFoundException('Could not find file {0}'.format(baseFile))

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateAlNum(self,
                                         'location',
                                         minLength=3,
                                         withSpaces=True,
                                         withSymbols=True)
    ObjectValidator.validateHash(self, 'sha1', 'SHA1')
    ObjectValidator.validateHash(self, 'sha256', 'SHA256')
    ObjectValidator.validateHash(self, 'sha384', 'SHA384')
    ObjectValidator.validateHash(self, 'sha512', 'SHA512')
    ObjectValidator.validateDigits(self, 'attribute_id')
    return ObjectValidator.isObjectValid(self)

class DateValue(BASE):
  """This is a container class for the DATEVALES table."""
  def __init__(self):
    pass

  __tablename__ = "DateValues"

  identifier = Column('DateValue_id', Integer, primary_key=True)
  value = Column('value', DateTime)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateAlNum(self, 'value')

class TextValue(BASE):
  """This is a container class for the TEXTVALUES table."""
  def __init__(self):
    pass

  __tablename__ = "TextValues"

  identifier = Column('TextValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateAlNum(self,
                                         'value',
                                         minLength=1,
                                         withNonPrintableCharacters=True,
                                         withSpaces=True,
                                         withSymbols=True)

class NumberValue(BASE):
  """This is a container class for the NUMBERVALUES table."""
  def __init__(self):
    pass

  __tablename__ = "NumberValues"
  identifier = Column('NumberValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDigits(self, 'value')



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
    """
    returns the class used for this value broker

    Note: May vary during its lifetime

    """
    return self.__clazz

  @clazz.setter
  def clazz(self, clazz):
    """
    setter for the class
    """
    self.__clazz = clazz

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return self.__clazz

  def __setClassByAttribute(self, attribute):
    """
    sets class for the attribute

    :param attribute: the attribute in context
    :type attribute: Attribute
    """
    className = attribute.definition.className
    self.__clazz = globals()[className]

  def __convertAttriuteValueToValue(self, attribute):
    """
    converts an Attribute to a XXXXXValue object

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns: XXXXXValue
    """
    valueInstance = self.__clazz()
    if isinstance(valueInstance, FileValue):
      # so It is a file then the attribute is a file!
      function = getattr(valueInstance, 'setValuesByFile')
      function(attribute)
    else:
      valueInstance.value = attribute.value
      valueInstance.identifier = attribute.value_id
      valueInstance.attribute_id = attribute.identifier

    return valueInstance

  def getByAttribute(self, attribute):
    """
    fetches one XXXXXValue instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : XXXXXValue
    """

    self.__setClassByAttribute(attribute)

    try:
      result = self.session.query(self.getBrokerClass()).filter(
              self.getBrokerClass().attribute_id == attribute.identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No value found with ID :{0} in {1}'.format(
                                  attribute.identifier, self.getBrokerClass()))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
          'Too many value found for ID :{0} in {1}'.format(attribute.identifier,
           self.getBrokerClass()))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

    return result

  def inserByAttribute(self, attribute, commit=True):
    """
    Inserts one XXXXXValue instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : XXXXXValue
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException('Attribute to be inserted is invalid')

    self.__setClassByAttribute(attribute)
    value = self.__convertAttriuteValueToValue(attribute)



    BrokerBase.insert(self, value, commit)

  def updateByAttribute(self, attribute, commit=True):
    """
    updates one XXXXXValue instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : XXXXXValue
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException('Attribute to be updated is invalid')

    self.__setClassByAttribute(attribute)
    value = self.__convertAttriuteValueToValue(attribute)
    BrokerBase.update(self, value, commit)

  def removeByAttribute(self, attribute, commit):
    """
    Removes one XXXXXValue with the information given by the attribtue

    :param attribute: the attribute in context
    :type attribute: Attribute
    :param commit: do a commit after
    :type commit: Boolean
    """
    self.__setClassByAttribute(attribute)

    try:
      self.session.query(self.getBrokerClass()).filter(
                      self.getBrokerClass().attribute_id == attribute.identifier
                      ).delete(synchronize_session='fetch')
      self.doCommit(commit)
    except sqlalchemy.exc.OperationalError as e:
      self.getLogger().error(e)
      self.session.rollback()
      raise OperationException(e)
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

