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
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.schema import Table, ForeignKeyConstraint, ForeignKey
from sqlalchemy.types import UnicodeText, Unicode, Integer, BigInteger
import sys
from types import ListType
from uuid import uuid4
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Table, MetaData
from sqlalchemy import update
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.session import make_transient

basePath = dirname(abspath(__file__)) + '/../../'
sys.path.insert(0, basePath)

from ce1sus.db.classes.internal.path import Path
from ce1sus.controllers.events.indicatorcontroller import IndicatorController
from ce1sus.helpers.common.config import Configuration
from ce1sus.helpers.common.objects import get_class
from ce1sus.db.common.session import Base
from ce1sus.db.common.session import SessionManager
from ce1sus.db.classes.ccybox.common.time import CyboxTime
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition, ObservableKeyword
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.information_source import InformationSource, InformationSourceRole
from ce1sus.db.classes.cstix.common.related import RelatedObservable
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.vocabstring import VocabString
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification, MarkingStructure
from ce1sus.db.classes.cstix.indicator import IndicatorType
from ce1sus.db.classes.cstix.indicator.indicator import Indicator, IndicatorType
from ce1sus.db.classes.cstix.indicator.sightings import Sighting
from ce1sus.db.classes.cstix.indicator.valid_time import ValidTime
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.attributes.attribute import Attribute, Condition
from ce1sus.db.classes.internal.attributes.values import NumberValue, TextValue, TimeStampValue, ValueBase
from ce1sus.db.classes.internal.backend.mailtemplate import MailTemplate
from ce1sus.db.classes.internal.backend.types import AttributeType
from ce1sus.db.classes.internal.core import BaseObject
from ce1sus.db.classes.internal.definitions import AttributeDefinition
from ce1sus.db.classes.internal.definitions import ObjectDefinition
from ce1sus.db.classes.internal.event import Event, Comment, EventGroupPermission
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.object import RelatedObject
from ce1sus.db.classes.internal.report import Reference, ReferenceDefinition, ReferenceHandler
from ce1sus.db.classes.internal.report import Report
from ce1sus.db.classes.internal.usrmgt.group import Group, EventPermissions
from ce1sus.db.classes.internal.usrmgt.user import User
from ce1sus.helpers.common.debug import Log
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.classes.internal.definitions import AttributeHandler
from ce1sus.db.classes.internal.attributes.values import DateValue, TextValue, StringValue, TimeStampValue
from ce1sus.db.classes.internal.backend.relation import Relation
from ce1sus.db.classes.cstix.common.vocabstring import VocabString
from ce1sus.db.classes.cstix.extensions.marking.simple_markings import SimpleMarkingStructure
from ce1sus.db.classes.cstix.extensions.test_mechanism.generic_test_mechanism import GenericTestMechanism
from ce1sus.controllers.admin.user import UserController
from datetime import datetime
from uuid import uuid4
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.db.classes.cstix.indicator.sightings import Sighting
from ce1sus.db.classes.internal.backend.config import Ce1susConfig
from ce1sus.helpers.version import Version
from ce1sus.controllers.common.path import PathController
from ce1sus.db.classes.cstix.common.vocabstring import VocabString
from ce1sus.db.classes.cstix.extensions.test_mechanism.snort_test_mechanism import SnortTestMechanism, SnortRule
from ce1sus.db.classes.cstix.extensions.test_mechanism.yara_test_mechanism import YaraTestMechanism
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.controllers.events.attributecontroller import AttributeController
from ce1sus.common.classes.cacheobject import CacheObject

