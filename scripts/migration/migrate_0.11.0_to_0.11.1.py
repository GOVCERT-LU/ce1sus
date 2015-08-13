# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 2, 2015
"""




import json
from optparse import OptionParser
from os.path import dirname, abspath, exists, isdir
from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy.exc import OperationalError
from sqlalchemy.schema import Table, ForeignKeyConstraint, ForeignKey
from sqlalchemy.types import UnicodeText, Unicode, Integer, BigInteger
from sqlalchemy.orm import relationship

import sys
from types import ListType
from uuid import uuid4
from alembic.migration import MigrationContext
from alembic.operations import Operations

basePath = dirname(abspath(__file__)) + '/../../'
sys.path.insert(0, '../../')

from ce1sus.db.classes.cstix.core.stix_header import STIXHeader
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.helpers.common.config import Configuration
from ce1sus.helpers.common.objects import get_class
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition, ObservableKeyword
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification, MarkingStructure
from ce1sus.db.classes.cstix.common.vocabstring import VocabString
from ce1sus.db.classes.cstix.common.kill_chains import KillChainPhase, Killchain
from ce1sus.db.classes.cstix.common.related import RelatedObservable
from ce1sus.db.classes.cstix.indicator.indicator import Indicator, IndicatorType
from ce1sus.db.classes.cstix.indicator.sightings import Sighting
from ce1sus.db.classes.internal.event import Event, Comment, EventGroupPermission
from ce1sus.db.classes.internal.object import RelatedObject
from ce1sus.db.classes.internal.report import Reference
from ce1sus.db.classes.internal.report import Report
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.common.session import Base
from ce1sus.db.common.session import SessionManager
from ce1sus.helpers.common.debug import Log
from ce1sus.db.classes.internal.definitions import ObjectDefinition
from ce1sus.db.classes.internal.definitions import AttributeDefinition
from ce1sus.db.classes.internal.usrmgt.user import User
from ce1sus.db.classes.internal.usrmgt.group import Group, EventPermissions
from ce1sus.db.classes.internal.attributes.attribute import Attribute, Condition
from ce1sus.db.classes.internal.core import BaseObject
from ce1sus.db.classes.cstix.indicator import IndicatorType
from ce1sus.db.classes.cstix.common.kill_chains import Killchain
from ce1sus.db.classes.cstix.common.information_source import InformationSource, InformationSourceRole
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.ccybox.common.time import CyboxTime
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.cstix.indicator.valid_time import ValidTime


class Migrator(object):

  def __init__(self, config):
    self.config = config
    self.logger = Log(config).get_logger('Main')
    self.sm = SessionManager(config).connector
    directconnection = self.sm.get_direct_session()
    self.session = directconnection
    self.engine = self.sm.get_engine()
    conn = self.engine.connect()
    ctx = MigrationContext.configure(
                connection=conn
    )
    self.op = Operations(ctx)

  def create_new_tables(self):
    engine = self.engine
    getattr(Base, 'metadata').create_all(engine, checkfirst=True)

  def __get_class_instance(self, column):
    classname = column.type.__class__.__name__
    clazz = get_class('sqlalchemy.types', classname)
    

    if hasattr(column.type, 'length') and hasattr(column.type, 'collation'):
      clazz_instance = clazz(column.type.length, collation=column.type.collation)
    elif hasattr(column.type, 'length'):
      clazz_instance = clazz(column.type.length)
    else:
      clazz_instance = clazz()
    return clazz_instance

  def __get_args(self, column):
    args = dict()
    args['index'] = column.expression.index
    args['nullable'] = column.expression.nullable
    args['unique'] = column.expression.unique
    return args
  
  def __alter_column(self, clazz, column_name):
    table_name = clazz.get_table_name()
    column = getattr(clazz, column_name)
    clazz_instance = self.__get_class_instance(column)
    args = self.__get_args(column)
    args['type_'] = clazz_instance
    del args['index']
    del args['unique']
    self.op.alter_column(table_name, column.name, **args)
  
  def __add_column(self, clazz, column_name):

    table_name = clazz.get_table_name()
    column = getattr(clazz, column_name)
    clazz_instance = self.__get_class_instance(column)
    args = self.__get_args(column)
    self.op.add_column(table_name, Column(column.name, clazz_instance, **args))

  def __drop_fk(self, clazz, fk_name):
    table_name = clazz.get_table_name()
    self.op.drop_constraint(fk_name, table_name, type_='foreignkey')

  def __change_column(self, clazz, column_name):
    table_name = clazz.get_table_name()
    column = getattr(clazz, column_name)
    args = self.__get_args(column)
    self.op.alter_column(table_name, column.name, **args)

  def __add_index(self, clazz, index_name, column_name):
    table_name = clazz.get_table_name()
    column = getattr(clazz, column_name)
    self.op.create_index(index_name, table_name, [column.name])
  
  def __drop_index(self, clazz, index_name):
    table_name = clazz.get_table_name()
    self.op.drop_index(index_name, table_name)

  def __drop_column(self, clazz, column_name):
    table_name = clazz.get_table_name()
    self.op.drop_column(table_name, column_name)

  def __drop_table(self, table_name):
    self.op.drop_table(table_name)


  def __add_fk(self, clazz, column_name, fk_name):
    table = Table(clazz.get_table_name(), Base.metadata, autoload=True)
    column = getattr(clazz, column_name)

    for constraint in table.constraints:
      if isinstance(constraint, ForeignKeyConstraint):
        if column_name == constraint.columns[0].name:
          fk = constraint.elements[0]

          referent_table = fk.column.table.name
          remote_cols = [fk.column.name]
          local_cols = [column.name]
          args = dict()
          args['onupdate'] = constraint.onupdate
          args['ondelete'] = constraint.ondelete

          self.op.create_foreign_key(fk_name, table.name, referent_table, local_cols, remote_cols, **args)
          break

  def __drop_add_pk(self, table_name, column_name):
    try:
      self.op.drop_constraint(None, table_name, type_='primary')
    except OperationalError:
      pass
    self.op.create_primary_key(None, table_name, [column_name])

  # drop cols
  def altering_tables_phase2(self):

    self.__add_fk(Condition, 'creator_id', 'conditions_ibfk_1')
    self.__add_fk(Condition, 'modifier_id', 'conditions_ibfk_2')

    self.__drop_column(Event, 'originating_group_id')
    self.__drop_column(Event, 'owner_group_id')
    # self.__drop_column(Event, 'code')
    # self.__drop_column(Event, 'tlp_level_id')
    self.__drop_column(Event, 'description')
    self.__drop_column(Event, 'title')

    self.__drop_column(Indicator, 'description')
    self.__drop_column(Indicator, 'short_description')
    self.__drop_column(Indicator, 'confidence')
    self.__drop_column(Indicator, 'originating_group_id')
    self.__drop_column(Indicator, 'owner_group_id')

    self.__add_fk(IndicatorType, 'creator_group_id', 'indicatortypes_ibfk_2')
    self.__add_fk(IndicatorType, 'creator_id', 'indicatortypes_ibfk_3')
    self.__add_fk(IndicatorType, 'modifier_id', 'indicatortypes_ibfk_4')

    self.__add_fk(KillChainPhase, 'creator_group_id', 'killchainphases_ibfk_1')
    self.__add_fk(KillChainPhase, 'creator_id', 'killchainphases_ibfk_2')
    self.__add_fk(KillChainPhase, 'modifier_id', 'killchainphases_ibfk_3')

    self.__add_fk(ObservableComposition, 'creator_group_id', 'observablecompositions_ibfk_2')
    self.__add_fk(ObservableComposition, 'creator_id', 'observablecompositions_ibfk_3')
    self.__add_fk(ObservableComposition, 'modifier_id', 'observablecompositions_ibfk_4')

    self.__add_fk(ObservableKeyword, 'creator_group_id', 'observablekeywords_ibfk_2')
    self.__add_fk(ObservableKeyword, 'creator_id', 'observablekeywords_ibfk_3')
    self.__add_fk(ObservableKeyword, 'modifier_id', 'observablekeywords_ibfk_4')

    self.__drop_column(Observable, 'description')
    self.__drop_column(Observable, 'originating_group_id')
    self.__drop_column(Observable, 'owner_group_id')

    self.__add_fk(RelatedObject, 'creator_group_id', 'relatedobjects_ibfk_3')
    self.__add_fk(RelatedObject, 'creator_id', 'relatedobjects_ibfk_4')
    self.__add_fk(RelatedObject, 'modifier_id', 'relatedobjects_ibfk_5')
    self.__drop_column(RelatedObject, 'relation')

    self.__add_fk(RelatedObservable, 'child_id', 'relatedobservables_ibfk_1')
    self.__drop_column(RelatedObservable, 'confidence')
    self.__drop_column(RelatedObservable, 'relation')
    self.__drop_column(RelatedObservable, 'parent_id')

    # self.__drop_column(MarkingStructure, 'marking_id')

    self.__drop_column(Sighting, 'description')
    self.__drop_column(Sighting, 'confidence')
    self.__drop_column(Sighting, 'originating_group_id')
    self.__drop_column(Sighting, 'owner_group_id')

    self.__drop_table('rel_ttps_killchains')
    self.__drop_table('ttpss')
    self.__drop_table('rel_ttps_killchains')
    self.__drop_table('rel_event_handling')
    # self.__drop_table('markings')

  
  @staticmethod
  def __set_old_fields(clazz):
    classname = clazz.get_classname()
    setattr(clazz, 'originating_group_id', Column('originating_group_id', BigInteger, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True))
    setattr(clazz, 'owner_group_id', Column('owner_group_id', BigInteger, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True))


  @staticmethod
  def __unset_old_fields(clazz):
    setattr(clazz, 'originating_group_id', None)
    setattr(clazz, 'originating_group', None)
    setattr(clazz, 'owner_group_id', None)
    setattr(clazz, 'owner_group', None)
  

  def __set_tlp_code(self, instance, parent):
    instance.tlp_level_id = parent.tlp_level_id
    instance.dbcode = parent.dbcode

  def __set_simplelogging(self, instance, parent):
    instance.created_at = parent.created_at
    instance.modified_on = parent.modified_on
    instance.modifier_id = parent.modifier_id
    instance.creator_id = parent.creator_id

  def __set_extendedlogging(self, instance, parent):
    self.__set_simplelogging(instance, parent)
    instance.creator_group_id = parent.creator_group_id

  def __create_information_source(self, group_id, role, instance):
    informationsource = InformationSource()
    self.__set_extendedlogging(informationsource, instance)
    self.__set_tlp_code(informationsource, instance)
    informationsource.identity = Identity()
    self.__set_extendedlogging(informationsource.identity, instance)
    self.__set_tlp_code(informationsource.identity, instance)
    
    group = self.session.get_session().query(Group).filter(Group.identifier == group_id).one()
    
    informationsource.identity.name = group.name
    informationsource.identity.namespace = 'ce1sus'
    isrole = InformationSourceRole()
    self.__set_extendedlogging(isrole, informationsource)
    self.__set_tlp_code(isrole, informationsource)
    isrole.role = role
    informationsource.roles.append(isrole)

    time = CyboxTime()
    self.__set_extendedlogging(time, instance)
    self.__set_tlp_code(time, instance)
    time.produced_time = DateTimeWithPrecision()
    self.__set_extendedlogging(time.produced_time, instance)
    self.__set_tlp_code(time.produced_time, instance)
    time.produced_time.value = instance.created_at
    informationsource.time = time

    return informationsource

  def __is_misp(self, event):
    for report in event.reports:
      for reference in report.references:
        if 'misp' in reference.value:
          return True
    return False

  def merge_data(self):

    all = self.session.get_session().query(Condition).all()
    for item in all:
      self.__set_simplelogging(item, all)
      self.session.get_session().merge(item)
      self.session.get_session().flush()

    setattr(Event, 'foo', Column('description', UnicodeText(collation='utf8_unicode_ci')))
    setattr(Event, 'title', Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=False))
    setattr(Event, 'tlp_level_id2', Column('tlp_level_id', Integer, default=3, nullable=False))
    setattr(Event, 'dbcode2', Column('code', Integer, nullable=False, default=0))
    Migrator.__set_old_fields(Event)
    
    all = self.session.get_session().query(Event).all()
    for item in all:
      if item.foo:
        item.version = '1.0.0'
        item.namespace = 'ce1sus'

        item.stix_header = STIXHeader()
        item.stix_header.title = item.title
        self.__set_tlp_code(item.stix_header, item)
        self.__set_extendedlogging(item.stix_header, item)
        is_ = self.__create_information_source(item.originating_group_id, 'Initial Author', item)
        item.stix_header.information_source = is_
        if self.__is_misp(item):
          is_ = self.__create_information_source(item.creator_group_id, 'Transformer/Translator', item)
          item.stix_header.information_source.contributing_sources.append(is_)



        # handling not used yet

        desription = StructuredText()
        desription.value = item.foo
        desription.namespace = 'ce1sus'
        self.__set_extendedlogging(desription, item)
        self.__set_tlp_code(desription, item)
        item.stix_header.description = desription






        self.session.get_session().merge(item)
        self.session.get_session().flush()

    Migrator.__set_old_fields(Indicator)
    setattr(Indicator, 'foo', Column('description', UnicodeText(collation='utf8_unicode_ci')))
    setattr(Indicator, 'bar', Column('short_description', Unicode(255, collation='utf8_unicode_ci')))


    all = self.session.get_session().query(Indicator).all()
    for item in all:
      item.namespace = 'ce1sus'
      item.version = '1.0.0'
      item.timestamp = item.created_at
      desription = None

      if item.foo:
        desription = StructuredText()
        desription.value = item.foo
        desription.namespace = 'ce1sus'
        self.__set_extendedlogging(desription, item)
        self.__set_tlp_code(description, item)
        item.description = desription

      short_description = None
      if item.bar:
        short_description = StructuredText()
        short_description.value = item.bar
        short_description.namespace = 'ce1sus'
        self.__set_extendedlogging(desription, item)
        self.__set_tlp_code(description, item)
        item.short_description = short_description

      is_ = self.__create_information_source(item.originating_group_id, 'Initial Author', item)
      item.producer = is_

      self.session.get_session().merge(item)
      self.session.get_session().flush()

    setattr(Indicator, 'foo', None)
    setattr(Indicator, 'bar', None)
    self.__unset_old_fields(Indicator)
    
    
    types = self.session.get_session().query(IndicatorType).all()
    for type_ in types:
      parent = type_.indicator
      self.__set_extendedlogging(type_, parent)
      self.__set_tlp_code(type_, parent)

      self.session.get_session().merge(type_)
      self.session.get_session().flush()
    


    all = self.session.get_session().query(KillChainPhase).all()
    for item in all:
      if hasattr(item, 'indicator'):
        parent = item.indicator
      if hasattr(item, 'killchain'):
        parent = item.killchain

      self.__set_extendedlogging(item, parent)
      self.__set_tlp_code(item, parent)

      self.session.get_session().merge(item)
      self.session.get_session().flush()



    # TODO: killchains
    
    #TODO: Markings
    #TODO: Markingstructures
    
    all = self.session.get_session().query(Object).all()
    for item in all:
      item.namespace = 'ce1sus'
      self.session.get_session().merge(item)
      self.session.get_session().flush()

    all = self.session.get_session().query(ObservableComposition).all()
    for item in all:
      item.namespace = 'ce1sus'
      parent = item.parent
      self.__set_extendedlogging(item, parent)
      item.tlp_level_id = parent.tlp_level_id

      self.session.get_session().merge(item)
      self.session.get_session().flush()

    all = self.session.get_session().query(ObservableKeyword).all()
    for item in all:
      parent = item.observable
      self.__set_extendedlogging(item, parent)
      self.__set_tlp_code(item, parent)

      self.session.get_session().merge(item)
      self.session.get_session().flush()

    setattr(Observable, 'foo', Column('description', UnicodeText(collation='utf8_unicode_ci')))
    self.__set_old_fields(Observable)

    all = self.session.get_session().query(Observable).all()
    for item in all:
      if item.foo:
        item.namespace = 'ce1sus'
        item.version = '1.0.0'
        desription = StructuredText()
        desription.value = item.foo
        desription.namespace = 'ce1sus'
        self.__set_extendedlogging(desription, parent)
        self.__set_tlp_code(desription, parent)
        item.description = desription

        self.session.get_session().merge(item)
        self.session.get_session().flush()

    #Reference were just columns removed

    all = self.session.get_session().query(RelatedObject).all()
    for item in all:
      parent = item.object
      self.__set_extendedlogging(item, parent)
      self.__set_tlp_code(item, parent)

      self.session.get_session().merge(item)
      self.session.get_session().flush()


    setattr(RelatedObservable, 'foo', Column('confidence', Unicode(5, collation='utf8_unicode_ci'), default=u'HIGH', nullable=False))

    all = self.session.get_session().query(RelatedObservable).all()
    for item in all:
      confidence = None
      if item.foo:
        confidence = Confidence()
        confidence.value = item.foo
        self.__set_extendedlogging(confidence, item)
        self.__set_tlp_code(confidence, item)
        item.confidence = confidence
        is_ = self.__create_information_source(item.creator_group_id, 'Initial Author', item)
        item.source = is_

      parent = item.observable
      self.__set_tlp_code(item, parent)

      self.session.get_session().merge(item)
      self.session.get_session().flush()


    setattr(RelatedObservable, 'foo', None)

    # Report only columns were dropped

    setattr(Sighting, 'foo', Column('confidence', Unicode(5, collation='utf8_unicode_ci'), default=u'HIGH', nullable=False))
    setattr(Sighting, 'bar', Column('description', UnicodeText(collation='utf8_unicode_ci')))
    self.__set_old_fields(Sighting)

    all = self.session.get_session().query(Sighting).all()
    for item in all:
      parent = item.indicator
      item.timestamp = item.created_at
      item.tlp_level_id = parent[0].tlp_level_id
      if item.foo:
        confidence = Confidence()
        confidence.value = item.foo
        self.__set_extendedlogging(confidence, item)
        self.__set_tlp_code(confidence, item)
        item.confidence = confidence
        is_ = self.__create_information_source(item.creator_group_id, 'Initial Author', item)
        item.source = is_

      if item.bar:
        desription = StructuredText()
        desription.value = item.bar
        desription.namespace = 'ce1sus'
        self.__set_extendedlogging(desription, item)
        self.__set_tlp_code(desription, item)
        item.description = desription

      is_ = self.__create_information_source(item.creator_group_id, 'Initial Author', item)
      item.source = is_

      self.session.get_session().merge(item)
      self.session.get_session().flush()

    setattr(Sighting, 'foo', None)
    setattr(Sighting, 'bar', None)
    self.__unset_old_fields(Sighting)

    self.session.get_session().commit()

  # TODO: Valid time positions

  def altering_tables_phase1(self):

    self.__drop_fk(Attribute, 'attributes_ibfk_5')
    self.__drop_fk(Attribute, 'attributes_ibfk_6')
    self.__drop_fk(Attribute, 'attributes_ibfk_7')
    self.__drop_fk(Attribute, 'attributes_ibfk_9')
    self.__drop_fk(Attribute, 'attributes_ibfk_8')
    self.__drop_column(Attribute, 'originating_group_id')
    self.__drop_column(Attribute, 'owner_group_id')
    self.__add_fk(Attribute, 'creator_group_id', 'attributes_ibfk_5')
    self.__add_fk(Attribute, 'creator_id', 'attributes_ibfk_6')
    self.__add_fk(Attribute, 'modifier_id', 'attributes_ibfk_7')

    self.__drop_fk(Comment, 'comments_ibfk_2')
    self.__drop_fk(Comment, 'comments_ibfk_3')
    self.__drop_fk(Comment, 'comments_ibfk_4')
    self.__drop_fk(Comment, 'comments_ibfk_5')
    self.__drop_fk(Comment, 'comments_ibfk_6')
    self.__drop_column(Comment, 'originating_group_id')
    self.__drop_column(Comment, 'owner_group_id')
    self.__add_fk(Comment, 'creator_group_id', 'comments_ibfk_2')
    self.__add_fk(Comment, 'creator_id', 'comments_ibfk_3')
    self.__add_fk(Comment, 'modifier_id', 'comments_ibfk_4')
    
    self.__add_column(Condition, 'created_at')
    self.__add_column(Condition, 'modified_on')
    self.__add_column(Condition, 'creator_id')
    self.__add_column(Condition, 'modifier_id')
    self.__add_index(Condition, 'ix_conditions_creator_id', 'creator_id')
    self.__add_index(Condition, 'ix_conditions_modifier_id', 'modifier_id')

    self.__drop_fk(EventGroupPermission, 'eventgrouppermissions_ibfk_3')
    self.__drop_fk(EventGroupPermission, 'eventgrouppermissions_ibfk_4')
    self.__drop_fk(EventGroupPermission, 'eventgrouppermissions_ibfk_5')
    self.__drop_fk(EventGroupPermission, 'eventgrouppermissions_ibfk_6')
    self.__drop_fk(EventGroupPermission, 'eventgrouppermissions_ibfk_7')
    self.__drop_column(EventGroupPermission, 'originating_group_id')
    self.__drop_column(EventGroupPermission, 'owner_group_id')
    self.__add_fk(EventGroupPermission, 'creator_group_id', 'eventgrouppermissions_ibfk_3')
    self.__add_fk(EventGroupPermission, 'creator_id', 'eventgrouppermissions_ibfk_4')
    self.__add_fk(EventGroupPermission, 'modifier_id', 'eventgrouppermissions_ibfk_5')


    self.__drop_fk(Event, 'events_ibfk_1')
    self.__drop_fk(Event, 'events_ibfk_2')
    self.__drop_fk(Event, 'events_ibfk_3')
    self.__drop_fk(Event, 'events_ibfk_5')
    self.__drop_fk(Event, 'events_ibfk_4')
    self.__add_column(Event, 'version')
    self.__add_column(Event, 'idref')
    self.__add_column(Event, 'namespace')
    self.__add_index(Event, 'ix_events_namespace', 'namespace')
    self.__add_index(Event, 'ix_events_idref', 'idref')
    self.__add_fk(Event, 'creator_group_id', 'events_ibfk_1')
    self.__add_fk(Event, 'creator_id', 'events_ibfk_2')
    self.__add_fk(Event, 'modifier_id', 'events_ibfk_3')


    self.__drop_fk(Indicator, 'indicators_ibfk_2')
    self.__drop_fk(Indicator, 'indicators_ibfk_3')
    self.__drop_fk(Indicator, 'indicators_ibfk_4')
    self.__drop_fk(Indicator, 'indicators_ibfk_6')
    self.__drop_fk(Indicator, 'indicators_ibfk_5')
    self.__add_column(Indicator, 'namespace')
    self.__add_column(Indicator, 'timestamp')
    self.__add_column(Indicator, 'alternative_id')
    self.__add_column(Indicator, 'negate')
    self.__add_column(Indicator, 'idref')
    self.__add_index(Indicator, 'ix_indicators_namespace', 'namespace')
    self.__add_index(Indicator, 'ix_indicators_indicator_idref', 'idref')
    self.__add_fk(Indicator, 'creator_group_id', 'indicators_ibfk_2')
    self.__add_fk(Indicator, 'creator_id', 'indicators_ibfk_3')
    self.__add_fk(Indicator, 'modifier_id', 'indicators_ibfk_4')

    self.__add_column(IndicatorType, 'created_at')
    self.__add_column(IndicatorType, 'modified_on')
    self.__add_column(IndicatorType, 'tlp_level_id')
    self.__add_column(IndicatorType, 'dbcode')
    self.__add_column(IndicatorType, 'creator_group_id')
    self.__add_column(IndicatorType, 'creator_id')
    self.__add_column(IndicatorType, 'modifier_id')
    self.__add_index(IndicatorType, 'ix_indicatortypes_modifier_id', 'modifier_id')
    self.__add_index(IndicatorType, 'ix_indicatortypes_creator_group_id', 'creator_group_id')
    self.__add_index(IndicatorType, 'ix_indicatortypes_code', 'dbcode')
    self.__add_index(IndicatorType, 'ix_indicatortypes_creator_id', 'creator_id')

    self.__add_column(KillChainPhase, 'created_at')
    self.__add_column(KillChainPhase, 'modified_on')
    self.__add_column(KillChainPhase, 'tlp_level_id')
    self.__add_column(KillChainPhase, 'dbcode')
    self.__add_column(KillChainPhase, 'creator_group_id')
    self.__add_column(KillChainPhase, 'creator_id')
    self.__add_column(KillChainPhase, 'modifier_id')
    self.__add_index(KillChainPhase, 'ix_killchainphases_modifier_id', 'modifier_id')
    self.__add_index(KillChainPhase, 'ix_killchainphases_code', 'creator_group_id')
    self.__add_index(KillChainPhase, 'ix_killchainphases_creator_id', 'dbcode')
    self.__add_index(KillChainPhase, 'ix_killchainphases_owner_group_id', 'creator_id')


    self.__drop_fk(Killchain, 'killchains_ibfk_1')
    self.__drop_fk(Killchain, 'killchains_ibfk_2')
    self.__drop_fk(Killchain, 'killchains_ibfk_3')
    self.__drop_fk(Killchain, 'killchains_ibfk_5')
    self.__drop_fk(Killchain, 'killchains_ibfk_4')
    self.__drop_column(Killchain, 'originating_group_id')
    self.__drop_column(Killchain, 'owner_group_id')
    self.__add_column(Killchain, 'dbcode')
    self.__add_column(Killchain, 'tlp_level_id')
    self.__add_column(Killchain, 'definer')
    self.__add_index(Killchain, 'ix_killchains_code', 'dbcode')
    self.__add_fk(Killchain, 'creator_group_id', 'killchains_ibfk_1')
    self.__add_fk(Killchain, 'creator_id', 'killchains_ibfk_2')
    self.__add_fk(Killchain, 'modifier_id', 'killchains_ibfk_3')

    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_2')
    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_3')
    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_4')
    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_6')
    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_5')
    self.__drop_column(MarkingStructure, 'originating_group_id')
    self.__drop_column(MarkingStructure, 'owner_group_id')
    self.__drop_column(MarkingStructure, 'value')
    self.__drop_column(MarkingStructure, 'type_id')
   
    self.__add_column(MarkingStructure, 'dbcode')
    self.__add_column(MarkingStructure, 'tlp_level_id')
    self.__add_column(MarkingStructure, 'namespace')
    self.__add_index(MarkingStructure, 'ix_markings_code', 'dbcode')
    self.__add_index(MarkingStructure, 'ix_markingstructures_namespace', 'namespace')
    self.__add_fk(MarkingStructure, 'creator_group_id', 'markingstructures_ibfk_2')
    self.__add_fk(MarkingStructure, 'creator_id', 'markingstructures_ibfk_3')
    self.__add_fk(MarkingStructure, 'modifier_id', 'markingstructures_ibfk_4')


    self.__drop_fk(Object, 'objects_ibfk_4')
    self.__drop_fk(Object, 'objects_ibfk_5')
    self.__drop_fk(Object, 'objects_ibfk_6')
    self.__drop_fk(Object, 'objects_ibfk_8')
    self.__drop_fk(Object, 'objects_ibfk_7')
    self.__drop_column(Object, 'originating_group_id')
    self.__drop_column(Object, 'owner_group_id')
    self.__add_column(Object, 'idref')
    self.__add_column(Object, 'namespace')
    self.__add_index(Object, 'ix_objects_namespace', 'namespace')
    self.__add_index(Object, 'ix_objects_idref', 'idref')
    self.__add_fk(Object, 'creator_group_id', 'objects_ibfk_4')
    self.__add_fk(Object, 'creator_id', 'objects_ibfk_5')
    self.__add_fk(Object, 'modifier_id', 'objects_ibfk_6')


    self.__add_column(ObservableComposition, 'created_at')
    self.__add_column(ObservableComposition, 'modified_on')
    self.__add_column(ObservableComposition, 'creator_group_id')
    self.__add_column(ObservableComposition, 'creator_id')
    self.__add_column(ObservableComposition, 'modifier_id')
    self.__add_column(ObservableComposition, 'tlp_level_id')
    self.__add_index(ObservableComposition, 'ix_observablecompositions_modifier_id', 'modifier_id')
    self.__add_index(ObservableComposition, 'ix_observablecompositions_creator_id', 'creator_id')
    self.__add_index(ObservableComposition, 'ix_observablecompositions_creator_group_id', 'creator_group_id')

    self.__add_column(ObservableKeyword, 'created_at')
    self.__add_column(ObservableKeyword, 'modified_on')
    self.__add_column(ObservableKeyword, 'dbcode')
    self.__add_column(ObservableKeyword, 'creator_group_id')
    self.__add_column(ObservableKeyword, 'creator_id')
    self.__add_column(ObservableKeyword, 'modifier_id')
    self.__add_column(ObservableKeyword, 'tlp_level_id')
    self.__add_index(ObservableKeyword, 'ix_observablekeywords_code', 'modifier_id')
    self.__add_index(ObservableKeyword, 'ix_observablekeywords_creator_id', 'creator_id')
    self.__add_index(ObservableKeyword, 'ix_observablekeywords_creator_group_id', 'creator_group_id')
    self.__add_index(ObservableKeyword, 'ix_observablekeywords_modifier_id', 'creator_group_id')


    self.__drop_fk(Observable, 'observables_ibfk_3')
    self.__drop_fk(Observable, 'observables_ibfk_4')
    self.__drop_fk(Observable, 'observables_ibfk_5')
    self.__drop_fk(Observable, 'observables_ibfk_7')
    self.__drop_fk(Observable, 'observables_ibfk_6')
    self.__drop_fk(Observable, 'observables_ibfk_1')
    self.__drop_column(Observable, 'version')
    self.__add_column(Observable, 'namespace')
    self.__add_column(Observable, 'idref')
    self.__add_column(Observable, 'sighting_count')
    self.__drop_column(Observable, 'parent_id')
    self.__add_index(Observable, 'ix_observables_idref', 'idref')
    self.__add_index(Observable, 'ix_observables_sighting_count', 'sighting_count')
    self.__add_index(Observable, 'ix_observables_namespace', 'namespace')
    self.__add_fk(Observable, 'creator_group_id', 'observables_ibfk_3')
    self.__add_fk(Observable, 'creator_id', 'observables_ibfk_4')
    self.__add_fk(Observable, 'modifier_id', 'observables_ibfk_5')


    self.__drop_fk(Reference, 'references_ibfk_4')
    self.__drop_fk(Reference, 'references_ibfk_5')
    self.__drop_fk(Reference, 'references_ibfk_6')
    self.__drop_fk(Reference, 'references_ibfk_8')
    self.__drop_fk(Reference, 'references_ibfk_7')
    self.__drop_column(Reference, 'originating_group_id')
    self.__drop_column(Reference, 'owner_group_id')
    self.__add_index(Reference, 'ix_references_code', 'dbcode')
    self.__add_fk(Reference, 'creator_group_id', 'references_ibfk_4')
    self.__add_fk(Reference, 'creator_id', 'references_ibfk_5')
    self.__add_fk(Reference, 'modifier_id', 'references_ibfk_6')



    self.__add_column(RelatedObject, 'created_at')
    self.__add_column(RelatedObject, 'modified_on')
    self.__add_column(RelatedObject, 'tlp_level_id')
    self.__add_column(RelatedObject, 'dbcode')
    self.__add_column(RelatedObject, 'relationship_id')
    self.__add_column(RelatedObject, 'idref')
    self.__add_column(RelatedObject, 'creator_group_id')
    self.__add_column(RelatedObject, 'creator_id')
    self.__add_column(RelatedObject, 'modifier_id')
    self.__add_index(RelatedObject, 'ix_relatedobjects_modifier_id', 'modifier_id')
    self.__add_index(RelatedObject, 'ix_relatedobjects_owner_group_id', 'creator_group_id')
    self.__add_index(RelatedObject, 'ix_relatedobjects_creator_id', 'dbcode')
    self.__add_index(RelatedObject, 'ix_relatedobjects_code', 'creator_id')
    self.__add_index(RelatedObject, 'idref', 'idref')



    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_1')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_2')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_3')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_4')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_5')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_6')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_7')
    self.__drop_column(RelatedObservable, 'originating_group_id')
    self.__drop_column(RelatedObservable, 'owner_group_id')
    self.__add_column(RelatedObservable, 'tlp_level_id')
    self.__add_column(RelatedObservable, 'dbcode')
    self.__add_column(RelatedObservable, 'relationship')
    self.__add_index(RelatedObservable, 'ix_relatedobservables_code', 'dbcode')
    self.__add_fk(RelatedObservable, 'creator_group_id', 'relatedobservables_ibfk_2')
    self.__add_fk(RelatedObservable, 'creator_id', 'relatedobservables_ibfk_3')
    self.__add_fk(RelatedObservable, 'modifier_id', 'relatedobservables_ibfk_4')


    self.__drop_fk(Report, 'reports_ibfk_3')
    self.__drop_fk(Report, 'reports_ibfk_4')
    self.__drop_fk(Report, 'reports_ibfk_5')
    self.__drop_fk(Report, 'reports_ibfk_7')
    self.__drop_fk(Report, 'reports_ibfk_6')
    self.__drop_column(Report, 'originating_group_id')
    self.__drop_column(Report, 'owner_group_id')
    self.__add_index(Report, 'ix_reports_code', 'dbcode')
    self.__add_fk(Report, 'creator_group_id', 'reports_ibfk_3')
    self.__add_fk(Report, 'creator_id', 'reports_ibfk_4')
    self.__add_fk(Report, 'modifier_id', 'reports_ibfk_5')


    self.__drop_fk(Sighting, 'sightings_ibfk_1')
    self.__drop_fk(Sighting, 'sightings_ibfk_2')
    self.__drop_fk(Sighting, 'sightings_ibfk_3')
    self.__drop_fk(Sighting, 'sightings_ibfk_5')
    self.__drop_fk(Sighting, 'sightings_ibfk_4')
    self.__add_column(Sighting, 'tlp_level_id')
    self.__add_column(Sighting, 'timestamp')
    self.__add_column(Sighting, 'reference')
    self.__add_index(Sighting, 'ix_sightings_code', 'dbcode')
    self.__add_fk(Sighting, 'creator_group_id', 'sightings_ibfk_1')
    self.__add_fk(Sighting, 'creator_id', 'sightings_ibfk_2')
    self.__add_fk(Sighting, 'modifier_id', 'sightings_ibfk_3')

    self.__drop_fk(ValidTime, 'validtimepositions_ibfk_2')
    self.__drop_fk(ValidTime, 'validtimepositions_ibfk_3')
    self.__drop_fk(ValidTime, 'validtimepositions_ibfk_4')
    self.__drop_fk(ValidTime, 'validtimepositions_ibfk_6')
    self.__drop_fk(ValidTime, 'validtimepositions_ibfk_5')
    self.__drop_column(ValidTime, 'originating_group_id')
    self.__drop_column(ValidTime, 'owner_group_id')
    self.__add_column(ValidTime, 'tlp_level_id')
    self.__add_index(ValidTime, 'ix_validtimepositions_code', 'dbcode')
    self.__add_fk(ValidTime, 'creator_group_id', 'validtimepositions_ibfk_2')
    self.__add_fk(ValidTime, 'creator_id', 'validtimepositions_ibfk_3')
    self.__add_fk(ValidTime, 'modifier_id', 'validtimepositions_ibfk_4')


    self.__drop_add_pk('rel_event_handling', 'eih_id')
    self.__drop_add_pk('rel_indicator_handling', 'rih_id')
    self.__drop_add_pk('rel_indicator_killchainphase', 'rik_id')
    self.__drop_add_pk('rel_indicator_observable', 'rio_id')
    self.__drop_add_pk('rel_indicator_sightings', 'ris_id')
    self.__drop_add_pk('rel_killchain_killchainphase', 'rkk_id')



    # relation tables


  def close(self):
    self.session.close()


if __name__ == '__main__':


  # check if dump directory is set

  # check if all the files are in the dump directory

  parser = OptionParser()
  parser.add_option('-d', dest='dump_folder', type='string', default=None,
                    help='folder of the dumps')
  (options, args) = parser.parse_args()


  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  config.get_section('Logger')['log'] = False


  migros = Migrator(config)
  migros.create_new_tables()
  migros.altering_tables_phase1()
  migros.merge_data()
  migros.altering_tables_phase2()
  migros.close()

