# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 23, 2014
"""
import re

from ce1sus.common.checks import is_object_viewable, get_max_tlp
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.controllers.events.relations import RelationController
from ce1sus.db.brokers.mailtemplate import MailTemplateBroker
from ce1sus.db.common.broker import BrokerException, ValidationException, NothingFoundException
from ce1sus.helpers.common.mailer import Mail, MailerException
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator
from ce1sus.helpers.pluginfunctions import is_plugin_available, get_plugin_function
from ce1sus.db.brokers.event.eventbroker import EventBroker

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MailController(BaseController):
  """Controller handling all the requests for groups"""

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.mail_broker = self.broker_factory(MailTemplateBroker)
    self.event_broker = self.broker_factory(EventBroker)
    self.relation_controller = RelationController(config, session)
    self.mail_handler = None
    self.url = config.get('ce1sus', 'baseurl')
    if is_plugin_available('mail', self.config):
      self.mail_handler = get_plugin_function('mail', 'get_instance', self.config, 'internal_plugin')()

  def get_all(self):
    try:
      return self.mail_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_by_id(self, mail_id):
    try:
      return self.mail_broker.get_by_id(mail_id)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_by_uuid(self, uuid):
    try:
      return self.mail_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def update_mail(self, mail_template, user):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_simple_logging(mail_template, user, insert=False)
      mail_template = self.mail_broker.update(mail_template)
      return mail_template
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(mail_template)
      raise ControllerException(u'Could not update mail due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def insert_mail(self, mail_template, user, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_simple_logging(mail_template, user, insert=False)
      mail_template = self.mail_broker.insert(mail_template, False)
      self.mail_broker.do_commit(commit)
      return mail_template
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(mail_template)
      raise ControllerException(u'Could not insert mail due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def import_gpg_key(self, key):
    if self.mail_handler:
      self.mail_handler.import_gpg_key(key)

  def send_activation_mail(self, user):
    try:
      if self.mail_handler:
        mail_tmpl = self.mail_broker.get_activation_template()
        mail = Mail()
        mail.reciever = user.email
        mail.subject = mail_tmpl.subject
        body = mail_tmpl.body
        url = self.config.get('ce1sus', 'baseurl')
        activation_url = url + u'/#/activate/{0}'.format(user.activation_str)
        body = body.replace(u'${name}', u'{0}'.format(user.name))
        body = body.replace(u'${sirname}', u'{0}'.format(user.sirname))
        body = body.replace(u'${username}', u'{0}'.format(user.username))
        body = body.replace(u'${password}', u'{0}'.format(user.plain_password))
        body = body.replace(u'${ce1sus_url}', u'{0}'.format(url))
        body = body.replace(u'${activation_link}', u'{0}'.format(activation_url))
        mail.body = body

        if user.gpg_key:
          mail.encrypt = True

        self.mail_handler.send_mail(mail)
    except Exception as error:
      self.logger.info(u'Could not send activation email to "{0}" for user "{1}" Error:{2}'.format(user.email, user.username, error))
      raise ControllerException(u'Could not send activation email to "{0}" for user "{1}"'.format(user.email, user.username))

  def __process_subject(self, subject, event):
    self.logger.debug(u'Processing subject')
    text = subject.replace(u'${event_uuid}', u'{0}'.format(event.uuid))
    text = text.replace(u'${event_id}', u'{0}'.format(event.identifier))
    text = text.replace(u'${event_tlp}', u'{0}'.format(event.tlp))
    text = text.replace(u'${event_risk}', u'{0}'.format(event.risk))
    text = text.replace(u'${event_title}', u'{0}'.format(event.title))
    return text

  def __populate_event_metadata(self, body, event):
    text = body.replace(u'${event_uuid}', u'{0}'.format(event.uuid))
    text = text.replace(u'${event_id}', u'{0}'.format(event.identifier))
    event_url = self.__get_event_url(event)
    text = text.replace(u'${event_url}', u'{0}'.format(event_url))
    text = text.replace(u'${event_created}', u'{0}'.format(event.created_at))
    text = text.replace(u'${event_reporter}', u'{0}'.format(event.creator_group.name))
    text = text.replace(u'${event_tlp}', u'{0}'.format(event.tlp))
    text = text.replace(u'${event_analysis}', u'{0}'.format(event.analysis))
    text = text.replace(u'${event_risk}', u'{0}'.format(event.risk))
    text = text.replace(u'${event_title}', u'{0}'.format(event.title))
    text = text.replace(u'${event_description}', u'{0}'.format(event.description))
    return text

  def __get_attributes(self, event, user, group, update, proposal=False):
    try:
      flat_attributes = self.relation_controller.get_flat_attributes_for_event(event)
      # return only visible attribtues
      event_permissions = None
      if user:
        event_permissions = self.event_broker.get_event_user_permissions(event, user)
      if group:
        event_permissions = self.event_broker.get_event_group_permissions(event, group)
      if event_permissions:
        result = ''
        for attribute in flat_attributes:
          if is_object_viewable(attribute, event_permissions):
            if update:
              if attribute.created_at <= event.last_publish_date:
                # skip the ones we are not intreseted
                continue
              if proposal:
                if not attribute.properties.is_proposal:
                  continue

            if attribute.is_ioc:
              text = u'{0}/{1}: {2} - IOC'.format(attribute.object.definition.name, attribute.definition.name, attribute.value)
            else:
              text = u'{0}/{1}: {2}'.format(attribute.object.definition.name, attribute.definition.name, attribute.value)
            result = result + text + '\n'
        return result
    except BrokerException as error:
      raise MailerException(error)

  def is_event_viewable(self, event, group):
    # The same is in the mailer
    if event.originating_group_id == group.identifier:
      return True
    else:
      if group:
        if group.identifier:
          user_group = self.group_broker.get_by_id(group.identifier)
          tlp_lvl = get_max_tlp(user_group)
          if event.tlp_level_id >= tlp_lvl:
            return True
          else:
            grp_ids = list()
            for group in user_group.children:
              grp_ids.append(group.identifier)
            grp_ids.append(group.identifier)

            for eventgroup in event.groups:
              group = eventgroup.group
              if group.identifier in grp_ids:
                return True
            return False
        else:
          return False
      else:
        return False

  def __get_event_url(self, event):
    return '{0}/#/events/event/{1}'.format(self.url, event.uuid)

  @staticmethod
  def __remove_control_chars(string):
    return re.sub(r"\W", "", string)

  def __relations_to_text(self, user, group, event, update):
    text = 'None'
    # get unique event relations
    relations = self.relation_controller.get_related_events_for_event(event)
    if relations:
      text = ''
      for relation in relations:
        if relation.rel_event.published:
          if update:
            if relation.rel_event.last_publish_date and relation.rel_event.last_publish_date >= event.last_publish_date:
              if self.is_event_viewable(relation.rel_event, group):
                url = self.__get_event_url(relation.rel_event)
                text = u'{0}{1}\n'.format(text, url)
          else:
            if self.is_event_viewable(relation.rel_event, group):
              url = self.__get_event_url(relation.rel_event)
              text = u'{0}{1}\n'.format(text, url)
    if not self.__remove_control_chars(text):
      text = 'None'
    if not text.strip():
      return 'None'
    return text

  def __add_relations(self, body, user, group, event, update):
    # add relations
    # creating relations data
    # add relations to mail
    event_relations = self.__relations_to_text(user, group, event, False)
    if '${event_relations}' in body:
      body = body.replace(u'${event_relations}', event_relations)
      if update:
        if '${event_updated_relations}' in body:
          event_relations = self.__relations_to_text(user, group, event, True)
          body = body.replace(u'${event_updated_relations}', event_relations)
    return body

  def get_publication_mail(self, event, user, group):
    template = self.mail_broker.get_publication_template()
    subject = self.__process_subject(template.subject, event)
    body = self.__populate_event_metadata(template.body, event)
    body = self.__add_relations(body, user, group, event, False)

    # creating objects data
    if '${event_objects}' in body:
      event_objects = self.__get_attributes(event, user, group, False, False)
      body = body.replace(u'${event_objects}', event_objects)

    mail = Mail()
    mail.subject = subject
    mail.body = body
    if user:
      mail.reciever = user.email
    if group:
      mail.reciever = group.email
    return mail

  def get_publication_update_mail(self, event, user, group):
    template = self.mail_broker.get_update_template()
    subject = self.__process_subject(template.subject, event)
    body = self.__populate_event_metadata(template.body, event)
    body = self.__add_relations(body, user, group, event, True)

    # creating objects data
    if '${event_objects}' in body:
      event_objects = self.__get_attributes(event, user, group, False, False)
      body = body.replace(u'${event_objects}', event_objects)
    if '${event_updated_objects}' in body:
      event_objects = self.__get_attributes(event, user, group, True, False)
      body = body.replace(u'${event_updated_objects}', event_objects)

    mail = Mail()
    mail.subject = subject
    mail.body = body
    if user:
      mail.reciever = user.email
    if group:
      mail.reciever = group.email
    return mail

  def get_proposal_mail(self, event, user, group):
    template = self.mail_broker.get_proposal_template()
    subject = self.__process_subject(template.subject, event)
    body = self.__populate_event_metadata(template.body, event)

    # creating objects data
    if '${event_objects}' in body:
      event_objects = self.__get_attributes(event, user, group, True, True)
      body = body.replace(u'${event_objects}', event_objects)

    mail = Mail()
    mail.subject = subject
    mail.body = body
    if user:
      mail.reciever = user.email
    if group:
      mail.reciever = group.email
    return mail

  def send_mail(self, mail):
    try:
      self.mail_handler.send_mail(mail)
    except Exception as error:
      message = u'Could not send email to "{0}" Error:{2}'.format(mail.reciever, error)
      self.logger.info(message)
      raise ControllerException(message)
