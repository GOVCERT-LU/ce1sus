# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 21, 2014
"""


from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from ce1sus.db.classes.internal.report import ReferenceDefinition, ReferenceHandler, Reference
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, BrokerException, TooManyResultsFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ReferencesBroker(BrokerBase):

  def get_broker_class(self):
    return Reference

  def get_all_handlers(self):
    try:
      result = self.session.query(ReferenceHandler)
      return result.all()
    except SQLAlchemyError as error:
      raise BrokerException(error)

  def get_handler_by_uuid(self, uuid):
    try:
      result = self.session.query(ReferenceHandler).filter(getattr(ReferenceHandler, 'uuid') == uuid).one()
    except NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(uuid, self.__class__.__name__))
    except MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID :{0}'.format(uuid))
    except SQLAlchemyError as error:
      raise BrokerException(error)

    return result

  def get_handler_by_id(self, identifier):
    try:
      result = self.session.query(ReferenceHandler).filter(getattr(ReferenceHandler, 'identifier') == identifier).one()
    except NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(identifier, self.__class__.__name__))
    except MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID :{0}'.format(identifier))
    except SQLAlchemyError as error:
      raise BrokerException(error)

    return result


class ReferenceDefintionsBroker(BrokerBase):

  def get_broker_class(self):
    return ReferenceDefinition

  def get_defintion_by_chksums(self, chksums):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      definitions = self.session.query(self.get_broker_class()).filter(getattr(self.get_broker_class(), 'chksum').in_(chksums)).all()
      if definitions:
        return definitions
      else:
        return list()
    except NoResultFound:
      raise NothingFoundException(u'No {0} not found for CHKSUMS {1}'.format(self.get_broker_class().__class__.__name__,
                                                                             chksums))
    except SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def get_definition_by_name(self, name):
    try:
      return self.session.query(ReferenceDefinition).filter(ReferenceDefinition.name == name).one()
    except NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(name, self.__class__.__name__))
    except MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID :{0}'.format(name))
    except SQLAlchemyError as error:
      raise BrokerException(error)
