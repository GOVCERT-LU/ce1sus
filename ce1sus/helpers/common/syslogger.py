# -*- coding: utf-8 -*-

"""
(Description)

Created on Mar 17, 2015
"""
import syslog


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SysloggerExcepton(Exception):
    pass


class Syslogger(object):

    def __init__(self, config=None, verbose=False):
        if config:
            level = config.get('syslogger', 'level', 'error').lower()
            self.log_syslog = config.get('syslogger', 'logtosyslog', False)
            self.log_console = config.get('syslogger', 'logtoconsole', False)
        else:
            level = 'info'
            self.log_syslog = False
            self.log_console = True
        self.level = self.get_level_id(level)
        self.info('Syslog enabled')

    def get_level_id(self, level):
        if level == 'debug':
            return 3
        elif level == 'info':
            return 2
        elif level == 'warning':
            return 1
        elif level == 'error':
            return 0
        raise SysloggerExcepton(u'Level {0} is not supported'.format(level))

    def debug(self, message):
        if self.log_syslog and self.level >= 3:
            syslog.syslog(syslog.LOG_DEBUG, u'[DEBUG] {0}'.format(message))
            if self.log_console:
                print u'[DEBUG] {0}'.format(message)

    def info(self, message):
        if self.log_syslog and self.level >= 2:
            syslog.syslog(syslog.LOG_INFO, u'[INFO] {0}'.format(message))
            if self.log_console:
                print u'[INFO] {0}'.format(message)

    def warning(self, message):
        if self.log_syslog and self.level >= 1:
            syslog.syslog(syslog.LOG_WARNING, u'[WARNING] {0}'.format(message))
            if self.log_console:
                print u'[WARNING] {0}'.format(message)

    def error(self, message):
        if self.log_syslog and self.level >= 0:
            syslog.syslog(syslog.LOG_ERR, u'[ERROR] {0}'.format(message))
            if self.log_console:
                print u'[ERROR] {0}'.format(message)
