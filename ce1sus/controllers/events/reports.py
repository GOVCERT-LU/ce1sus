# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 9, 2015
"""
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.definitions.referencesbroker import ReferenceDefintionsBroker
from ce1sus.db.brokers.event.reportbroker import ReportBroker, ReferenceBroker
from ce1sus.db.common.broker import BrokerException, NothingFoundException, IntegrityException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ReportController(BaseController):
    """event controller handling all actions in the event section"""

    def __init__(self, config, session=None):
        BaseController.__init__(self, config, session)
        self.report_broker = self.broker_factory(ReportBroker)
        self.reference_broker = self.broker_factory(ReferenceBroker)
        self.reference_definition_broker = self.broker_factory(ReferenceDefintionsBroker)

    def get_report_by_id(self, identifier):
        try:
            return self.report_broker.get_by_id(identifier)
        except BrokerException as error:
            raise ControllerException(error)

    def get_report_by_uuid(self, uuid):
        try:
            return self.report_broker.get_by_uuid(uuid)
        except BrokerException as error:
            raise ControllerException(error)

    def insert_report(self, report, user, commit=True):
        try:
            user = self.user_broker.get_by_id(user.identifier)
            self.set_extended_logging(report, user, user.group, True)
            self.report_broker.insert(report)
        except IntegrityException as error:
            self.logger.debug(error)
            self.logger.info(u'User {0} tried to insert a report with uuid "{1}" but the uuid already exists'.format(user.username, report.uuid))
            raise ControllerException(u'An report with uuid "{0}" already exists'.format(report.uuid))
        except BrokerException as error:
            raise ControllerException(error)

    def update_report(self, report, user, commit=True):
        try:
            user = self.user_broker.get_by_id(user.identifier)
            self.set_extended_logging(report, user, user.group, False)
            self.report_broker.update(report)
        except BrokerException as error:
            raise ControllerException(error)

    def remove_report(self, report, user, commit=True):
        try:
            self.report_broker.remove_by_id(report.identifier)
        except BrokerException as error:
            raise ControllerException(error)

    def get_reference_definitions_by_id(self, identifier):
        try:
            return self.reference_definition_broker.get_by_id(identifier)
        except NothingFoundException as error:
            raise ControllerNothingFoundException(error)
        except BrokerException as error:
            raise ControllerException(error)

    def get_reference_definitions_by_uuid(self, uuid):
        try:
            return self.reference_definition_broker.get_by_uuid(uuid)
        except NothingFoundException as error:
            raise ControllerNothingFoundException(error)
        except BrokerException as error:
            raise ControllerException(error)

    def get_reference_by_id(self, identifier):
        try:
            return self.reference_broker.get_by_id(identifier)
        except NothingFoundException as error:
            raise ControllerNothingFoundException(error)
        except BrokerException as error:
            raise ControllerException(error)

    def get_reference_by_uuid(self, uuid):
        try:
            return self.reference_broker.get_by_uuid(uuid)
        except NothingFoundException as error:
            raise ControllerNothingFoundException(error)
        except BrokerException as error:
            raise ControllerException(error)

    def update_reference(self, reference, user, commit=True):
        # TODO: include handler
        try:
            user = self.user_broker.get_by_id(user.identifier)
            self.set_extended_logging(reference, user, user.group, False)
            # TODO integrate handlersd
            self.reference_broker.update(reference)
        except BrokerException as error:
            raise ControllerException(error)

    def remove_reference(self, reference, user, commit=True):
        # TODO: include handler
        try:
            self.reference_broker.remove_by_id(reference.identifier)
        except BrokerException as error:
            raise ControllerException(error)

    def insert_reference(self, reference, additional_references, user, commit=True, owner=True):
        self.logger.debug('User {0} inserts a new reference'.format(user.username))

        # handle handler references

        try:

            user = self.user_broker.get_by_id(user.identifier)
            if owner:
                reference.properties.is_validated = True

            self.set_extended_logging(reference, user, user.group, True)
            self.reference_broker.insert(reference, False)

            if additional_references:
                for additional_reference in additional_references:
                    if owner:
                        additional_reference.properties.is_validated = True

                    self.set_extended_logging(additional_reference, user, user.group, True)
                    self.reference_broker.insert(additional_reference, commit=False)

            self.reference_broker.do_commit(commit)
            return reference, additional_references
        except IntegrityException as error:
            self.logger.debug(error)
            self.logger.info(u'User {0} tried to insert a reference with uuid "{1}" but the uuid already exists'.format(user.username, reference.uuid))
            raise ControllerException(u'An reference with uuid "{0}" already exists'.format(reference.uuid))
        except BrokerException as error:
            raise ControllerException(error)

    def get_defintion_by_chksums(self, chksums):
        try:
            return self.reference_definition_broker.get_defintion_by_chksums(chksums)
        except BrokerException as error:
            raise ControllerException(error)

    def insert_handler_reports(self, related_reports, user, commit=True, owner=False):
        # Validate children
        validated = False
        if related_reports:
            for related_report in related_reports:
                self.__validate_report(related_report)
            validated = True

        if validated:
            for related_report in related_reports:
                self.insert_report(related_report, user, False)
        self.report_broker.do_commit(commit)

    def __validate_report(self, report):
        # validate
        if report.validate:
            for related_report in report.related_reports:
                if not related_report.validate:
                    raise ControllerException('Related object is invalid')
        else:
            raise ControllerException('Object is invalid')
