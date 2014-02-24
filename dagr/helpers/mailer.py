# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 6, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from smtplib import SMTPException, SMTP
from email.mime.text import MIMEText
from dagr.helpers.debug import Log
import gnupg


class MailerException(Exception):
  """base exception"""
  pass


class NotInitializedException(MailerException):
  """NotInitializedException"""
  pass


# pylint: disable=R0903
class Mail(object):
  """Mail container"""
  def __init__(self):
    self.sender = None
    self.reciever = None
    self.subject = None
    self.body = None
    self.encrypt = False

  @property
  def message(self):
    """Formated plain message"""
    return """From: {0}\nTo: {1}\nSubject:{2}\n\n {3}""".format(self.sender,
                                                                self.reciever,
                                                                self.body)


class Mailer(object):

  """System for sending mails"""
  def __init__(self, config):
    self.__config_section = config.get_section('Mailer')
    self.sender = self.__config_section.get('from')
    self.logger = Log(config)
    self.__key_path = self.__config_section.get('gpgkeys', None)
    self.__passphrase = self.__config_section.get('passphrase', None)

  def get_gpg(self):
    self.get_logger().debug('Getting gpg')
    gpg = gnupg.GPG(gnupghome=self.__key_path)
    try:
      if self.__key_path:
        gpg.list_keys(True)[0]
    except:
      # TODO: make this externally
      self.get_logger().debug('Importing key gpg')
      keyfile = self.__config_section.get('keyfile', None)
      key_data = open(keyfile).read()
      gpg.import_keys(key_data)
      self.get_logger().debug(gpg.list_keys(True)[0])
    return gpg

  def __sign_message(self, text):
    if self.__key_path:
      # gpg = gnupg.GPG(gnupghome=self.__key_path)
      try:
        if self.__passphrase:
          # there should be at most one!
          gpg = self.get_gpg()
          private_key = gpg.list_keys(True)[0]
          signer_fingerprint = private_key.get('fingerprint', None)
          if signer_fingerprint:
            signed_data = gpg.sign(text,
                     keyid=signer_fingerprint,
                     passphrase=self.__passphrase)
            message = str(signed_data)
            if message:
              return message
            else:
              info_log = getattr(self.get_logger(), 'info')
              info_log('Something went wrong while signing')
      except ImportError as error:
        info_log = getattr(self.get_logger(), 'info')
        info_log(error)

    info_log = getattr(self.get_logger(), 'info')
    info_log('GPG Path not specified sending unsinged mail')
    return text

  def __encrypt_message(self, text, reciever):
    self.get_logger().debug('Encrypting message')

    if self.__key_path:
      try:
        if self.__passphrase:
          # there should be at most one!
          gpg = self.get_gpg()
          private_key = gpg.list_keys(True)[0]
          signer_fingerprint = private_key.get('fingerprint', None)
          if signer_fingerprint:
            encrypted_data = gpg.encrypt(text, reciever,
                                         sign=signer_fingerprint,
                                         passphrase=self.__passphrase,
                                         always_trust=True)
            return str(encrypted_data)
          else:
            raise MailerException('PK fingerprint not found.')
        else:
          raise MailerException('No passphrase specified.')
      except ImportError as error:
        error_log = getattr(self.get_logger(), 'error')
        error_log(error)

    #TODO raise exception!!!
    info_log = getattr(self.get_logger(), 'info')
    info_log('GPG not installed sending unencrypted mail')
    return text

  def send_mail(self, mail):
    """Sends the mail object"""
    try:
      server = self.__config_section.get('smtp')
      port = self.__config_section.get('port')
      smtp_obj = SMTP(server, port)
      # smtp_obj.set_debuglevel(1)
      smtp_obj.ehlo()

      # Create a text/plain message
      text = mail.body.encode("iso-8859-15", "replace")
      if mail.encrypt:
        message = MIMEText(self.__encrypt_message(text, mail.reciever))
      else:
        text = self.__sign_message(text)
        message = MIMEText(text)

      message['Subject'] = mail.subject
      if  mail.sender:
        sender = mail.sender
      else:
        sender = self.sender
      message['From'] = sender
      message['To'] = mail.reciever

      smtp_obj.sendmail(sender, mail.reciever, message.as_string())
      smtp_obj.quit()
    except SMTPException as error:
      self.get_logger().critical(error)
      raise MailerException(error)

  def add_gpg_key(self, data):
    try:
      gpg = self.get_gpg()
      gpg.import_keys(data)
    except ImportError as error:
      error_log = getattr(self.get_logger(), 'error')
      error_log('Could not find gnupg will not import key')
      error_log(error)

  def get_logger(self):
    """returns the internal logger"""
    return self.logger.get_logger(self.__class__.__name__)
