# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 6, 2014
"""
from email.mime.text import MIMEText
import gnupg
from os import makedirs
import os
from os.path import exists
from smtplib import SMTPException, SMTP

from ce1sus.helpers.common.debug import Log


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


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
    return u"""From: {0}\nTo: {1}\nSubject:{2}\n\n {3}""".format(self.sender,
                                                                 self.reciever,
                                                                 self.subject,
                                                                 self.body)


class Mailer(object):

  pgp = None

  """System for sending mails"""
  def __init__(self, config):
    self.__config_section = config.get_section('Mailer')
    self.sender = self.__config_section.get('from')
    if not self.sender:
      raise MailerException('No from specified in config')
    self.logger = Log(config)
    self.__key_path = self.__config_section.get('gpgkeys', None)
    if self.__key_path:
      self.__passphrase = self.__config_section.get('passphrase', None)
      if not self.__passphrase:
        raise MailerException('No passphrase specified in config')
      self.__keylength = self.__config_section.get('keylength', 2048)
      self.__expiredate = self.__config_section.get('expiredate', None)
      if not self.__expiredate:
        raise MailerException('No expiration date specified in config')
      self.__expiredate = u'{0}'.format(self.__expiredate.date())
    self.gpg = self.__get_gpg()

  def __get_gpg(self):
    if Mailer.pgp:
      return Mailer.pgp
    else:
      if self.__key_path:
        self.get_logger().debug('Getting gpg from {0}'.format(self.__key_path))
        gpg = None
        if self.__key_path:
          gpg = gnupg.GPG(gnupghome=self.__key_path)
          # check if key exists else generate one
          private_keys = gpg.list_keys(True)
          if not private_keys:
            self.get_logger().info('No private keys stored')
            # !??!?
            try:
              os.environ['LOGNAME']
            except KeyError:
              os.environ["LOGNAME"] = "ce1sus"

            input_data = gpg.gen_key_input(name_real='Ce1sus system',
                                           name_email=self.sender,
                                           expire_date=self.__expiredate,
                                           key_type='RSA',
                                           key_length=self.__keylength,
                                           key_usage='',
                                           subkey_type='RSA',
                                           subkey_length=self.__keylength,
                                           subkey_usage='encrypt,sign',
                                           passphrase=self.__passphrase)
            self.get_logger().info('Generating key for {0}'.format(self.sender))
            key = gpg.gen_key(input_data)
            key_str = u'{0}'.format(key)
            keyfolder = self.__key_path + '/keys'
            self.get_logger().info('Generated a new key for {0} keys are stored in {1}'.format(self.sender, keyfolder))
            ascii_armored_public_keys = gpg.export_keys(key_str)
            ascii_armored_private_keys = gpg.export_keys(key_str, True)
            if not exists(keyfolder):
              makedirs(keyfolder)

            with open(keyfolder + '/ce1sus_keys.asc', 'w') as f:
              f.write(ascii_armored_public_keys)
              f.write(ascii_armored_private_keys)
        Mailer.pgp = gpg
        return gpg
      else:
        return None

  def import_gpg(self, key):
    if self.gpg:
      self.gpg.import_keys(key)
    else:
      raise MailerException('Gpg not initialized')

  def __sign_message(self, text):
    try:
      if self.gpg:
        # there should be at most one!
        private_key = self.gpg.list_keys(True)[0]
        signer_fingerprint = private_key.get('fingerprint', None)
        if signer_fingerprint:
          signed_data = self.gpg.sign(text,
                                      keyid=signer_fingerprint,
                                      passphrase=self.__passphrase)
          message = str(signed_data)
          if message:
            return message
          else:
            info_log = getattr(self.get_logger(), 'info')
            info_log('Something went wrong while signing')
      else:
        info_log = getattr(self.get_logger(), 'info')
        info_log('GPG Path not specified sending unsinged mail')
        return text
    except IndexError as error:
      info_log = getattr(self.get_logger(), 'info')
      info_log(error)
      info_log('No private key found. Not sending Mail')

  def __encrypt_message(self, text, reciever):
    self.get_logger().debug('Encrypting message')
    try:
      if self.gpg:
        # there should be at most one!
        private_key = self.gpg.list_keys(True)[0]
        signer_fingerprint = private_key.get('fingerprint', None)
        if signer_fingerprint:
          encrypted_data = self.gpg.encrypt(text, reciever,
                                            sign=signer_fingerprint,
                                            passphrase=self.__passphrase,
                                            always_trust=True)
          return str(encrypted_data)
        else:
          raise MailerException('PK fingerprint not found.')
      else:
        raise MailerException('Gpg not initialized')
    except ImportError as error:
      error_log = getattr(self.get_logger(), 'error')
      error_log(error)

    info_log = getattr(self.get_logger(), 'info')
    info_log('GPG not installed not sending unencrypted mail')
    raise MailerException('GPG not configured.')

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
      if mail.sender:
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

  def get_logger(self):
    """returns the internal logger"""
    return self.logger.get_logger(self.__class__.__name__)
