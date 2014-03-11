# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 20, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'
from dagr.db.broker import BrokerBase, BrokerException, NothingFoundException, TooManyResultsFoundException
from ce1sus.brokers.definition.definitionclasses import AttributeHandler
import sqlalchemy.orm.exc


class AttributeHandlerBroker(BrokerBase):
  """
  Attribute handler broker
  """

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return AttributeHandler

  def get_all_cb_values(self):
    """
    Returns all the values ready for comboboxes
    """
    result = dict()
    definitions = self.get_all()
    for definition in definitions:
      result[definition.classname] = (definition.identifier, definition.description)

    return result

  def get_by_uuid(self, uuid):
    """
    Returns the handler by its uuid
    """
    try:
      return self.session.query(AttributeHandler).filter(AttributeHandler.uuid == uuid).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found with uuid :{0}'.format(
                                                                  uuid))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for uuid :{0}'.format(uuid))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
