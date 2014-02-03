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
        assert test.is_rest_instert
        assert test.is_validated
        assert not test.is_web_insert
        assert test.is_shareable

    def testWebValidSharable(self):
        test = BitValue('1101')
        assert not test.is_rest_instert
        assert test.is_validated
        assert test.is_web_insert
        assert test.is_shareable

    def testRestValid(self):
        test = BitValue('0110')
        assert test.is_rest_instert
        assert test.is_validated
        assert not test.is_web_insert
        assert not test.is_shareable

    def testWebValid(self):
        test = BitValue('0101')
        assert not test.is_rest_instert
        assert test.is_validated
        assert test.is_web_insert
        assert not test.is_shareable

    def testRestSharable(self):
        test = BitValue('1010')
        assert test.is_rest_instert
        assert not test.is_validated
        assert not test.is_web_insert
        assert test.is_shareable

    def testWebSharable(self):
        test = BitValue('1001')
        assert not test.is_rest_instert
        assert not test.is_validated
        assert test.is_web_insert
        assert test.is_shareable

    def testWebself(self):
        test = BitValue('0001')
        assert not test.is_rest_instert
        assert not test.is_validated
        assert test.is_web_insert
        assert not test.is_shareable

    def testToString(self):
      test = BitValue(5)
      print test.bit_code

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
