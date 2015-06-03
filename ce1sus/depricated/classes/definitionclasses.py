# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 5, 2013
"""
import json
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from ce1sus.db.common.session import BaseClass
from ce1sus.depricated.brokers.basefoo import BASE
from ce1sus.depricated.classes.oldce1susconfig import OldCe1susConfig
from ce1sus.handlers.base import HandlerBase, HandlerException
from ce1sus.helpers.common.objects import get_class
from ce1sus.helpers.common.validator.objectvalidator import ValidationException, ObjectValidator, FailedValidation


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_OBJECT_ATTRIBUTE_DEFINITION = Table(
    'DObj_has_DAttr', getattr(BASE, 'metadata'),
    Column('def_attribute_id', Integer, ForeignKey('DEF_Attributes.def_attribute_id')),
    Column('def_object_id', Integer, ForeignKey('DEF_Objects.def_object_id'))
)


class OldAttributeHandler(BASE):
    """
    Attribute handler class
    """
    def __init__(self):
        pass
    __tablename__ = "AttributeHandlers"
    identifier = Column('AttributeHandler_id', Integer, primary_key=True)
    module_classname = Column('moduleClassName', String)
    description = Column('description', String)
    uuid = Column('uuid', String)
    ce1sus_id = Column('config', Integer, ForeignKey('ce1sus.ce1sus_id'))
    configuration = relationship(OldCe1susConfig)
    __config = None

    def to_dict(self):
        return {'identifier': BaseClass.convert_value(self.identifier),
                'module_classname': BaseClass.convert_value(self.module_classname),
                'description': BaseClass.convert_value(self.description),
                'uuid': BaseClass.convert_value(self.uuid),
                'ce1sus_id': BaseClass.convert_value(self.ce1sus_id)
                }

    @property
    def config(self):
        """
        Returns the global configuration for handlers
        """
        if self.__config is None:
            config_str = getattr(self.configuration, 'value')
            self.__config = json.loads(config_str)
        return self.__config

    @property
    def classname(self):
        """
        Returns the classname
        """
        return unicode(self.module_classname).rsplit('.')[1]

    @property
    def module(self):
        """
        Returns the module
        """
        return unicode(self.module_classname).rsplit('.')[0]

    @property
    def clazz(self):
        clazz = get_class('ce1sus.handlers.attributes.{0}'.format(self.module), self.classname)
        return clazz

    def create_instance(self):
        """
        creates an instantiated object
        """
        # instantiate
        handler = self.clazz()
        # check if handler base is implemented
        if not isinstance(handler, HandlerBase):
            raise HandlerException((u'{0} does not implement '
                                    + 'HandlerBase').format(self.module_classname))
        return handler


class OldObjectDefinition(BASE):
    """This is a container class for the DEF_Objects table."""
    def __init__(self):
        pass
    __tablename__ = "DEF_Objects"
    # table class mapping
    identifier = Column('def_object_id', Integer, primary_key=True)
    name = Column('name', String, nullable=False)
    description = Column('description', String)
    chksum = Column('chksum', String)
    share = Column('sharable', Integer)

    def to_dict(self):
        return {'identifier': BaseClass.convert_value(self.identifier),
                'name': BaseClass.convert_value(self.name),
                'description': BaseClass.convert_value(self.description),
                'share': BaseClass.convert_value(self.share),
                'chksum': BaseClass.convert_value(self.chksum),
                }

    def add_attribute(self, attribute):
        """
        Add an attribute to this object

        :param attribute: Attribute to be added
        :type attribute: OldAttributeDefinition
        """
        errors = not attribute.validate()
        if errors:
            raise ValidationException(u'Attribute to be added is invalid')
        function = getattr(self.attributes, 'append')
        function(attribute)

    def remove_attribute(self, attribute):
        """
        Removes an attribute from this object

        :param obj: Object to be removed
        :type obj: Object
        """
        errors = not attribute.validate()
        if errors:
            raise ValidationException(u'Attribute to be removed is invalid')
        function = getattr(self.attributes, 'remove')
        function(attribute)

    def validate(self):
        """
        Checks if the attributes of the class are valid

        :returns: Boolean
        """
        ObjectValidator.validateAlNum(self,
                                      'name',
                                      withSpaces=True,
                                      withSymbols=True,
                                      minLength=3)
        ObjectValidator.validateAlNum(self,
                                      'description',
                                      withNonPrintableCharacters=True,
                                      withSpaces=True,
                                      minLength=5,
                                      withSymbols=True)
        return ObjectValidator.isObjectValid(self)


class OldAttributeDefinition(BASE):
    """This is a container class for the DEF_ATTRIBUTES table."""
    def __init__(self):
        pass

    tableDefinitions = {0: 'TextValue',
                        1: 'StringValue',
                        2: 'DateValue',
                        3: 'NumberValue'}

    __tablename__ = "DEF_Attributes"
    # table class mapping
    identifier = Column('def_attribute_id', Integer, primary_key=True)
    name = Column('name', String)
    description = Column('description', String)
    regex = Column('regex', String)
    class_index = Column('classIndex', Integer)
    handler_index = Column('handlerIndex', ForeignKey(OldAttributeHandler.identifier))
    attribute_handler = relationship(OldAttributeHandler,

                                     primaryjoin='OldAttributeHandler.identifier==OldAttributeDefinition.handler_index',
                                     lazy='joined',
                                     cascade='all',
                                     order_by="OldAttributeDefinition.name")
    deletable = Column('deletable', Integer)
    # note class relationTable attribute
    share = Column('sharable', Integer)
    relation = Column('relationable', Integer)
    chksum = Column('chksum', String)
    __handler = None

    @property
    def handler(self):
        """
        Returns the instantiatied handler
        """
        if self.__handler is None:
            self.__handler = getattr(self.attribute_handler, 'create_instance')()
        return self.__handler

    @property
    def classname(self):
        """The name for the class used for storing the attribute value"""
        if self.class_index is not None:
            if isinstance(self.class_index, FailedValidation):
                return self.find_classname(self.class_index.value)
            else:
                return self.find_classname(self.class_index)
        else:
            return ''

    @staticmethod
    def find_classname(index):
        """
        returns the table name

        :param index: index of the class name
        :type index: Integer

        :returns: String
        """
        # Test if the index is
        if index < 0 and index >= len(OldAttributeDefinition.tableDefinitions):
            raise Exception(u'Invalid input "{0}"'.format(index))
        return OldAttributeDefinition.tableDefinitions[index]

    @staticmethod
    def find_table_index(name):
        """
        searches for the index for the given table name

        :param index: class name
        :type index: String

        :returns: Integer
        """
        result = None
        for index, tablename in OldAttributeDefinition.tableDefinitions.iteritems():
            if tablename == name:
                result = index
                break
        return result

    @staticmethod
    def get_all_table_names():
        """returns all the table names"""
        result = list()
        for tablename in OldAttributeDefinition.tableDefinitions.itervalues():
            result.append(tablename)
        return result

    @staticmethod
    def get_cb_values(simple=True):
        """ returns the table definitions where the key is the value and value the
        index of the tables.

        Note: Used for displaying the definitions of the tables in combo boxes

        :returns: Dictionary
        """
        result = dict()
        for index, tablename in OldAttributeDefinition.tableDefinitions.iteritems():
            if simple:
                key = tablename.replace('Value', '')
            else:
                key = tablename
            value = index
            result[key] = value
        return result

    def to_dict(self):

        return {'identifier': BaseClass.convert_value(self.identifier),
                'name': BaseClass.convert_value(self.name),
                'description': BaseClass.convert_value(self.description),
                'regex': BaseClass.convert_value(self.regex),
                'class_index': BaseClass.convert_value(self.class_index),
                'handler_index': BaseClass.convert_value(self.handler_index),
                'deletable': BaseClass.convert_value(self.deletable),
                'share': BaseClass.convert_value(self.share),
                'relation': BaseClass.convert_value(self.relation),
                'chksum': BaseClass.convert_value(self.chksum),
                }

    def validate(self):
        """
        Checks if the attributes of the class are valid

        :returns: Boolean
        """
        ObjectValidator.validateAlNum(self, 'name', withSpaces=True,
                                      withSymbols=True,
                                      minLength=3)
        ObjectValidator.validateAlNum(self,
                                      'description',
                                      withNonPrintableCharacters=True,
                                      withSpaces=True,
                                      minLength=3,
                                      withSymbols=True)
        ObjectValidator.validateRegularExpression(self, 'regex')
        ObjectValidator.validateDigits(self, 'class_index')
        ObjectValidator.validateDigits(self, 'handler_index')
        # check if handler is compatible with the class_index
        allowed_classes = self.handler.get_allowed_types()
        if not (self.class_index in allowed_classes):
            class_index = self.class_index
            self.class_index = FailedValidation(class_index,
                                                ('Class is not compatible "{0}".\n'
                                                 'Supported classes are {1}').format(self.attribute_handler.classname,
                                                                                     self.__class_numbers_to_text(allowed_classes))
                                                )

        return ObjectValidator.isObjectValid(self)

    def __class_numbers_to_text(self, class_array):
        result = ''
        for item in class_array:
            if result:
                result = u'{0}, {1}'.format(result, OldAttributeDefinition.find_classname(item))
            else:
                result = u'[{0}'.format(OldAttributeDefinition.find_classname(item))
        return u'{0}]'.format(result)

    def add_object(self, obj):
        """
        Add an object to this attribute$

        :param obj: Object to be added
        :type obj: Object
        """
        function = getattr(self.objects, 'append')
        function(obj)

    def remove_object(self, obj):
        """
        Removes an object from this attribute$

        :param obj: Object to be removed
        :type obj: Object
        """
        function = getattr(self.objects, 'remove')
        function(obj)

    @staticmethod
    def is_class_index_existing(index):
        """Returns true if the class index exsits"""
        return index >= 0 and index <= len(OldAttributeDefinition.tableDefinitions)
