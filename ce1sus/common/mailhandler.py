# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 23, 2014
"""
import random
import re

from ce1sus.brokers.mailbroker import MailTemplateBroker
from ce1sus.brokers.relationbroker import RelationBroker
from ce1sus.common.checks import is_viewable
from dagr.db.broker import BrokerException
from dagr.db.session import SessionManager
from dagr.helpers.config import ConfigException
from dagr.helpers.datumzait import DatumZait
from dagr.helpers.debug import Log
from dagr.helpers.hash import hashSHA1
from dagr.helpers.mailer import Mailer, Mail, MailerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MailHandlerException(Exception):
  pass


class MailHandler(object):

  def __init__(self, config):
    self.config = config
    self.mailer = Mailer(config)
    self.session_manager = SessionManager(config)
    self.mail_broker = self.session_manager.broker_factory(MailTemplateBroker)
    self.logger = Log(config)
    self.relation_broker = self.session_manager.broker_factory(RelationBroker)

  def _get_logger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return self.logger.get_logger(self.__class__.__name__)

  def send_event_mail(self, event):
    """Procedure to send out activation mail"""
    try:
      mail = Mail()

      if event.last_publish_date:
        mail_tmpl = self.mail_broker.get_publication_template()
        mail.body = self.__process_update_body(mail_tmpl.body, event)
        update = True
      else:
        mail_tmpl = self.mail_broker.get_update_template()
        mail.body = self.__process_publication_body(mail_tmpl.body, event)
        update = False

      mail.subject = self.__process_subject(mail_tmpl.subject, event)
      self.__process_send_mail(mail, event, update, True)
    except (BrokerException, ConfigException) as error:
      raise MailHandlerException(error)

  def send_event_notification_mail(self, event):
    try:
      mail = Mail()
      mail_tmpl = self.mail_broker.get_notifcation_template()
      mail.body = self.__process_notification_body(mail_tmpl.body, event)
      mail.subject = self.__process_subject(mail_tmpl.subject, event)
      # send mail to groups
      if event.creator_group.usermails:
        self.__send_mail(mail, event.creator_group, event, True)
      else:
        for user in event.creator_group.users:
          self.__send_mail(mail, user, event, True)
    except (BrokerException, ConfigException) as error:
      raise MailHandlerException(error)

  def __process_subject(self, subject, event):
    self._get_logger().debug(u'Processing subject')
    text = subject.replace(u'${event_uuid}', u'{0}'.format(event.uuid))
    text = text.replace(u'${event_id}', u'{0}'.format(event.identifier))
    text = text.replace(u'${event_tlp}', u'{0}'.format(event.tlp.text))
    text = text.replace(u'${event_risk}', u'{0}'.format(event.risk))
    text = text.replace(u'${event_title}', u'{0}'.format(event.title))
    return text

  def __attribute_to_text(self, attribute, indent_str):
    self._get_logger().debug('Converting attribute to text')
    value = unicode(attribute.plain_value)
    prefix = u'{0} : '.format(attribute.definition.name)
    if '\n' in value:
      value = value.replace(u'\n', u'\n' + indent_str + (' ' * len(prefix)))
    if attribute.ioc == 1:
      text = u'{0}{1}{2} - IOC'.format(indent_str, prefix, value)
    else:
      text = u'{0}{1}{2}'.format(indent_str, prefix, value)
    return text

  @staticmethod
  def __remove_control_chars(string):
    return re.sub(r"\W", "", string)

  def __object_to_text(self, obj, publication_date=None, indent=1):
    self._get_logger().debug('Converting object to text')
    text = ''
    indent_str = '\t' * indent
    text = u'{0}{1}{2}:\n'.format(text, ('\t' * (indent - 1)), obj.definition.name)
    if obj.attributes:
      for attribute in obj.attributes:
        if publication_date:
          if (attribute.modified >= publication_date) or (attribute.created >= publication_date):
            if (attribute.bit_value.is_shareable and attribute.bit_value.is_validated):
              text = u'{0}{1}\n'.format(text, self.__attribute_to_text(attribute, indent_str))
        else:
          if (attribute.bit_value.is_shareable and attribute.bit_value.is_validated):
            text = u'{0}{1}\n'.format(text, self.__attribute_to_text(attribute, indent_str))
    else:
      text = u'{0}{1}Empty\n'.format(text, indent_str)
    for child in obj.children:
      text = u'{0}{1}\n'.format(text, self.__object_to_text(child, publication_date, indent + 1))
    # check if there are items
    if not self.__remove_control_chars(text):
      text = u'None'
    return text

  def __objects_to_text(self, objects, publication_date=None):
    self._get_logger().debug('Converting objects to text')
    text = 'None'
    if objects:
      text = ''
      for obj in objects:
        if publication_date:
          if (obj.modified >= publication_date) or (obj.created >= publication_date):
            if (obj.bit_value.is_shareable and obj.bit_value.is_validated):
              text = u'{0}{1}\n'.format(text, self.__object_to_text(obj, publication_date))
        else:
          if (obj.bit_value.is_shareable and obj.bit_value.is_validated):
            text = u'{0}{1}\n'.format(text, self.__object_to_text(obj, publication_date))
      if not self.__remove_control_chars(text):
        text = 'None'
    else:
      text = 'Empty'
    return text

  def __relations_to_text(self, group, event, update):
    text = 'None'
    relations = self.relation_broker.get_relations_by_event(event, True)
    if relations:
      text = ''
      for relation in relations:
        if relation.rel_event.published:
          if update:
            if relation.rel_event.last_publish_date and relation.rel_event.last_publish_date >= event.last_publish_date:
              if is_viewable(relation.rel_event, group, False):
                url = self.__get_event_url(relation.rel_event)
                text = u'{0}{1}\n'.format(text, url)
          else:
            if is_viewable(relation.rel_event, group, False):
              url = self.__get_event_url(relation.rel_event)
              text = u'{0}{1}\n'.format(text, url)
    if not self.__remove_control_chars(text):
      text = 'None'
    if not text.strip():
      return 'None'
    return text

  def __get_event_url(self, event):
    url = self.config.get('ce1sus', 'baseurl')
    return '{0}/events/event/extview/{1}'.format(url, event.uuid)

  def __process_publication_body(self, body, event):
    self._get_logger().debug('Processing body')
    # creating metadata
    text = body.replace(u'${event_uuid}', u'{0}'.format(event.uuid))
    text = text.replace(u'${event_id}', u'{0}'.format(event.identifier))
    event_url = self.__get_event_url(event)
    text = text.replace(u'${event_url}', u'{0}'.format(event_url))
    text = text.replace(u'${event_created}', u'{0}'.format(event.created))
    text = text.replace(u'${event_reporter}', u'{0}'.format(event.creator_group.name))
    text = text.replace(u'${event_tlp}', u'{0}'.format(event.tlp.text))
    text = text.replace(u'${event_analysis}', u'{0}'.format(event.analysis))
    text = text.replace(u'${event_risk}', u'{0}'.format(event.risk))
    text = text.replace(u'${event_title}', u'{0}'.format(event.title))
    text = text.replace(u'${event_description}', u'{0}'.format(event.description))

    # creating objects data
    if '${event_objects}' in text:
      event_objects = self.__objects_to_text(event.objects)
      text = text.replace(u'${event_objects}', event_objects)
    # Note relations are user specific will be done before sending!
    return text

  def __process_notification_body(self, body, event):
    self._get_logger().debug('Processing body')
    # creating metadata
    text = body.replace(u'${event_uuid}', u'{0}'.format(event.uuid))
    text = text.replace(u'${event_id}', u'{0}'.format(event.identifier))
    event_url = self.__get_event_url(event)
    text = text.replace(u'${event_url}', u'{0}'.format(event_url))
    text = text.replace(u'${event_created}', u'{0}'.format(event.created))
    text = text.replace(u'${event_reporter}', u'{0}'.format(event.creator_group.name))
    text = text.replace(u'${event_tlp}', u'{0}'.format(event.tlp.text))
    text = text.replace(u'${event_analysis}', u'{0}'.format(event.analysis))
    text = text.replace(u'${event_risk}', u'{0}'.format(event.risk))
    text = text.replace(u'${event_title}', u'{0}'.format(event.title))
    text = text.replace(u'${event_description}', u'{0}'.format(event.description))
    return text

  def __process_update_body(self, body, event):
    self._get_logger().debug(u'Processing update body')
    text = self.__process_publication_body(body, event)
    # creating objects data
    objects = list()
    event_objects = self.__objects_to_text(event.objects, event.last_publish_date)
    text = text.replace(u'${event_updated_objects}', event_objects)
    # Note relations are user specific will be done before sending!
    return text

  def __add_relations(self, mail, group, event, update):
    # add relations
    # creating relations data
    # add relations to mail
    event_relations = self.__relations_to_text(group, event, False)
    mail.body = mail.body.replace(u'${event_relations}', event_relations)
    if update:
      event_relations = self.__relations_to_text(group, event, True)
      mail.body = mail.body.replace(u'${event_updated_relations}', event_relations)

  def __send_mail(self, mail, reciever, event, ignore_errors=False):
    try:
      mail.reciever = reciever.email
      if mail.encrypt:
        if reciever.gpg_key:
          self._get_logger().debug(u'Mail sending encrypted mail to {0}'.format(reciever.email))
          self.mailer.send_mail(mail)
        else:
          self._get_logger().info(u'Mail will not be send to {0} as not gpg key'.format(reciever.email))
      else:
        self._get_logger().debug(u'Mail sending plain text mail to {0}'.format(reciever.email))
        self.mailer.send_mail(mail)
    except (MailerException, TypeError) as error:
      if ignore_errors:
        self._get_logger().info(u'Mail could not be send to mail to {0} due to {1}'.format(reciever.email, error))
      else:
        raise error

  def __process_send_mail(self, mail, event, update, sent_to_subgroups=True, ignore_errors=False):
    try:

      # send mail only if gpg key of the user or tlp == White
      # decide if to encrypt if TLP == WHITE do not
      if event.tlp_level_id == 3:
        mail.encrypt = False
      else:
        mail.encrypt = True

      mail_body = mail.body
      # send mail to subgroups
      seen_group_ids = list()
      if sent_to_subgroups:
        for subgroup in event.subgroups:
          for group in subgroup.groups:
            seen_group_ids.append(group.identifier)
            mail.body = mail_body
            self.__add_relations(mail, group, event, update)
            if group.usermails:
              self.__send_mail(mail, group, event, ignore_errors)
            else:
              for user in group.users:
                self.__send_mail(mail, user, event, ignore_errors)

      # send mail to groups
      for group in event.maingroups:
        mail.body = mail_body
        self.__add_relations(mail, group, event, update)
        if group.identifier not in seen_group_ids:
          # send mail
          if group.usermails:
            self.__send_mail(mail, group, event, ignore_errors)
          else:
            for user in group.users:
                self.__send_mail(mail, user, event, ignore_errors)

    except MailerException as error:
      self._get_logger().critical(error)

  def send_activation_mail(self, user):
    try:
      """Procedure to send out activation mail"""
      mail_tmpl = self.mail_broker.get_activation_template()
      mail = Mail()
      mail.reciever = user.email
      mail.subject = mail_tmpl.subject
      body = mail_tmpl.body
      url = self.config.get('ce1sus', 'baseurl')
      activation_url = url + u'/activate/{0}'.format(user.activation_str)
      body = body.replace(u'${name}', u'{0}'.format(user.name))
      body = body.replace(u'${sirname}', u'{0}'.format(user.sirname))
      body = body.replace(u'${username}', u'{0}'.format(user.username))
      body = body.replace(u'${password}', u'{0}'.format(user.password_plain))
      body = body.replace(u'${ce1sus_url}', u'{0}'.format(url))
      body = body.replace(u'${activation_link}', u'{0}'.format(activation_url))
      mail.body = body
      user.activation_str = hashSHA1('{0}{1}'.format(user.password_plain, random.random()))
      user.activation_sent = DatumZait.utcnow()
      if user.gpg_key:
        mail.encrypt = True

      self.mailer.send_mail(mail)
    except (BrokerException, ConfigException, MailerException) as error:
      raise MailHandlerException(error)

  def import_gpg_key(self, gpg_key):
    self.mailer.add_gpg_key(gpg_key)
