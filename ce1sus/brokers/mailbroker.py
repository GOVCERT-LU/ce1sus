# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 21, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.session import BASE
from sqlalchemy import Column, Integer, String
from dagr.db.broker import BrokerBase, NothingFoundException, TooManyResultsFoundException, BrokerException
import sqlalchemy.orm.exc
from dagr.helpers.validator.objectvalidator import ObjectValidator


# pylint: disable = R0903,W0232
class MailTemplate(BASE):
  """This is a container class for the Mails table."""

  __tablename__ = "Mails"
  identifier = Column('mail_id', Integer, primary_key=True)
  name = Column('name', String)
  description = Column('description', String)
  body = Column('body', String)
  subject = Column('subject', String)
  function_id = Column('function_id', Integer)

  def validate(self):
    """Validates the mail template object"""
    ObjectValidator.validateAlNum(self, 'name', withSpaces=True, minLength=3,
                                  withSymbols=True)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  withNonPrintableCharacters=True,
                                  withSpaces=True,
                                  minLength=3,
                                  withSymbols=True)
    ObjectValidator.validateAlNum(self,
                                  'body',
                                  withNonPrintableCharacters=True,
                                  withSpaces=True,
                                  minLength=3,
                                  withSymbols=True)
    ObjectValidator.validateAlNum(self, 'subject', withSpaces=True, minLength=3,
                                  withSymbols=True)
    return ObjectValidator.isObjectValid(self)


class MailTemplateBroker(BrokerBase):
  """
  Mail template broker
  """
  ACTIVATION = 1
  EVENT_PUBLICATION = 2
  EVENT_UPDATE = 3
  PROPOSAL = 4

  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    return MailTemplate

  def __get_template(self, identifier):
    """
    Returns the object by the given identifier

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :returns: MailTemplate
    """
    try:

      result = self.session.query(MailTemplate).filter(
                        MailTemplate.function_id == identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found for function_id :{0}'.format(
                                                                  identifier))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for function_id :{0}'.format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

    return result

  def get_activation_template(self):
    """Returns the template for the activation of users"""
    return self.__get_template(MailTemplateBroker.ACTIVATION)

  def get_publication_template(self):
    return self.__get_template(MailTemplateBroker.EVENT_PUBLICATION)

  def get_notifcation_template(self):
    return self.__get_template(MailTemplateBroker.PROPOSAL)

  def get_update_template(self):
    return self.__get_template(MailTemplateBroker.EVENT_UPDATE)
