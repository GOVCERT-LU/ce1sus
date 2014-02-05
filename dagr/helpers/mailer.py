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
  def __init__(self, message):
    Exception.__init__(self, message)


class NotInitializedException(MailerException):
  """Server Error"""
  def __init__(self, message):
    MailerException.__init__(self, message)


class Mail(object):

  def __init__(self):
    self.sender = None
    self.reciever = None
    self.subject = None
    self.body = None

  @property
  def message(self):
    return """From: {0}\nTo: {1}\nSubject:{2}\n\n {3}""".format(self.sender,
                                                                self.reciever,
                                                                self.body)


class Mailer(object):

  def __init__(self, config):
    self.__config_section = config.get_section('Mailer')
    self.sender = self.__config_section.get('from')
    self.logger = Log(config)

  def sendMail(self, mail):
    try:
      server = self.__config_section.get('smtp')
      port = self.__config_section.get('port')
      smtpObj = SMTP(server, port)
      # smtpObj.set_debuglevel(1)
      smtpObj.ehlo()

      # Create a text/plain message
      message = MIMEText(mail.body)
      message['Subject'] = mail.subject
      if  mail.sender:
        sender = mail.sender
      else:
        sender = self.sender
      message['From'] = sender
      message['To'] = mail.reciever

      smtpObj.sendmail(sender, mail.reciever, message.as_string())
      smtpObj.quit()
    except SMTPException as error:
      self.get_logger().critical(error)
      raise MailerException(error)

  def get_logger(self):
    return self.logger.get_logger(self.__class__.__name__)