_REL_INDICATOR_SIGHTINGS = Table('rel_indicator_sightings', Base.metadata,
                                 Column('ris_id', BigInteger, primary_key=True, nullable=False, index=True),
                                 Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                 Column('sighting_id', BigInteger, ForeignKey('sightings.sighting_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                 )


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
    self.user_controller = UserController(config, directconnection)
    self.path_controller = PathController(config, directconnection)
    self.observable_controller = ObservableController(config, directconnection)
    self.attribute_controller = AttributeController(config, directconnection)
    self.indicator_controller = IndicatorController(config, directconnection)

  def create_new_tables(self):
    engine = self.engine
    getattr(Base, 'metadata').create_all(engine, checkfirst=True)

  def __get_class_instance(self, column):

    classname = column.type.__class__.__name__

    if 'Type' in classname:
      clazz = get_class('ce1sus.db.classes.internal.corebase', classname)
    else:
      clazz = get_class('sqlalchemy.types', classname)
    if clazz.__name__ == 'Variant':
      clazz = BigInteger

    if hasattr(column.type, 'length') and hasattr(column.type, 'collation'):
      clazz_instance = clazz(column.type.length, collation=column.type.collation)
    elif hasattr(column.type, 'length'):
      clazz_instance = clazz(column.type.length)
    else:
      clazz_instance = clazz()
    return clazz_instance

  def __get_args(self, column):
    args = dict()
    if  column.expression.index:
      args['index'] = column.expression.index
    if  column.expression.nullable:
      args['nullable'] = column.expression.nullable
    if column.expression.unique:
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
    index = args.get('index', None)
    if index is not None:
      del args['index']
    unique = args.get('unique', None)
    if unique is not None:
      del args['unique']
    clazz_instance = self.__get_class_instance(column)
    args['existing_type'] = clazz_instance
    self.op.alter_column(table_name, column.name, **args)
    if index:
      self.op.create_index('ix_{0}_{1}'.format(table_name, column.name), table_name, [column.name], unique=unique)
      

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

  def __drop_add_pk(self, table_name, column_array):
    self.op.drop_constraint(None, table_name, type_='primary')
    self.op.create_primary_key(None, table_name, column_array)

  # drop cols
  def altering_tables_phase2(self):

    for clazz in [Attribute, Indicator, Observable, Object, Reference, Report, Event]:
      self.__drop_column(clazz, 'code')
      self.__drop_column(clazz, 'tlp_level_id')

    self.__drop_column(ObservableComposition, 'code')
    self.__drop_column(Sighting, 'code')

    self.__drop_column(Event, 'originating_group_id')
    self.__drop_column(Event, 'owner_group_id')
    self.__drop_column(Event, 'description')
    self.__drop_column(Event, 'title')

    self.__drop_column(Indicator, 'originating_group_id')
    self.__drop_column(Indicator, 'owner_group_id')
    self.__drop_column(Indicator, 'event_id')
    self.__drop_column(Indicator, 'confidence')
    self.__drop_column(Indicator, 'short_description')
    self.__drop_column(Indicator, 'description')

    self.__drop_column(Observable, 'originating_group_id')
    self.__drop_column(Observable, 'owner_group_id')
    self.__drop_column(Observable, 'parent_id')
    self.__drop_column(Observable, 'version')
    self.__drop_column(Observable, 'event_id')
    self.__drop_column(Observable, 'description')

    self.__drop_column(Sighting, 'originating_group_id')
    self.__drop_column(Sighting, 'owner_group_id')
    self.__drop_column(Sighting, 'confidence')
    self.__drop_column(Sighting, 'description')
  
    self.__drop_table('rel_indicator_sightings')

    self.__drop_column(Object, 'observable_id')
    self.__drop_column(Object, 'parent_id')

  @staticmethod
  def __set_old_fields(clazz):
    classname = clazz.get_classname()
    setattr(clazz, 'originating_group_id', Column('originating_group_id', BigInteger, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True))
    setattr(clazz, 'owner_group_id', Column('owner_group_id', BigInteger, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True))


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

  def __set_old_tlp_new_instance(self, instance):
    setattr(instance, 'tlp_level_id_old', instance.tlp_level_id)
    setattr(instance, 'dbcode_old', instance.dbcode)

  def __create_information_source(self, group_id, role, instance, parent_attr='parent'):
    informationsource = InformationSource()
    informationsource.uuid = uuid4()
    informationsource.namespace = 'ce1sus'
    setattr(informationsource, parent_attr, instance)
    self.__set_extendedlogging(informationsource, instance)
    self.session.get_session().add(informationsource)
    self.session.get_session().flush()
    self.__set_path(informationsource, parent_tlp=instance, parent=instance)
    self.__set_old_tlp_new_instance(informationsource)

    informationsource.identity = Identity()
    informationsource.identity.uuid = uuid4()
    informationsource.identity.parent = informationsource
    self.__set_extendedlogging(informationsource.identity, instance)
    self.session.get_session().add(informationsource.identity)
    self.session.get_session().flush()
    self.__set_path(informationsource.identity, parent=informationsource, parent_tlp=informationsource)
    

    group = self.session.get_session().query(Group).filter(Group.identifier == group_id).one()
    
    informationsource.identity.name = group.name
    informationsource.identity.namespace = 'ce1sus'

    isrole = InformationSourceRole()
    isrole.uuid = uuid4()
    isrole.parent = informationsource
    isrole.role = role
    self.__set_extendedlogging(isrole, informationsource)
    self.session.get_session().add(isrole)
    self.session.get_session().flush()
    self.__set_path(isrole, parent=informationsource, parent_tlp=informationsource)
    informationsource.roles.append(isrole)

    time = CyboxTime()
    time.uuid = uuid4()
    time.parent = informationsource
    self.__set_extendedlogging(time, instance)
    self.session.get_session().add(time)
    self.session.get_session().flush()
    self.__set_path(time, parent=informationsource, parent_tlp=informationsource)
    self.__set_old_tlp_new_instance(time)

    time.produced_time = DateTimeWithPrecision()
    time.produced_time.uuid = uuid4()
    time.produced_time.value = instance.created_at
    time.produced_time.cyboxtime_produced = time
    informationsource.time = time
    self.__set_extendedlogging(time.produced_time, instance)
    self.session.get_session().add(time)
    self.session.get_session().flush()
    self.__set_path(time.produced_time, parent=time, parent_tlp=time)
    return informationsource
  
  def __create_description(self, value, parent, parent_attr):
    desription = StructuredText()
    desription.uuid = uuid4()
    desription.value = value
    desription.namespace = 'ce1sus'
    setattr(desription, parent_attr, parent)
    self.__set_extendedlogging(desription, parent)
    self.session.get_session().add(desription)
    self.session.get_session().flush()
    self.__set_path(desription, parent=parent, parent_tlp=parent)

  def __merge_observables(self, all, observables, events):
    for item in all:
      self.__merge_observable(item, observables, events)
    self.session.get_session().flush()

  def __merge_observable(self, item, observables, events):
    print 'Merging Observable {0}'.format(item.identifier)
    item.namespace = 'ce1sus'
    if item.event_id:
      event = events[item.event_id]
      item.event = event

    if item.path is None:

      self.__set_path(item)
      self.session.get_session().merge(item)
      self.session.get_session().flush()

      if item.foo:
        description = self.__create_description(item.foo, item, 'observable_description')

      if item.observable_composition:
        print 'Merging ObservableComposition {0}'.format(item.observable_composition.identifier)
        item.namespace = 'ce1sus'
        self.__set_extendedlogging(item.observable_composition, item)
        self.__set_path(item.observable_composition, parent=item, parent_tlp=item)
        self.session.get_session().merge(item.observable_composition)
        self.session.get_session().flush()
        self.__merge_observables(item.observable_composition.observables, observables, events)
    else:
      print 'Merging Observable {0} was seen'.format(item.identifier)
      item.parent.observables.remove(item)

    self.session.get_session().flush()
    observables[item.identifier] = item

  def __merge_object_recursive(self, obj, observables, parent=None):
    self.__merge_object(obj, observables, parent=parent)
    # merge RelatedObject
    for rel_obj in obj.related_objects:
      print 'Merging ReleatedObject {0}'.format(rel_obj.identifier)
      self.__set_extendedlogging(rel_obj, obj)
      self.__set_path(rel_obj, parent=obj, parent_tlp=obj)
      self.session.get_session().merge(rel_obj)
      self.session.get_session().flush()
      self.__merge_object_recursive(rel_obj.object, observables, parent=obj)

  def __merge_object(self, obj, observables, parent=None):
    try:
      print 'Merging Object {0}'.format(obj.identifier)
      obj.namespace = 'ce1sus'

      if obj.parent_id:
        if observables:
          observable = observables.get(obj.parent_id, None)
          if observable is None:
            raise NoResultFound()
        else:
          observable = self.session.get_session().query(Observable).filter(Observable.identifier == obj.parent_id).one()
        obj.observable = observable
        parent_inst = observable
      else:
        parent_inst = parent

      self.__set_path(obj, parent=parent_inst)
      self.session.get_session().merge(obj)
      self.session.get_session().flush()
      for attribute in obj.attributes:
        print 'Merging Attribute {0}'.format(attribute.identifier)
        self.__set_path(attribute, parent=obj)
        try:
          self.session.get_session().flush()
        except OperationalError as error:
          print 'Error on attribute {0} error: {1}'.format(attribute.uuid, error)

      self.session.get_session().merge(obj)
      self.session.get_session().flush()
    except NoResultFound:
      # in existing observable
      pass

  def __merge_report(self, item):
    self.__set_path(item, recursive=True)
    print 'Merging Report with id {0}'.format(item.identifier)
    if item.description_old:
      description = self.__create_description(item.description_old, item, 'report_description')
    if item.short_description_old:
      description = self.__create_description(item.short_description_old, item, 'report_short_description')

    self.session.get_session().merge(item)
    
  def __merge_report_recursive(self, item):
    self.__merge_report(item)
    for rel_rep in item.related_reports:
      self.__merge_report_recursive(rel_rep)
  
  def merge_data(self):
    
    user_uuid = config.get('ce1sus', 'maintenaceuseruuid', None)
    if None:
      raise Exception('maintenaceuseruuid was not defined in config')
    try:
      user = self.user_controller.get_user_by_uuid(user_uuid)
    except ControllerNothingFoundException:
      raise Exception('Cannot find maintenance user with uuid {0}'.format(user_uuid))
    except ControllerException as error:
      raise Exception(error)



    all = self.session.get_session().query(Condition).all()
    for item in all:
      print 'Merging Condition {0}'.format(item.identifier)
      item.created_at = datetime.utcnow()
      item.modified_on = datetime.utcnow()
      item.modifier_id = user.identifier
      item.creator_id = user.identifier
      self.session.get_session().merge(item)
    self.session.get_session().flush()


    setattr(StructuredText, '_PARENTS', ['stix_header_description', 'stix_header_short_description', 'information_source_description', 'indicator_description', 'indicator_short_description', 'report_description', 'report_short_description', 'observable_description', 'sighting_description'])
    setattr(InformationSource, '_PARENTS', ['stix_header', 'indicator_producer', 'sighting', 'information_source'])
    setattr(Event, 'foo', Column('description', UnicodeText(collation='utf8_unicode_ci')))
    setattr(Event, 'title', Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=False))
    Migrator.__set_old_fields(Event)
    self.__set_dbcode_tlp(Event)
    
    events = dict()
    observables = dict()

    all = self.session.get_session().query(Event).all()
    for item in all:

      self.__set_path(item)
      if item.foo:
        print 'Merging Event {0}'.format(item.identifier)
        item.version = '1.0.0'
        item.namespace = 'ce1sus'

        item.stix_header = STIXHeader()
        item.stix_header.uuid = uuid4()
        item.stix_header.title = item.title
        item.stix_header.event = item
        self.__set_extendedlogging(item.stix_header, item)
        self.session.get_session().add(item.stix_header)
        self.session.get_session().flush()
        self.__set_path(item.stix_header, parent=item, parent_tlp=item)
        self.__set_old_tlp_new_instance(item.stix_header)


        is_ = self.__create_information_source(item.originating_group_id, 'Initial Author', item.stix_header)
        item.stix_header.information_source = is_

        # handling not used yet
        description = self.__create_description(item.foo, item.stix_header, 'stix_header_description')

      self.session.get_session().merge(item)
      self.session.get_session().flush()
      events[item.identifier] = item

    self.session.get_session().flush()
    
    setattr(InformationSource, '_PARENTS', ['indicator_producer', 'sighting', 'information_source'])

    setattr(Indicator, '_PARENTS', ['event'])
    Migrator.__set_old_fields(Indicator)
    setattr(Indicator, 'foo', Column('description', UnicodeText(collation='utf8_unicode_ci')))
    setattr(Indicator, 'bar', Column('short_description', Unicode(255, collation='utf8_unicode_ci')))
    setattr(Indicator, 'event_id', Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True))
    setattr(Indicator, 'sig', relationship('Sighting', secondary='rel_indicator_sightings'))
    self.__set_dbcode_tlp(Indicator)

    setattr(Sighting, 'foo', Column('confidence', Unicode(5, collation='utf8_unicode_ci'), default=u'HIGH', nullable=False))
    setattr(Sighting, 'bar', Column('description', UnicodeText(collation='utf8_unicode_ci')))
    self.__set_old_fields(Sighting)
    setattr(Sighting, 'dbcode_old', Column('code', Integer, nullable=False, default=0, index=True))

    setattr(Observable, 'foo', Column('description', UnicodeText(collation='utf8_unicode_ci')))
    setattr(Observable, 'event_id', Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True))
    self.__set_old_fields(Observable)
    self.__set_dbcode_tlp(Observable)


    all = self.session.get_session().query(Observable).options(joinedload(Observable.observable_composition), joinedload(Observable.object)).filter(Observable.event_id != None).all()
    self.__merge_observables(all, observables, events)

    setattr(Confidence, '_PARENTS', ['sighting'])
    all = self.session.get_session().query(Indicator).options(joinedload(Indicator.sightings), joinedload(Indicator.sightings), joinedload(Indicator.observables)).all()
    for item in all:
      setattr(StructuredText, '_PARENTS', [ 'indicator_description', 'indicator_short_description', 'sighting_description', 'information_source_description', 'report_description', 'report_short_description', 'observable_description'])

      event = events[item.event_id]
      item.event = event
      print 'Merging Indicator {0}'.format(item.identifier)
      item.namespace = 'ce1sus'
      item.version = '1.0.0'
      item.timestamp = item.created_at
      self.__set_path(item)

      if item.foo:
        description = self.__create_description(item.foo, item, 'indicator_description')

      short_description = None
      if item.bar:
        short_description = self.__create_description(item.bar, item, 'indicator_short_description')

      is_ = self.__create_information_source(item.originating_group_id, 'Initial Author', item, 'indicator_producer')
      item.producer = is_

      setattr(StructuredText, '_PARENTS', ['sighting_description', 'information_source_description', 'report_description', 'report_short_description', 'observable_description'])
      for sig in item.sig:
        sig.indicator = item
        print 'Merging Sighting {0}'.format(item.identifier)
        sighting = self.session.get_session().query(Sighting).filter(Sighting.identifier == sig.identifier).one()
        sig.timestamp = sig.modified_on
        setattr(sig, 'tlp_level_id_old', item.tlp_level_id_old)
        self.__set_path(sig, parent=item, parent_tlp=item)

        is_ = self.__create_information_source(sig.originating_group_id, 'Initial Author', sig, 'sighting')
        sig.source = is_

        if sig.foo:
          confidence = Confidence()
          confidence.uuid = uuid4()
          confidence.value = sig.foo
          confidence.sighting = sig
          self.__set_extendedlogging(confidence, sig)
          self.session.get_session().add(confidence)
          self.session.get_session().flush()
          self.__set_path(confidence, parent=sig, parent_tlp=sig)

          sig.confidence = confidence

        if sig.bar:
          description = self.__create_description(sig.bar, item, 'sighting_description')

        is_ = self.__create_information_source(item.creator_group_id, 'Initial Author', sig)

        self.session.get_session().merge(sig)
      self.session.get_session().merge(item)
      self.session.get_session().flush()
      self.__merge_observables(item.observables, observables, events)
    self.session.get_session().flush()


    self.session.get_session().commit()
    return observables, events

  def merge_remaining(self, observables, events):

    # remove observable orphans

    all = self.session.get_session().query(Observable).options(joinedload(Observable.observable_composition), joinedload(Observable.description), joinedload(Observable.object)).filter(Observable.path == None).all()
    for item in all:
      self.observable_controller.remove_observable(item, CacheObject(), False, False)
    self.session.get_session().flush()
    # remove composition orphans
    all = self.session.get_session().query(ObservableComposition).options(joinedload(ObservableComposition.observables)).filter(ObservableComposition.path == None).all()
    for item in all:
      self.observable_controller.remove_observable_composition(item, CacheObject(), False, False)
    self.session.get_session().flush()

    self.__set_dbcode_tlp(Object)

    self.__set_dbcode_tlp(Attribute)
    setattr(Object, 'parent_id', Column('parent_id', BigInteger, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), index=True))


    all = self.session.get_session().query(Object).options(joinedload(Object.observable), joinedload(Object.attributes)).filter(Object.parent_id != None).all()
    for item in all:
      self.__merge_object_recursive(item, observables)

    setattr(Report,
            'description_old',
            Column('description',
                   UnicodeTextType()
                   )
            )
    setattr(Report,
            'short_description_old',
            Column('short_description',
                   UnicodeTextType()
                   )
            )
    setattr(StructuredText, '_PARENTS', [ 'report_description', 'report_short_description', 'observable_description'])
    self.__set_dbcode_tlp(Report)
    all = self.session.get_session().query(Report).options(joinedload(Report.event)).filter(Report.parent_report_id == None).all()
    for item in all:
      self.__merge_report_recursive(item)
    self.session.get_session().flush()

    self.__set_dbcode_tlp(Reference)
    all = self.session.get_session().query(Reference).options(joinedload(Reference.report)).all()
    for item in all:
      self.__set_path(item)
      self.session.get_session().merge(item)
    self.session.get_session().flush()

    self.session.get_session().commit()

  def altering_tables_phase1(self):

    self.__change_column(AttributeDefinition, 'description')
    self.__change_column(AttributeDefinition, 'regex')
    self.__add_column(AttributeDefinition, 'case_insensitive')

    self.__change_column(AttributeHandler, 'description')

    self.__drop_fk(Attribute, 'attributes_ibfk_4')
    self.__drop_fk(Attribute, 'attributes_ibfk_5')
    self.__drop_fk(Attribute, 'attributes_ibfk_6')
    self.__drop_fk(Attribute, 'attributes_ibfk_7')
    self.__drop_fk(Attribute, 'attributes_ibfk_9')
    self.__drop_fk(Attribute, 'attributes_ibfk_8')
    self.__drop_column(Attribute, 'originating_group_id')
    self.__drop_column(Attribute, 'owner_group_id')
    self.__drop_column(Attribute, 'parent_id')
    self.__drop_column(Attribute, 'description')
    self.__add_fk(Attribute, 'creator_group_id', 'attributes_ibfk_4')
    self.__add_fk(Attribute, 'creator_id', 'attributes_ibfk_5')
    self.__add_fk(Attribute, 'modifier_id', 'attributes_ibfk_6')

    self.__change_column(AttributeType, 'description')

    self.__drop_fk(Comment, 'comments_ibfk_2')
    self.__drop_fk(Comment, 'comments_ibfk_3')
    self.__drop_fk(Comment, 'comments_ibfk_4')
    self.__drop_fk(Comment, 'comments_ibfk_5')
    self.__drop_fk(Comment, 'comments_ibfk_6')
    self.__drop_column(Comment, 'originating_group_id')
    self.__drop_column(Comment, 'owner_group_id')
    self.__change_column(Comment, 'comment')
    self.__add_fk(Comment, 'creator_group_id', 'comments_ibfk_2')
    self.__add_fk(Comment, 'creator_id', 'comments_ibfk_3')
    self.__add_fk(Comment, 'modifier_id', 'comments_ibfk_4')
    
    self.__change_column(Condition, 'value')
    self.__change_column(Condition, 'description')
    self.__add_column(Condition, 'created_at')
    self.__add_column(Condition, 'modified_on')
    self.__add_column(Condition, 'creator_id')
    self.__add_column(Condition, 'modifier_id')
    self.__add_fk(Condition, 'creator_id', 'conditions_ibfk_1')
    self.__add_fk(Condition, 'modifier_id', 'conditions_ibfk_2')

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
    self.__add_column(Event, 'version_db')
    self.__add_column(Event, 'idref')
    self.__add_column(Event, 'namespace')

    self.__add_fk(Event, 'creator_group_id', 'events_ibfk_1')
    self.__add_fk(Event, 'creator_id', 'events_ibfk_2')
    self.__add_fk(Event, 'modifier_id', 'events_ibfk_3')


    self.__change_column(Group, 'name')
    self.__change_column(Group, 'description')
    self.__change_column(Group, 'email')
    self.__change_column(Group, 'gpg_key')
    self.__change_column(Group, 'send_usermails')

    self.__drop_fk(Indicator, 'indicators_ibfk_1')
    self.__drop_fk(Indicator, 'indicators_ibfk_2')
    self.__drop_fk(Indicator, 'indicators_ibfk_3')
    self.__drop_fk(Indicator, 'indicators_ibfk_4')
    self.__drop_fk(Indicator, 'indicators_ibfk_6')
    self.__drop_fk(Indicator, 'indicators_ibfk_5')

    self.__change_column(Indicator, 'version_db')
    self.__change_column(Indicator, 'operator')
    self.__add_column(Indicator, 'namespace')
    self.__add_column(Indicator, 'timestamp')
    self.__add_column(Indicator, 'alternative_id')
    self.__add_column(Indicator, 'negate')
    self.__add_column(Indicator, 'idref')
    self.__add_fk(Indicator, 'creator_group_id', 'indicators_ibfk_1')
    self.__add_fk(Indicator, 'creator_id', 'indicators_ibfk_2')
    self.__add_fk(Indicator, 'modifier_id', 'indicators_ibfk_3')


    self.__change_column(IndicatorType, 'type_id')
    self.__add_column(IndicatorType, 'created_at')
    self.__add_column(IndicatorType, 'modified_on')
    self.__add_column(IndicatorType, 'creator_group_id')
    self.__add_column(IndicatorType, 'creator_id')
    self.__add_column(IndicatorType, 'modifier_id')
    self.__add_fk(IndicatorType, 'creator_group_id', 'indicatortypes_ibfk_2')
    self.__add_fk(IndicatorType, 'creator_id', 'indicatortypes_ibfk_3')
    self.__add_fk(IndicatorType, 'modifier_id', 'indicatortypes_ibfk_4')


    self.__change_column(MailTemplate, 'name')
    self.__change_column(MailTemplate, 'body')
    self.__change_column(MailTemplate, 'subject')

    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_1')
    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_2')
    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_3')
    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_4')
    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_6')
    self.__drop_fk(MarkingStructure, 'markingstructures_ibfk_5')
    self.__drop_column(MarkingStructure, 'originating_group_id')
    self.__drop_column(MarkingStructure, 'owner_group_id')
    self.__drop_column(MarkingStructure, 'value')
    self.__drop_column(MarkingStructure, 'type_id')
    self.__drop_column(MarkingStructure, 'marking_id')
    self.__change_column(MarkingStructure, 'marking_model_name')
    self.__change_column(MarkingStructure, 'marking_model_ref')
    self.__add_column(MarkingStructure, 'namespace')
    self.__add_column(MarkingStructure, 'type')
    self.__add_column(MarkingStructure, 'markingspecification_id')
    self.__add_fk(MarkingStructure, 'creator_group_id', 'markingstructures_ibfk_2')
    self.__add_fk(MarkingStructure, 'creator_id', 'markingstructures_ibfk_3')
    self.__add_fk(MarkingStructure, 'modifier_id', 'markingstructures_ibfk_4')
    self.__add_fk(MarkingStructure, 'markingspecification_id', 'markingstructures_ibfk_1')

    self.__change_column(ObjectDefinition, 'description')

    self.__drop_fk(Object, 'objects_ibfk_2')
    self.__drop_fk(Object, 'objects_ibfk_3')
    self.__drop_fk(Object, 'objects_ibfk_4')
    self.__drop_fk(Object, 'objects_ibfk_5')
    self.__drop_fk(Object, 'objects_ibfk_6')
    self.__drop_fk(Object, 'objects_ibfk_8')
    self.__drop_fk(Object, 'objects_ibfk_7')
    self.__add_column(Object, 'parent_id')
    self.__add_fk(Object, 'parent_id', 'objects_ibfk_5')
    self.__drop_column(Object, 'originating_group_id')
    self.__drop_column(Object, 'owner_group_id')

    self.__add_column(Object, 'idref')
    self.__add_column(Object, 'namespace')
    self.__add_fk(Object, 'creator_group_id', 'objects_ibfk_2')
    self.__add_fk(Object, 'creator_id', 'objects_ibfk_3')
    self.__add_fk(Object, 'modifier_id', 'objects_ibfk_4')

    self.__change_column(ObservableComposition, 'operator')
    self.__add_column(ObservableComposition, 'created_at')
    self.__add_column(ObservableComposition, 'modified_on')
    self.__add_column(ObservableComposition, 'creator_group_id')
    self.__add_column(ObservableComposition, 'creator_id')
    self.__add_column(ObservableComposition, 'modifier_id')
    self.__add_fk(ObservableComposition, 'creator_group_id', 'observablecompositions_ibfk_2')
    self.__add_fk(ObservableComposition, 'creator_id', 'observablecompositions_ibfk_3')
    self.__add_fk(ObservableComposition, 'modifier_id', 'observablecompositions_ibfk_4')

    # self.__change_column(ObservableKeyword, 'uuid')
    self.__add_column(ObservableKeyword, 'created_at')
    self.__add_column(ObservableKeyword, 'modified_on')
    self.__add_column(ObservableKeyword, 'creator_group_id')
    self.__add_column(ObservableKeyword, 'creator_id')
    self.__add_column(ObservableKeyword, 'modifier_id')
    self.__add_fk(ObservableKeyword, 'creator_group_id', 'observablekeywords_ibfk_2')
    self.__add_fk(ObservableKeyword, 'creator_id', 'observablekeywords_ibfk_3')
    self.__add_fk(ObservableKeyword, 'modifier_id', 'observablekeywords_ibfk_4')


    self.__drop_fk(Observable, 'observables_ibfk_2')
    self.__drop_fk(Observable, 'observables_ibfk_3')
    self.__drop_fk(Observable, 'observables_ibfk_4')
    self.__drop_fk(Observable, 'observables_ibfk_5')
    self.__drop_fk(Observable, 'observables_ibfk_7')
    self.__drop_fk(Observable, 'observables_ibfk_6')
    self.__drop_fk(Observable, 'observables_ibfk_1')

    self.__add_column(Observable, 'namespace')
    self.__add_column(Observable, 'idref')
    self.__add_column(Observable, 'sighting_count')
    self.__add_fk(Observable, 'creator_group_id', 'observables_ibfk_1')
    self.__add_fk(Observable, 'creator_id', 'observables_ibfk_2')
    self.__add_fk(Observable, 'modifier_id', 'observables_ibfk_3')

    self.__change_column(ReferenceDefinition, 'description')
    self.__change_column(ReferenceDefinition, 'regex')

    self.__change_column(ReferenceHandler, 'description')

    self.__drop_fk(Reference, 'references_ibfk_4')
    self.__drop_fk(Reference, 'references_ibfk_5')
    self.__drop_fk(Reference, 'references_ibfk_6')
    self.__drop_fk(Reference, 'references_ibfk_8')
    self.__drop_fk(Reference, 'references_ibfk_7')
    self.__drop_column(Reference, 'originating_group_id')
    self.__drop_column(Reference, 'owner_group_id')
    self.__change_column(Reference, 'value')
    self.__add_fk(Reference, 'creator_group_id', 'references_ibfk_4')
    self.__add_fk(Reference, 'creator_id', 'references_ibfk_5')
    self.__add_fk(Reference, 'modifier_id', 'references_ibfk_6')

    self.__drop_column(RelatedObject, 'relation')
    self.__add_column(RelatedObject, 'created_at')
    self.__add_column(RelatedObject, 'modified_on')
    self.__add_column(RelatedObject, 'relationship_id')
    self.__add_column(RelatedObject, 'idref')
    self.__add_column(RelatedObject, 'creator_group_id')
    self.__add_column(RelatedObject, 'creator_id')
    self.__add_column(RelatedObject, 'modifier_id')
    self.__add_fk(RelatedObject, 'creator_group_id', 'relatedobjects_ibfk_3')
    self.__add_fk(RelatedObject, 'creator_id', 'relatedobjects_ibfk_4')
    self.__add_fk(RelatedObject, 'modifier_id', 'relatedobjects_ibfk_5')


    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_1')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_2')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_3')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_4')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_5')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_6')
    self.__drop_fk(RelatedObservable, 'relatedobservables_ibfk_7')
    self.__drop_column(RelatedObservable, 'originating_group_id')
    self.__drop_column(RelatedObservable, 'owner_group_id')
    self.__drop_column(RelatedObservable, 'confidence')
    self.__drop_column(RelatedObservable, 'relation')
    self.__drop_column(RelatedObservable, 'parent_id')
    self.__add_column(RelatedObservable, 'relationship')
    self.__add_fk(RelatedObservable, 'creator_group_id', 'relatedobservables_ibfk_2')
    self.__add_fk(RelatedObservable, 'creator_id', 'relatedobservables_ibfk_3')
    self.__add_fk(RelatedObservable, 'modifier_id', 'relatedobservables_ibfk_4')
    self.__add_fk(RelatedObservable, 'child_id', 'relatedobservables_ibfk_1')


    self.__drop_fk(Report, 'reports_ibfk_3')
    self.__drop_fk(Report, 'reports_ibfk_4')
    self.__drop_fk(Report, 'reports_ibfk_5')
    self.__drop_fk(Report, 'reports_ibfk_7')
    self.__drop_fk(Report, 'reports_ibfk_6')
    self.__drop_column(Report, 'originating_group_id')
    self.__drop_column(Report, 'owner_group_id')

    self.__add_fk(Report, 'creator_group_id', 'reports_ibfk_3')
    self.__add_fk(Report, 'creator_id', 'reports_ibfk_4')
    self.__add_fk(Report, 'modifier_id', 'reports_ibfk_5')


    self.__drop_fk(Sighting, 'sightings_ibfk_1')
    self.__drop_fk(Sighting, 'sightings_ibfk_3')
    self.__drop_fk(Sighting, 'sightings_ibfk_5')
    self.__drop_fk(Sighting, 'sightings_ibfk_4')

    self.__change_column(Sighting, 'timestamp_precision')
    self.__add_column(Sighting, 'timestamp')
    self.__add_column(Sighting, 'reference')
    self.__add_column(Sighting, 'indicator_id')
    self.__add_fk(Sighting, 'indicator_id', 'sightings_ibfk_1')
    self.__add_fk(Sighting, 'creator_id', 'sightings_ibfk_3')
    self.__add_fk(Sighting, 'modifier_id', 'sightings_ibfk_4')


    self.__change_column(TextValue, 'value')


    self.__change_column(User, 'name')
    self.__change_column(User, 'sirname')
    self.__change_column(User, 'username')
    self.__change_column(User, 'password')
    self.__change_column(User, 'email')
    self.__change_column(User, 'gpg_key')
    self.__change_column(User, 'activation_str')




    self.__drop_fk(ValidTime, 'validtimepositions_ibfk_2')
    self.__drop_fk(ValidTime, 'validtimepositions_ibfk_3')
    self.__drop_fk(ValidTime, 'validtimepositions_ibfk_4')
    self.__drop_fk(ValidTime, 'validtimepositions_ibfk_6')
    self.__drop_fk(ValidTime, 'validtimepositions_ibfk_5')
    self.__drop_column(ValidTime, 'originating_group_id')
    self.__drop_column(ValidTime, 'owner_group_id')
    self.__add_fk(ValidTime, 'creator_group_id', 'validtimepositions_ibfk_2')
    self.__add_fk(ValidTime, 'creator_id', 'validtimepositions_ibfk_3')
    self.__add_fk(ValidTime, 'modifier_id', 'validtimepositions_ibfk_4')

    self.__drop_add_pk('rel_indicator_observable', ['indicator_id', 'observable_id'])
    self.op.drop_column('rel_indicator_observable', 'rio_id')
    self.__drop_add_pk('rel_observable_composition', ['observablecomposition_id', 'child_id'])
    self.op.drop_column('rel_observable_composition', 'roc_id')






    self.op.add_column('rel_indicator_handling', Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id'), nullable=False))
    self.op.drop_constraint('rel_indicator_handling_ibfk_2', 'rel_indicator_handling', type_='foreignkey')
    self.op.drop_column('rel_indicator_handling', 'marking_id')
    self.__drop_add_pk('rel_indicator_handling', ['indicator_id', 'markingspecification_id'])
    self.op.drop_column('rel_indicator_handling', 'rih_id')
    self.op.create_index('ix_rel_indicator_handling_markingspecification_id', 'rel_indicator_handling', ['markingspecification_id'])




    self.__drop_table('rel_ttps_killchains')
    self.__drop_table('rel_killchain_killchainphase')

    self.__drop_table('rel_indicator_killchainphase')
    self.__drop_table('rel_event_handling')
    self.__drop_table('ttpss')
    self.__drop_table('markings')
    self.__drop_table('killchains')
    self.__drop_table('killchainphases')


  def change_value_tables_phase1(self):
    # relation tables
    for clazz in [StringValue, TextValue, DateValue, TimeStampValue, NumberValue]:
      try:
        self.__drop_column(clazz, 'identifier')
      except Exception:
        pass
      self.__add_column(clazz, 'identifier')

      self.__drop_fk(clazz, '{0}_ibfk_1'.format(clazz.get_table_name()))
      self.__drop_fk(clazz, '{0}_ibfk_2'.format(clazz.get_table_name()))
      self.__drop_fk(clazz, '{0}_ibfk_3'.format(clazz.get_table_name()))

      self.__add_fk(clazz, 'identifier', '{0}_ibfk_1'.format(clazz.get_table_name()))

      self.__drop_column(clazz, 'uuid')
      # drop unique constraint
      self.op.alter_column(clazz.get_table_name(), 'attribute_id', nullable=True, existing_type=BigInteger)
      self.op.alter_column(clazz.get_table_name(), 'event_id', nullable=True, existing_type=BigInteger)
      self.op.alter_column(clazz.get_table_name(), 'attributetype_id', nullable=True, existing_type=BigInteger)



  def change_value_tables_phase2(self):
    for clazz in [StringValue, TextValue, DateValue, TimeStampValue, NumberValue]:
      table_name = clazz.get_table_name()
      self.__drop_fk(clazz, '{0}_ibfk_1'.format(clazz.get_table_name()))
      try:
        self.__drop_add_pk(table_name, ['identifier'])
      except OperationalError:
        self.op.create_primary_key(None, table_name, ['identifier'])

      self.__add_fk(clazz, 'identifier', '{0}_ibfk_1'.format(clazz.get_table_name()))
      self.__drop_column(clazz, '{0}_id'.format(clazz.get_classname().lower()))
      self.__drop_column(clazz, 'attribute_id')
      self.__drop_column(clazz, 'event_id')
      self.__drop_column(clazz, 'attributetype_id')

    self.__drop_column(Report, 'description')
    self.__drop_column(Report, 'short_description')

  def __set_dbcode_tlp(self, clazz):
    setattr(clazz, 'tlp_level_id_old', Column('tlp_level_id', Integer, default=3, nullable=False))
    setattr(clazz, 'dbcode_old', Column('code', Integer, nullable=False, default=0, index=True))

  def __set_path(self, instance, parent=None, parent_tlp=None, recursive=False):
    instance.path = Path()
    instance.path.path = ''
    if parent_tlp:
      instance.path.item_tlp_level_id = parent_tlp.tlp_level_id_old
      instance.path.item_dbcode = parent_tlp.dbcode_old
    else:
      instance.path.item_tlp_level_id = instance.tlp_level_id_old
      instance.path.item_dbcode = instance.dbcode_old

    path = self.path_controller.make_path(instance, parent=parent, recursive=recursive)
    instance.path.path = path.path
    instance.path.dbcode = path.dbcode
    instance.path.tlp_level_id = path.tlp_level_id
    instance.path.event = path.event
    instance.path.event_id = path.event_id

  def merge_value_data(self):

    all = self.session.get_session().query(Object).filter(Object.path == None).all()
    for item in all:
      self.observable_controller.remove_object(item, CacheObject(), False)
    self.session.get_session().flush()

    meta = MetaData(bind=self.engine, reflect=True)
    for clazz in [StringValue, TextValue, DateValue, TimeStampValue, NumberValue]:

      table = meta.tables[
                          clazz.get_table_name()
                          ]
      
      all = list(self.engine.execute(table.select(table.c.identifier == None)))

      for item in all:
        value = item.value
        attribute_id = item.attribute_id
        event_id = item.event_id
        value_type_id = item.attributetype_id
        id_ = getattr(item, '{0}_id'.format(clazz.get_classname().lower()))
        print 'Merging Attribute {1}Value with id {0}'.format(id_, clazz.get_classname())
        # check if attribute still exists
        if self.session.get_session().query(Attribute).filter(Attribute.identifier == attribute_id).count() == 1:
          new_value_base = clazz()
          new_value_base.uuid = uuid4()
          new_value_base.attribute_id = attribute_id
          new_value_base.event_id = event_id
          new_value_base.value_type_id = value_type_id
          new_value_base.type = clazz.get_classname().lower()
          new_value_base.value = value
          self.session.get_session().add(new_value_base)

      self.session.get_session().flush()
      self.session.get_session().query(clazz).filter(clazz.identifier == None).delete(synchronize_session='fetch')
      self.session.get_session().flush()

    self.session.get_session().commit()



  def pre_steps(self):
    # check if db exits in table
    try:
      dbversion = self.session.get_session().query(Ce1susConfig).filter(Ce1susConfig.key == 'db_version').one()
      if dbversion.value:
        print dbversion.value
        version = Version(dbversion.value)
        if version.compare('0.11.1') < 0:
          raise Exception('Migration already ran')
    except MultipleResultsFound as error:
      raise Exception(error)
    except NoResultFound:
      dbversion = Ce1susConfig()
      dbversion.key = 'db_version'
      dbversion.value = '0.11.0'
      dbversion.uuid = '08e63b80-4ffb-11e5-b970-0800200c9a66'
      self.session.get_session().add(dbversion)
      self.session.get_session().commit()

  def post_steps(self):
    paths = self.session.get_session().query(Path).all()

    for path in paths:
      path.event = path.root
      self.session.get_session().merge(path)
    self.session.get_session().flush()

    """
    # insert or update db key
    dbversion = self.session.get_session().query(Ce1susConfig).filter(Ce1susConfig.key == 'db_version').one()
    dbversion.value = '0.11.1'
    self.session.get_session().merge(dbversion)

    """
    self.session.get_session().commit()

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
  # migros.create_new_tables()
  # migros.pre_steps()
  # migros.altering_tables_phase1()
  # migros.change_value_tables_phase1()
  # observables, events = None, None
  # observables, events = migros.merge_data()
  # migros.merge_remaining(observables, events)
  # migros.merge_value_data()
  # migros.change_value_tables_phase2()
  # migros.altering_tables_phase2()
  migros.post_steps()
  migros.close()

