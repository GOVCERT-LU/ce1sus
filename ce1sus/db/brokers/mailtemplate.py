# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 21, 2014
"""


from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from ce1sus.db.classes.internal.backend.mailtemplate import MailTemplate
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, TooManyResultsFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MailTemplateBroker(BrokerBase):
  """
  Mail template broker
  """
  ACTIVATION = 'Activation'
  EVENT_PUBLICATION = 'Publication'
  EVENT_UPDATE = 'Update'
  PROPOSAL = 'Proposal'

  def get_broker_class(self):
    return MailTemplate

  def __get_template(self, identifier):
    """
    Returns the object by the given identifier

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :returns: MailTemplate
    """
    try:
      result = self.session.query(MailTemplate).filter(MailTemplate.name == identifier).one()
    except NoResultFound:
      raise NothingFoundException(u'Nothing found for function_id :{0}'.format(identifier))
    except MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for function_id :{0}'.format(identifier))
    except SQLAlchemyError as error:
      raise BrokerException(error)

    return result

  def get_activation_template(self):
    """Returns the template for the activation of users"""
    return self.__get_template(MailTemplateBroker.ACTIVATION)

  def get_publication_template(self):
    return self.__get_template(MailTemplateBroker.EVENT_PUBLICATION)

  def get_proposal_template(self):
    return self.__get_template(MailTemplateBroker.PROPOSAL)

  def get_update_template(self):
    return self.__get_template(MailTemplateBroker.EVENT_UPDATE)
