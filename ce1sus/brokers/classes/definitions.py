
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

# Created on Jul 5, 2013

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from ce1sus.db.session import Base
import ce1sus.helpers.validator as validator


RelationDefinitionsAttributeObject = Table(
    'DObj_has_DAttr', Base.metadata,
    Column('def_attribute_id', Integer, ForeignKey('DEF_Attributes.def_attribute_id')),
    Column('def_object_id', Integer, ForeignKey('DEF_Objects.def_object_id'))
    )

class DEF_Attribute(Base):


  __definitions = {0 : 'TextValue',
                 1 : 'StringValue',
                 2 : 'DateValue',
                 3 : 'NumberValue'}

  __tablename__ = "DEF_Attributes"

  identifier = Column('def_attribute_id', Integer, primary_key=True)
  name = Column('name', String)
  description = Column('description', String)
  regex = Column('regex', String)
  classIndex = Column(Integer)

  # note class relationTable attribute

  objects = relationship('DEF_Object', secondary='DObj_has_DAttr', back_populates='attributes', cascade='all')

  @property
  def className(self):
    if not self.classIndex is None:
      return self.findClassName(self.classIndex)
    else:
      return ''

  def findClassName(self, index):
    """returns the table name"""
    try:
      identifier = int(index)

      if identifier >= 0 and identifier <= len(self.__definitions):
        return self.__definitions[index]
    except Exception:
      pass

    raise Exception('Invalid input "{0}"'.format(index))
    return

  def findTableIndex(self, name):
    """searches for the index for the given table name"""
    for index, tableName in self.__definitions.iteritems():
      if tableName == name:
        return index
    return None

  @staticmethod
  def getTableDefinitions():
    result = dict()
    for index, tableName in DEF_Attribute.__definitions.iteritems():
      key = tableName.replace('Value', '')
      value = index
      result[key] = value
    return result

  def validate(self):
    validator.validateAlNum(self, 'name')
    validator.validateAlNum(self, 'description', True)
    # validator.validateRegex(self, 'regex', "^.*$", "fail", False)
    validator.validateAlpha(self, 'classIndex')
    return validator.isObjectValid(self)

  def addObject(self, obj):
    self.objects.append(obj)

  def removeObject(self, obj):
    self.objects.remove(obj)


class DEF_Object(Base):
  __tablename__ = "DEF_Objects"

  identifier = Column('def_object_id', Integer, primary_key=True)
  name = Column('name', String, nullable=False)
  description = Column('description', String)

  attributes = relationship('DEF_Attribute', secondary='DObj_has_DAttr', back_populates='objects', cascade='all')

  def addAttribute(self, attribute):
    self.attributes.append(attribute)

  def removeAttribute(self, attribute):
    self.attributes.remove(attribute)

  def validate(self):
    validator.validateAlNum(self, 'name')
    validator.validateAlNum(self, 'description', True)
    return validator.isObjectValid(self)
