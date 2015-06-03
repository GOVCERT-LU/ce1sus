# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""
import re
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import or_

from ce1sus.db.classes.user import User
from ce1sus.db.common.broker import BrokerBase, ValidationException, BrokerException, NothingFoundException, TooManyResultsFoundException
from ce1sus.helpers.common.hash import hashSHA1


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class UserBroker(BrokerBase):
    """This is the interface between python an the database"""

    def insert(self, instance, commit=True, validate=True):
        """
        overrides BrokerBase.insert
        """
        errors = False
        if validate:
            errors = not instance.validate()
            if errors:
                raise ValidationException(u'User to be inserted is invalid')

        try:
            BrokerBase.insert(self, instance, commit, validate=False)
            self.do_commit(commit)
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def update(self, instance, commit=True):
        """
        overrides BrokerBase.insert
        """

        errors = not instance.validate()
        if errors:
            raise ValidationException(u'User to be updated is invalid')

        if instance.password != 'EXTERNALAUTH':
            # Don't update if the password is already a hash
            if re.match('^[0-9a-f]{40}$', instance.password) is None:
                if not errors:
                    instance.password = hashSHA1(instance.password,
                                                 instance.username)
        try:
            BrokerBase.update(self, instance, commit, validate=False)
            self.do_commit(commit)
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def get_broker_class(self):
        """
        overrides BrokerBase.get_broker_class
        """
        return User

    def getUserByUserName(self, username):
        """
        Returns the user with the following username

        :param user: The username
        :type user: Stirng

        :returns: User
        """
        try:
            user = self.session.query(User).filter(User.username == username).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found with username :{0}'.format(username)
                                        )
        except sqlalchemy.orm.exc.MultipleResultsFound:
            raise TooManyResultsFoundException(u'Too many results found for' +
                                               'ID :{0}'.format(username))
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)
        return user

    def getUserByUsernameAndPassword(self, username, password, salt=None):
        """
        Returns the user with the following username and password

        Note: Password will be hashed inside this function

        :param user: The username
        :type user: Stirng
        :param password: The username
        :type password: Stirng

        :returns: User
        """
        if salt:
            passwd = hashSHA1(password, salt)
            old_pwd = hashSHA1(password + username)
        else:
            passwd = password
            old_pwd = None

        try:
            if old_pwd:
                user = self.session.query(User).filter(User.username == username,
                                                       or_(
                                                           User.password == passwd,
                                                           User.password == old_pwd,
                                                           )
                                                       ).one()
            else:
                user = self.session.query(User).filter(User.username == username, User.password == passwd).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found with ID :{0}'.format(username)
                                        )
        except sqlalchemy.orm.exc.MultipleResultsFound:
            raise TooManyResultsFoundException(u'Too many results found for ID ' +
                                               ':{0}'.format(username))
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)
        return user

    def get_user_by_api_key(self, api_key):
        # check if api key exists
        try:
            result = self.session.query(User).filter(User.api_key == api_key).one()
            return result
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found with apikey :{0}'.format(api_key))
        except sqlalchemy.orm.exc.MultipleResultsFound:
            raise TooManyResultsFoundException('Too many results found for apikey :{0}'.format(api_key))
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise BrokerException(error)

    def get_all(self):
        """
        Returns all get_broker_class() instances

        Note: raises a NothingFoundException or a TooManyResultsFound Exception

        :returns: list of instances
        """
        try:
            result = self.session.query(self.get_broker_class()
                                        ).order_by(User.username.asc()).all()
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found')
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise BrokerException(error)

        return result

    def get_user_by_act_str(self, activation_str):
        try:
            result = self.session.query(User).filter(User.activation_str == activation_str).one()
            return result
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found for activation_str {0}'.format(activation_str))
        except sqlalchemy.orm.exc.MultipleResultsFound:
            raise TooManyResultsFoundException('Too many results found for activation_str :{0}'.format(activation_str))
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise BrokerException(error)

    def get_all_notifiable_users(self):
        try:

            result = self.session.query(User).filter(User.notifications == 1, User.email != None).all()
            return result
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'No notifiable users found')
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise BrokerException(error)
