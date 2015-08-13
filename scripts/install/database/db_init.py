# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""

import os
import sys


basePath = os.path.dirname(os.path.abspath(__file__)) + '/../../../'
sys.path.insert(0, '../../../')


# must be known as they are not imported by base -> polymorphic classes
from ce1sus.common.dbinit import dbinit
from ce1sus.helpers.common.config import Configuration

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


if __name__ == '__main__':

    # want parent of parent directory aka ../../
    # setup cherrypy
    #
    basePath = os.path.dirname(os.path.abspath(__file__))
    ce1susConfigFile = basePath + '/../../../config/ce1sus.conf'

    config = Configuration(ce1susConfigFile)

    dbinit(config)
