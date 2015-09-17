# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
from sqlalchemy.orm import joinedload
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import and_, or_

from ce1sus.common.utils import get_max_tlp
from ce1sus.db.classes.ccybox.common.time import CyboxTime
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.information_source import InformationSource, InformationSourceRole
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader
from ce1sus.db.classes.cstix.incident.time import Time
from ce1sus.db.classes.internal.common import Analysis, Status, TLP
from ce1sus.db.classes.internal.event import Event, EventGroupPermission
from ce1sus.db.classes.internal.path import Path
from ce1sus.db.classes.internal.usrmgt.group import Group
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, BrokerException, TooManyResultsFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventPermissionBroker(BrokerBase):

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return EventGroupPermission


# pylint: disable=R0904
class EventBroker(BrokerBase):

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Event

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
      anal = parameters.get('filter[initial_author]', None)
      if anal:
        result = result.join(Event.stix_header).join(STIXHeader.information_source).join(InformationSource.identity).filter(Identity.name.like('%{0}%'.format(anal)))
      anal = parameters.get('filter[modified_on]', None)
      if anal:
        result = result.filter(Event.modified_on.like('%{0}%'.format(anal)))
      anal = parameters.get('filter[title]', None)
      if anal:
        result = result.filter(STIXHeader.title.like('%{0}%'.format(anal)))
      anal = parameters.get('filter[status]', None)
      if anal:
        matching_ids = self.__find_id(Status.get_dictionary(), anal)
        result = result.filter(Event.status_id.in_(matching_ids))
      anal = parameters.get('filter[tlp]', None)
      if anal:
        matching_ids = self.__find_id(TLP.get_dictionary(), anal)
        result = result.join(Event.path).filter(Path.item_tlp_level_id.in_(matching_ids))

      # do a similar stuff for sorting
      anal = parameters.get('sorting[analysis]', None)
      if anal:
        if anal == 'desc':
          result = result.order_by(Event.analysis_id.desc())
        else:
          result = result.order_by(Event.analysis_id.asc())

      anal = parameters.get('sorting[initial_author]', None)
      if anal:
        if anal == 'desc':
          result = result.join(Event.stix_header).join(STIXHeader.information_source).join(InformationSource.identity).order_by(Identity.name.desc())
        else:
          result = result.join(Event.stix_header).join(STIXHeader.information_source).join(InformationSource.identity).order_by(Identity.name.asc())

      anal = parameters.get('sorting[modified_on]', None)
      if anal:
        if anal == 'desc':
          result = result.order_by(Event.modified_on.desc())
        else:
          result = result.order_by(Event.modified_on.asc())

      anal = parameters.get('sorting[title]', None)
      if anal:
        if anal == 'desc':
          result = result.order_by(STIXHeader.title.desc())
        else:
          result = result.order_by(STIXHeader.title.asc())

      anal = parameters.get('sorting[status]', None)
      if anal:
        if anal == 'desc':
          result = result.order_by(Event.status_id.desc())
        else:
          result = result.order_by(Event.status_id.asc())

      anal = parameters.get('sorting[tlp]', None)
      if anal:
        if anal == 'desc':
          result = result.join(Event.path).order_by(Path.item_tlp_level_id.desc())
        else:
          result = result.join(Event.path).order_by(Path.item_tlp_level_id.asc())

      anal = parameters.get('sorting[id]', None)
      if anal:
        if anal == 'desc':
          result = result.order_by(Event.identifier.desc())
        else:
          result = result.order_by(Event.identifier.asc())
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

  def __get_events_query(self, user, parameters, unvalidated_only=False, loadalong=True):
    if user:
      group_ids = self.__get_all_group_ids_of_user(user)
      tlp = get_max_tlp(user.group)

    query = self.session.query(Event.identifier).join(Event.path).outerjoin(Event.groups)
    if unvalidated_only:
      query = query.filter(Path.dbcode.op('&')(4) != 4)
    else:
      query = query.filter(or_(Event.creator_group_id == user.group.identifier,
                               and_(Path.dbcode.op('&')(12) == 12,
                                    or_(Path.tlp_level_id >= tlp,
                                        EventGroupPermission.group_id.in_(group_ids),
                                        )
                                    )
                               )
                           )
    if parameters:
      query = self.__set_parameters(query, parameters)
    ids = list()
    for value in query.all():
      ids.append(value[0])

    query = self.session.query(Event)
    if loadalong:
      query = query.options(joinedload(Event.path),
                            joinedload(Event.groups),
                            joinedload(Event.stix_header),
                            joinedload(Event.stix_header).joinedload(STIXHeader.path),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.roles),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.roles).joinedload(InformationSourceRole.path),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.path),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.identity),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.identity).joinedload(Identity.path),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.time),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.time).joinedload(CyboxTime.path),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.time).joinedload(CyboxTime.start_time),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.time).joinedload(CyboxTime.end_time),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.time).joinedload(CyboxTime.produced_time),
                            joinedload(Event.stix_header).joinedload(STIXHeader.information_source).joinedload(InformationSource.time).joinedload(CyboxTime.received_time),
                            joinedload(Event.stix_header).joinedload(STIXHeader.path)
                            )
    query = query.filter(Event.identifier.in_(ids))
    query = self.__set_parameters(query, parameters)
    return query

  def get_all_for_user(self, user, limit=None, offset=None, parameters=None):
    """Returns only a subset of entries"""
    try:
      query = self.__get_events_query(user, parameters)
      if limit is None and offset is None:
        result = query.all()
      else:
        result = query.limit(limit).offset(offset).all()
      return result

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:

      raise BrokerException(error)

  def get_all_from(self, user, from_datetime):
    try:
      query = self.__get_events_query(user, None)
      result = query.filter(Event.created_at >= from_datetime).all()
      return result
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_total_events(self, user, parameters=None):
    try:
      query = self.__get_events_query(user, parameters, loadalong=False)
      result = query.count()
      return result
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_all_unvalidated_total(self, user, parameters=None):
    try:
      query = self.__get_events_query(None, parameters, unvalidated_only=True, loadalong=False)
      result = query.count()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:

      raise BrokerException(error)


  def get_all_unvalidated(self, limit=None, offset=None, parameters=None):
    """
    Returns all unvalidated events
    """
    try:
      query = self.__get_events_query(None, parameters, unvalidated_only=True)
      result = query.order_by(Event.created_at.desc()).limit(limit).offset(offset).all()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:

      raise BrokerException(error)


  def get_group_by_id(self, identifier):
    try:
      result = self.session.query(EventGroupPermission).filter(EventGroupPermission.identifier == identifier).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:

      raise BrokerException(error)
    return result

  def get_by_uuids(self, ids):
    try:
      result = self.session.query(Event).filter(Event.uuid.in_(ids)).all()
      return result
    except sqlalchemy.exc.SQLAlchemyError as error:

      raise BrokerException(error)
    return result

  def get_group_by_uuid(self, uuid):
    try:
      result = self.session.query(EventGroupPermission).filter(EventGroupPermission.uuid == uuid).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:

      raise BrokerException(error)
    return result

  def update_group_permission(self, event_group_permission, commit=True):
    try:
      self.update(event_group_permission, commit)
    except sqlalchemy.exc.SQLAlchemyError as error:

      raise BrokerException(error)

  def insert_group_permission(self, event_group_permission, commit=True):
    try:
      self.insert(event_group_permission, commit)
    except sqlalchemy.exc.SQLAlchemyError as error:

      raise BrokerException(error)

  def remove_group_permission_by_id(self, identifier, commit=True):
    try:
      self.session.query(EventGroupPermission).filter(EventGroupPermission.identifier == identifier).delete(synchronize_session='fetch')
      self.do_commit(commit)
    except sqlalchemy.exc.SQLAlchemyError as error:

      raise BrokerException(error)
