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

  def send_mail(self, mail):
    """Sends the mail object"""
    try:
      server = self.__config_section.get('smtp')
      port = self.__config_section.get('port')
      smtp_obj = SMTP(server, port)
      # smtp_obj.set_debuglevel(1)
      smtp_obj.ehlo()

      # Create a text/plain message
      message = MIMEText(mail.body)
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

  def get_logger(self):
    """returns the internal logger"""
    return self.logger.get_logger(self.__class__.__name__)
