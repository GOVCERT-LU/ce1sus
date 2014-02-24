# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 23, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerException
from dagr.helpers.mailer import Mailer, Mail, MailerException
from ce1sus.brokers.mailbroker import MailTemplateBroker
from dagr.helpers.debug import Log
from dagr.db.session import SessionManager
from dagr.helpers.config import ConfigException
from ce1sus.brokers.relationbroker import RelationBroker
from ce1sus.common.checks import is_viewable
import re


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
      self.__process_send_event_mail(mail, event, update)
    except (BrokerException, ConfigException) as error:
      raise MailHandlerException(error)

  def __process_subject(self, subject, event):
    self._get_logger().debug('Processing subject')
    text = subject.replace('${event_uuid}', '{0}'.format(event.uuid))
    text = text.replace('${event_id}', '{0}'.format(event.identifier))
    text = text.replace('${event_tlp}', '{0}'.format(event.tlp.text))
    text = text.replace('${event_risk}', '{0}'.format(event.risk))
    text = text.replace('${event_title}', '{0}'.format(event.title))
    return text

  def __attribute_to_text(self, attribute, indent_str):
    self._get_logger().debug('Converting attribute to text')
    value = unicode(attribute.plain_value)
    prefix = '{0} : '.format(attribute.definition.name)
    if '\n' in value:
      value = value.replace('\n', '\n' + indent_str + (' ' * len(prefix)))
    if attribute.ioc == 1:
      text = indent_str + '{0}{1} - IOC'.format(prefix, value)
    else:
      text = indent_str + '{0}{1}'.format(prefix, value)
    return text

  @staticmethod
  def __remove_control_chars(string):
    return re.sub(r"\W", "", string)

  def __object_to_text(self, obj, publication_date=None, indent=1):
    self._get_logger().debug('Converting object to text')
    text = ''
    indent_str = '\t' * indent
    text += ('\t' * (indent - 1)) + obj.definition.name + ':\n'
    if obj.attributes:
      for attribute in obj.attributes:
        if publication_date:
          if (attribute.modified >= publication_date) or (attribute.created >= publication_date):
            if (attribute.bit_value.is_shareable and attribute.bit_value.is_validated):
              text += self.__attribute_to_text(attribute, indent_str) + '\n'
        else:
          if (attribute.bit_value.is_shareable and attribute.bit_value.is_validated):
            text += self.__attribute_to_text(attribute, indent_str) + '\n'
    else:
      text += indent_str + 'Empty' + '\n'
    for child in obj.children:
      text += self.__object_to_text(child, publication_date, indent + 1) + '\n'
    # check if there are items
    if not self.__remove_control_chars(text):
      text = 'None'
    return text

  def __objects_to_text(self, objects, publication_date=None):
    self._get_logger().debug('Converting objects to text')
    text = 'None'
    if objects:
      for obj in objects:
        if publication_date:
          if (obj.modified >= publication_date) or (obj.created >= publication_date):
            if (obj.bit_value.is_shareable and obj.bit_value.is_validated):
              text += self.__object_to_text(obj, publication_date) + '\n'
        else:
          if (obj.bit_value.is_shareable and obj.bit_value.is_validated):
            text += self.__object_to_text(obj, publication_date) + '\n'
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
            if relation.rel_event.last_publish_date >= event.last_publish_date:
              if is_viewable(relation.rel_event, group, False):
                url = self.__get_event_url(relation.rel_event)
                text += url + '\n'
          else:
            if is_viewable(relation.rel_event, group, False):
              url = self.__get_event_url(relation.rel_event)
              text += url + '\n'
    if not self.__remove_control_chars(text):
      text = 'None'
    return text

  def __get_event_url(self, event):
    url = self.config.get('ce1sus', 'baseurl')
    return '{0}/event/extView/{1}'.format(url, event.uuid)

  def __process_publication_body(self, body, event):
    self._get_logger().debug('Processing body')
    # creating metadata
    text = body.replace('${event_uuid}', '{0}'.format(event.uuid))
    text = text.replace('${event_id}', '{0}'.format(event.identifier))
    event_url = self.__get_event_url(event)
    text = text.replace('${event_url}', '{0}'.format(event_url))
    text = text.replace('${event_created}', '{0}'.format(event.created))
    text = text.replace('${event_reporter}', '{0}'.format(event.creator_group.name))
    text = text.replace('${event_tlp}', '{0}'.format(event.tlp.text))
    text = text.replace('${event_analysis}', '{0}'.format(event.analysis))
    text = text.replace('${event_risk}', '{0}'.format(event.risk))
    text = text.replace('${event_title}', '{0}'.format(event.title))
    text = text.replace('${event_description}', '{0}'.format(event.description))

    # creating objects data
    event_objects = self.__objects_to_text(event.objects)
    text = text.replace('${event_objects}', event_objects)
    # Note relations are user specific will be done before sending!
    return text

  def __process_update_body(self, body, event):
    self._get_logger().debug('Processing update body')
    text = self.__process_publication_body(body, event)
    # creating objects data
    objects = list()
    event_objects = self.__objects_to_text(event.objects, event.last_publish_date)
    text = text.replace('${event_updated_objects}', event_objects)
    # Note relations are user specific will be done before sending!
    return text

  def __add_relations(self, mail, group, event, update):
    # add relations
    # creating relations data
    # add relations to mail
    event_relations = self.__relations_to_text(group, event, False)
    mail.body = mail.body.replace('${event_relations}', event_relations)
    if update:
      event_relations = self.__relations_to_text(group, event, True)
      mail.body = mail.body.replace('${event_updated_relations}', event_relations)

  def __send_mail(self, mail, reciever, event):
    mail.reciever = reciever.email
    if mail.encrypt:
      if reciever.gpg_key:
        self._get_logger().debug('Mail sending encrypted mail to {0}'.format(reciever.email))
        self.mailer.send_mail(mail)
      else:
        self._get_logger().info('Mail will not be send to {0} as not gpg key'.format(reciever.email))
    else:
      self._get_logger().debug('Mail sending plain text mail to {0}'.format(reciever.email))
      self.mailer.send_mail(mail)

  def __process_send_event_mail(self, mail, event, update):
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
      for subgroup in event.subgroups:
        for group in subgroup.groups:
          seen_group_ids.append(group.identifier)
          mail.body = mail_body
          self.__add_relations(mail, group, event, update)
          if group.usermails:
            self.__send_mail(mail, group, event)
          else:
            for user in group.users:
              self.__send_mail(mail, user, event)

      # send mail to groups
      for group in event.maingroups:
        mail.body = mail_body
        self.__add_relations(mail, group, event, update)
        if group.identifier not in seen_group_ids:
          # send mail
          if group.usermails:
            self.__send_mail(mail, group, event)
          else:
            for user in group.users:
                self.__send_mail(mail, user, event)

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
      activation_url = url + '/activate/{0}'.format(user.activation_str)
      body = body.replace('${name}', '{0}'.format(user.name))
      body = body.replace('${sirname}', '{0}'.format(user.sirname))
      body = body.replace('${username}', '{0}'.format(user.username))
      body = body.replace('${password}', '{0}'.format(user.password_plain))
      body = body.replace('${ce1sus_url}', '{0}'.format(url))
      body = body.replace('${activation_link}', '{0}'.format(activation_url))
      mail.body = body

      if user.gpg_key:
        mail.encrypt = True

      self.mailer.send_mail(mail)
    except (BrokerException, ConfigException, MailerException) as error:
      raise MailHandlerException(error)

  def import_gpg_key(self, gpg_key):
    self.mailer.add_gpg_key(gpg_key)
