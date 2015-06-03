# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
import sqlalchemy

from ce1sus.db.brokers.values import ValueBroker
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.common.broker import BrokerBase, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class AttributeBroker(BrokerBase):
    """
    This broker handles all operations on event objects
    """
    def __init__(self, session):
        BrokerBase.__init__(self, session)

    def get_broker_class(self):
        """
        overrides BrokerBase.get_broker_class
        """
        return Attribute

    def look_for_attribute_value(self, attribute_definition, value, operand='=='):
        """
        returns a list of matching values

        :param attribute_definition: attribute definition to use for the lookup
        :type attribute_definition: AttributeDefinition
        :param value: Value to look for
        :type value: String

        :returns: List of clazz
        """
        result = list()
        if attribute_definition is None:
            # search by tables!
            try:
                clazzes = ValueBroker.get_all_classes()
                for clazz in clazzes:
                    temp = self.__look_for_value_by_class(clazz, value, operand, False)
                    result = result + temp

            except BrokerException:
                pass

        else:
            clazz = ValueBroker.get_class_by_attr_def(attribute_definition)
            result = self.__look_for_value_by_attrib_id(clazz,
                                                        value,
                                                        attribute_definition.identifier,
                                                        operand,
                                                        False)
        return result

    def __look_for_value_by_class(self, clazz, value, operand, bypass_validation=False):
        """
        Searches the tables for a value
        """
        if bypass_validation:
            code = 0
        else:
            code = 4
        try:
            if operand == '==':
                return self.session.query(clazz).join(clazz.attribute).filter(clazz.value == value,
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
            if operand == '<':
                return self.session.query(clazz).join(clazz.attribute).filter(clazz.value < value,
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
            if operand == '>':
                return self.session.query(clazz).join(clazz.attribute).filter(clazz.value > value,
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
            if operand == '<=':
                return self.session.query(clazz).join(clazz.attribute).filter(clazz.value <= value,
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
            if operand == '>=':
                return self.session.query(clazz).join(clazz.attribute).filter(clazz.value >= value,
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
            if operand == 'like':
                return self.session.query(clazz).join(clazz.attribute).filter(clazz.value.like('%{0}%'.format(value)),
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def __look_for_value_by_attrib_id(self,
                                      clazz,
                                      value,
                                      attribute_definition_id,
                                      operand='==',
                                      bypass_validation=False):
        """
        Searches the tables for the value using an attribute definition id
        """
        # will return only valid ones
        if bypass_validation:
            code = 0
        else:
            code = 4
        try:
            if operand == '==':
                return self.session.query(clazz).join(clazz.attribute).filter(Attribute.definition_id == attribute_definition_id,
                                                                              clazz.value == value,
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
            if operand == '<':
                return self.session.query(clazz).join(clazz.attribute).filter(Attribute.definition_id == attribute_definition_id,
                                                                              clazz.value < value,
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
            if operand == '>':
                return self.session.query(clazz).join(clazz.attribute).filter(Attribute.definition_id == attribute_definition_id,
                                                                              clazz.value > value,
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
            if operand == '<=':
                return self.session.query(clazz).join(clazz.attribute).filter(Attribute.definition_id == attribute_definition_id,
                                                                              clazz.value <= value,
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
            if operand == '>=':
                return self.session.query(clazz).join(clazz.attribute).filter(Attribute.definition_id == attribute_definition_id,
                                                                              clazz.value >= value,
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
            if operand == 'like':
                return self.session.query(clazz).join(clazz.attribute).filter(Attribute.definition_id == attribute_definition_id,
                                                                              clazz.value.like('%{0}%'.format(value)),
                                                                              Attribute.dbcode.op('&')(code) == code
                                                                              ).all()
        except ValueError:
            return list()
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def get_attriutes_by_class_and_values(self, clazz, search_items):
        try:
            return self.session.query(clazz).filter(clazz.value.in_(search_items)).all()
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)
