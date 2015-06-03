# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 9, 2015
"""
import sqlalchemy.exc

from ce1sus.db.classes.report import Report, Reference
from ce1sus.db.common.broker import BrokerBase, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ReportBroker(BrokerBase):

    def __init__(self, session):
        BrokerBase.__init__(self, session)

    def get_broker_class(self):
        return Report


class ReferenceBroker(BrokerBase):

    def __init__(self, session):
        BrokerBase.__init__(self, session)

    def get_broker_class(self):
        return Reference

    def get_all_misp_references(self, bypass_validation=False):
        if bypass_validation:
            code = 0
        else:
            code = 4
        try:
            return self.session.query(Reference).filter(Reference.value.like('%{0}%'.format('Event ID')),
                                                        Reference.dbcode.op('&')(code) == code
                                                        ).all()
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def look_for_reference_value(self, reference_definition, value, operand='==', bypass_validation=False):
        """
        returns a list of matching values

        :param attribute_definition: attribute definition to use for the lookup
        :type attribute_definition: AttributeDefinition
        :param value: Value to look for
        :type value: String

        :returns: List of clazz
        """
        result = list()
        if reference_definition is None:
            # look only for the value
            return self.__look_for_value(value, operand, bypass_validation)
        else:
            # look for definition id an the value
            return self.__look_for_definition_value(reference_definition.identifier, value, operand, bypass_validation)
        return result

    def __look_for_value(self, needle, operand, bypass_validation=False):
        if bypass_validation:
            code = 0
        else:
            code = 4
        try:
            if operand == '==':
                return self.session.query(Reference).filter(Reference.value == needle,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
            if operand == '<':
                return self.session.query(Reference).filter(Reference.value < needle,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
            if operand == '>':
                return self.session.query(Reference).filter(Reference.value > needle,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
            if operand == '<=':
                return self.session.query(Reference).filter(Reference.value <= needle,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
            if operand == '>=':
                return self.session.query(Reference).filter(Reference.value >= needle,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
            if operand == 'like':
                return self.session.query(Reference).filter(Reference.value.like('%{0}%'.format(needle)),
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)

    def __look_for_definition_value(self, def_id, needle, operand, bypass_validation=False):
        if bypass_validation:
            code = 0
        else:
            code = 12
        try:
            if operand == '==':
                return self.session.query(Reference).filter(Reference.value == needle,
                                                            Reference.definition_id == def_id,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
            if operand == '<':
                return self.session.query(Reference).filter(Reference.value < needle,
                                                            Reference.definition_id == def_id,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
            if operand == '>':
                return self.session.query(Reference).filter(Reference.value > needle,
                                                            Reference.definition_id == def_id,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
            if operand == '<=':
                return self.session.query(Reference).filter(Reference.value <= needle,
                                                            Reference.definition_id == def_id,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
            if operand == '>=':
                return self.session.query(Reference).filter(Reference.value >= needle,
                                                            Reference.definition_id == def_id,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
            if operand == 'like':
                return self.session.query(Reference).filter(Reference.value.like('%{0}%'.format(needle)),
                                                            Reference.definition_id == def_id,
                                                            Reference.dbcode.op('&')(code) == code
                                                            ).all()
        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            raise BrokerException(error)
