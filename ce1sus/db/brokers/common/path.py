# -*- coding: utf-8 -*-

"""
(Description)

Created on 9 Sep 2015
"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from ce1sus.common.utils import instance_code, table_code
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.path import Path
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class PathBroker(BrokerBase):

  def get_broker_class(self):
    return Path
  
  def get_all_elements(self, event):
    try:
      result = self.session.query(Path).filter(Path.path.like('/{0}%'.format(instance_code(event)))).all()
      return result
    except NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(event.identifier, self.__class__.__name__))
    except SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def get_all_attribute_paths(self, event):
    try:
      result = self.session.query(Path).filter(Path.path.like('/{0}%/{1}%'.format(instance_code(event), table_code(Attribute.get_table_name())))).all()
      return result
    except NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(event.identifier, self.__class__.__name__))
    except SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
