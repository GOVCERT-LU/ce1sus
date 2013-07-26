from sqlalchemy.sql.expression import or_
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

# Created on Jul 5, 2013

from ce1sus.db.broker import BrokerBase
from ce1sus.brokers.classes.definitions import DEF_Attribute, DEF_Object, \
  RelationDefinitionsAttributeObject
import sqlalchemy.orm.exc
from ce1sus.db.dbexceptions import NothingFoundException

class DEF_AttributeBroker(BrokerBase):

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return DEF_Attribute

  def getObjectsByAttribute(self, identifier, belongIn=True):
    try:
      if belongIn:
        attribute = self.getByID(identifier)
        return attribute.attributes
        pass
      else:
        result = self.session.query(DEF_Object).outerjoin(RelationDefinitionsAttributeObject, DEF_Attribute).filter(or_(DEF_Attribute.identifier != identifier, DEF_Attribute.identifier == None)).all()
    except sqlalchemy.orm.exc.NoResultFound:
      result = list()
    return result

  def getCBValues(self):
    definitions = self.getAll()
    result = dict()
    for definition in definitions:
      result[definition.name] = definition.identifier
    return result

  def addObjectToAttribute(self, objID, attrID):
    try:
      obj = self.session.query(DEF_Object).filter(DEF_Object.identifier == objID).one()
      attribute = self.session.query(DEF_Attribute).filter(DEF_Attribute.identifier == attrID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    attribute.addObject(obj)
    self.session.commit()

  def removeObjectFromAttribute(self, objID, attrID):
    try:
      obj = self.session.query(DEF_Object).filter(DEF_Object.identifier == objID).one()
      attribute = self.session.query(DEF_Attribute).filter(DEF_Attribute.identifier == attrID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    attribute.removeObject(obj)
    self.session.commit()


class DEF_ObjectBroker(BrokerBase):

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return DEF_Object

  def getAttributesByObject(self, identifier, belongIn=True):
    try:
      if belongIn:
        obj = self.getByID(identifier)
        return obj.attributes
        pass
      else:
        result = self.session.query(DEF_Attribute).outerjoin(RelationDefinitionsAttributeObject, DEF_Object).filter(or_(DEF_Object.identifier != identifier, DEF_Object.identifier == None)).all()
    except sqlalchemy.orm.exc.NoResultFound:
      result = list()
    return result

  def getCBValues(self):
    definitions = self.getAll()
    result = dict()
    for definition in definitions:
      result[definition.name] = definition.identifier
    return result

  def addAttributeToObject(self, attrID, objID):
    try:
      obj = self.session.query(DEF_Object).filter(DEF_Object.identifier == objID).one()
      attribute = self.session.query(DEF_Attribute).filter(DEF_Attribute.identifier == attrID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    obj.addAttribute(attribute)
    self.session.commit()

  def removeAttributeFromObject(self, attrID, objID):
    try:
      obj = self.session.query(DEF_Object).filter(DEF_Object.identifier == objID).one()
      attribute = self.session.query(DEF_Attribute).filter(DEF_Attribute.identifier == attrID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    obj.removeAttribute(attribute)
    self.session.commit()


