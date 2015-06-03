# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import and_, or_

from ce1sus.common.checks import get_max_tlp
from ce1sus.db.classes.common import Analysis, Status, TLP
from ce1sus.db.classes.event import Event, EventGroupPermission
from ce1sus.db.classes.group import Group
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, BrokerException, TooManyResultsFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class EventBroker(BrokerBase):
    """
    This broker handles all operations on event objects
    """
    def __init__(self, session):
        BrokerBase.__init__(self, session)

    def get_broker_class(self):
        """
        overrides BrokerBase.get_broker_class
        """
        return Event

    def get_event_user_permissions(self, event, user):
        group = user.group
        return self.get_event_group_permissions(event, group)

    def get_event_group_permissions(self, event, group):
        try:
            return self.session.query(EventGroupPermission).filter(and_(EventGroupPermission.event_id == event.identifier,
                                                                        EventGroupPermission.group_id == group.identifier
                                                                        )
                                                                   ).one()
        except sqlalchemy.orm.exc.MultipleResultsFound:
            raise TooManyResultsFoundException('Too many results found for this cannot happen')
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException('Group {0} was not associated to event {1}'.format(group.identifier, event.identifier))
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise BrokerException(error)

    def get_all_by_ids(self, ids):
        try:
            return self.session.query(EventGroupPermission).filter(EventGroupPermission.event_id.in_(ids))
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise BrokerException(error)

    def __find_id(self, dictionary, text):
        result = list()
        for key, value in dictionary.iteritems():
            if text.lower() in value.lower():
                result.append(key)

        result.append(key + 1)
        return result

    def __set_parameters(self, result, parameters):
        # add additinal filters

        if parameters:
            anal = parameters.get('filter[analysis]', None)
            if anal:
                matching_ids = self.__find_id(Analysis.get_dictionary(), anal)
                result = result.filter(Event.analysis_id.in_(matching_ids))
            anal = parameters.get('filter[creator_group_name]', None)
            if anal:
                result = result.join(Event.creator_group).filter(Group.name.like('%{0}%'.format(anal)))
            anal = parameters.get('filter[created_at]', None)
            if anal:
                result = result.filter(Event.created_at.like('%{0}%'.format(anal)))
            anal = parameters.get('filter[title]', None)
            if anal:
                result = result.filter(Event.title.like('%{0}%'.format(anal)))
            anal = parameters.get('filter[status]', None)
            if anal:
                matching_ids = self.__find_id(Status.get_dictionary(), anal)
                result = result.filter(Event.status_id.in_(matching_ids))
            anal = parameters.get('filter[tlp]', None)
            if anal:
                matching_ids = self.__find_id(TLP.get_dictionary(), anal)
                result = result.filter(Event.tlp_level_id.in_(matching_ids))

            # do a similar stuff for sorting
            anal = parameters.get('sorting[analysis]', None)
            if anal:
                if anal == 'desc':
                    result = result.order_by(Event.analysis_id.desc())
                else:
                    result = result.order_by(Event.analysis_id.asc())

            anal = parameters.get('sorting[creator_group_name]', None)
            if anal:
                if anal == 'desc':
                    result = result.join(Event.creator_group).order_by(Group.name.desc())
                else:
                    result = result.join(Event.creator_group).order_by(Group.name.asc())

            anal = parameters.get('sorting[created_at]', None)
            if anal:
                if anal == 'desc':
                    result = result.order_by(Event.created_at.desc())
                else:
                    result = result.order_by(Event.created_at.asc())

            anal = parameters.get('sorting[title]', None)
            if anal:
                if anal == 'desc':
                    result = result.order_by(Event.title.desc())
                else:
                    result = result.order_by(Event.title.asc())

            anal = parameters.get('sorting[status]', None)
            if anal:
                if anal == 'desc':
                    result = result.order_by(Event.status_id.desc())
                else:
                    result = result.order_by(Event.status_id.asc())

            anal = parameters.get('sorting[tlp]', None)
            if anal:
                if anal == 'desc':
                    result = result.order_by(Event.tlp_level_id.desc())
                else:
                    result = result.order_by(Event.tlp_level_id.asc())

            anal = parameters.get('sorting[id]', None)
            if anal:
                if anal == 'desc':
                    result = result.order_by(Event.identifier.desc())
                else:
                    result = result.order_by(Event.identifier.asc())
        return result

    def get_all_limited(self, limit, offset, parameters=None):
        """Returns only a subset of entries"""
        try:
            # TODO add validation and published checks
            # result = self.session.query(self.get_broker_class()).filter(Event.dbcode.op('&')(4) == 4).order_by(Event.created_at.desc()).limit(limit).offset(offset).all()
            result = self.session.query(Event).distinct().filter(Event.dbcode.op('&')(4) == 4)
            result = self.__set_parameters(result, parameters)
            result = result.limit(limit).offset(offset).all()
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found')
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

        return result

    def __get_group_ids_of_group(self, group):
        result = list()
        if group:
            result.append(group.identifier)
            for group in group.children:
                result = result + self.__get_group_ids_of_group(group)
        return result

    def __get_all_group_ids_of_user(self, user):
        result = self.__get_group_ids_of_group(user.group)
        return result

    def get_all_limited_for_user(self, limit, offset, user, parameters=None):
        """Returns only a subset of entries"""
        try:
            group_ids = self.__get_all_group_ids_of_user(user)

            tlp = get_max_tlp(user.group)
            # TODO: events for user
            # TODO add validation and published checks
            # result = self.session.query(self.get_broker_class()).filter(Event.dbcode.op('&')(4) == 4).order_by(Event.created_at.desc()).limit(limit).offset(offset).all()
            # , Event.tlp_level_id >= tlp
            result = self.session.query(Event).distinct().join(EventGroupPermission).filter(and_(Event.dbcode.op('&')(4) == 4, or_(Event.tlp_level_id >= tlp, EventGroupPermission.group_id.in_(group_ids), Event.owner_group_id == user.group_id)))
            result = self.__set_parameters(result, parameters)

            result = result.limit(limit).offset(offset).all()
            # remove all the no viewable
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found')
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

        return result

    def get_all_for_user(self, user):
        """Returns only a subset of entries"""
        try:
            group_ids = self.__get_all_group_ids_of_user(user)
            tlp = get_max_tlp(user.group)
            # TODO: events for user
            # TODO add validation and published checks
            # result = self.session.query(self.get_broker_class()).filter(Event.dbcode.op('&')(4) == 4).order_by(Event.created_at.desc()).limit(limit).offset(offset).all()
            result = self.session.query(Event).distinct().join(EventGroupPermission).filter(and_(Event.dbcode.op('&')(4) == 4, or_(Event.tlp_level_id >= tlp, EventGroupPermission.group_id.in_(group_ids)))).all()
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found')
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

        return result

    def get_all_from(self, from_datetime):
        try:
            result = self.session.query(Event).filter(Event.created_at >= from_datetime).all()
            return result
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def get_total_events(self, parameters=None):
        try:
            # TODO add validation and published checks
            result = self.session.query(Event)
            result = self.__set_parameters(result, parameters)

            result = result.count()
            # result = self.session.query(self.get_broker_class()).count()
            return result
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def get_total_events_for_user(self, user, parameters=None):
        try:
            group_ids = self.__get_all_group_ids_of_user(user)
            tlp = get_max_tlp(user.group)
            # TODO add validation and published checks
            # TODO: total events for user
            result = self.session.query(Event).distinct().join(EventGroupPermission).filter(and_(Event.dbcode.op('&')(4) == 4, or_(Event.tlp_level_id >= tlp, EventGroupPermission.group_id.in_(group_ids))))
            result = self.__set_parameters(result, parameters)

            result = result.count()
            return result
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def get_all_unvalidated_total(self, parameters=None):
        try:
            result = self.session.query(Event).filter(Event.dbcode.op('&')(4) != 4)
            result = self.__set_parameters(result, parameters)
            result = result.count()
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found')
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)
        return result

    def get_all_unvalidated(self, limit=None, offset=None, parameters=None):
        """
        Returns all unvalidated events
        """
        try:
            result = self.session.query(Event).filter(Event.dbcode.op('&')(4) != 4)
            result = self.__set_parameters(result, parameters)
            result = result.order_by(Event.created_at.desc()).limit(limit).offset(offset).all()
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found')
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)
        return result

    def get_group_by_id(self, identifier):
        try:
            result = self.session.query(EventGroupPermission).filter(EventGroupPermission.identifier == identifier).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found')
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)
        return result

    def get_by_uuids(self, ids):
        try:
            result = self.session.query(Event).filter(Event.uuid.in_(ids)).all()
            return result
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)
        return result

    def get_group_by_uuid(self, uuid):
        try:
            result = self.session.query(EventGroupPermission).filter(EventGroupPermission.uuid == uuid).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise NothingFoundException(u'Nothing found')
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)
        return result

    def update_group_permission(self, event_group_permission, commit=True):
        try:
            self.update(event_group_permission, commit)
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def insert_group_permission(self, event_group_permission, commit=True):
        try:
            self.insert(event_group_permission, commit)
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def remove_group_permission_by_id(self, identifier, commit=True):
        try:
            self.session.query(EventGroupPermission).filter(EventGroupPermission.identifier == identifier).delete(synchronize_session='fetch')
            self.do_commit(commit)
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)
