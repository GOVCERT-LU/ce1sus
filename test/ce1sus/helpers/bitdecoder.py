# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import unittest
from ce1sus.helpers.bitdecoder import BitValue


# pylint: disable=R0904
class TestBitDecoder(unittest.TestCase):

    def testRestValidSharable(self):
        test = BitValue('1110')
        assert test.isRestInsert
        assert test.isValidated
        assert not test.isWebInsert
        assert test.isSharable

    def testWebValidSharable(self):
        test = BitValue('1101')
        assert not test.isRestInsert
        assert test.isValidated
        assert test.isWebInsert
        assert test.isSharable

    def testRestValid(self):
        test = BitValue('0110')
        assert test.isRestInsert
        assert test.isValidated
        assert not test.isWebInsert
        assert not test.isSharable

    def testWebValid(self):
        test = BitValue('0101')
        assert not test.isRestInsert
        assert test.isValidated
        assert test.isWebInsert
        assert not test.isSharable

    def testRestSharable(self):
        test = BitValue('1010')
        assert test.isRestInsert
        assert not test.isValidated
        assert not test.isWebInsert
        assert test.isSharable

    def testWebSharable(self):
        test = BitValue('1001')
        assert not test.isRestInsert
        assert not test.isValidated
        assert test.isWebInsert
        assert test.isSharable

    def testWebself(self):
        test = BitValue('0001')
        assert not test.isRestInsert
        assert not test.isValidated
        assert test.isWebInsert
        assert not test.isSharable

    def testToString(self):
      test = BitValue(5)
      print test.bitCode

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
