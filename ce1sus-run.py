# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
import os
import cherrypy
from ce1sus.common.bootstrap import bootstrap
from ce1sus.helpers.common.config import Configuration
from ce1sus.db.classes.cstix.extensions.marking.simple_markings import SimpleMarkingStructure
from ce1sus.db.classes.cstix.common.vocabstring import VocabString
from ce1sus.db.classes.cstix.extensions.test_mechanism.generic_test_mechanism import GenericTestMechanism

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

basePath = os.path.dirname(os.path.abspath(__file__))
ce1susConfigFile = basePath + '/config/ce1sus.conf'

if __name__ == '__main__':



  bootstrap(Configuration(ce1susConfigFile))
  try:
    cherrypy.engine.start()
    cherrypy.engine.block()
  except cherrypy._cperror as e:
    raise ConfigException(e)
else:
  bootstrap(Configuration(ce1susConfigFile))
  cherrypy.engine.start()
  application = cherrypy.tree
