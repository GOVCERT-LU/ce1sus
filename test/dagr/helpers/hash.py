'''
Created on Sep 16, 2013

@author: jhemp
'''
import unittest
import dagr.helpers.hash as hasher
import os


# pylint: disable=R0904, C0111, R0201, W0612, W0613, R0915, R0903
class Testhash(unittest.TestCase):

  def testHashes(self):

    assert hasher.hashMD5('Test') == '0cbc6611f5540bd0809a388dc95a615b'
    assert hasher.hashSHA1('Test') == ('640ab2bae07bedc4c163f679a746f7ab7'
                                       + 'fb5d1fa')
    assert hasher.hashSHA256('Test') == ('532eaabd9574880dbf76b9b8cc00832c20a6'
                                       + 'ec113d682299550d7a6e0f345e25')
    assert hasher.hashSHA384('Test') == ('7b8f4654076b80eb963911f19cfad1aaf428'
                                       + '5ed48e826f6cde1b01a79aa73fadb5446e66'
                                       + '7fc4f90417782c91270540f3')
    hash512 = hasher.hashSHA512('Test')
    assert hash512 == ('c6ee9e33cf5c6715a1d148fd73f7318884b41a'
                                      + 'dcb916021e2bc0e800a5c5dd97f5142178'
                                      + 'f6ae88c8fdd98e1afb0ce4c8d2c54b5f37b30'
                                      + 'b7da1997bb33b0b8a31')
    assert hasher.hashMD5(None) == ''

  def testFileHashes(self):
    # generate file
    testFile = open("file.txt", "w")
    testFile.write("Test")
    testFile.close()
    # startTests
    assert hasher.fileHashMD5('file.txt') == '0cbc6611f5540bd0809a388dc95a615b'
    string = hasher.fileHashSHA1('file.txt')
    assert string == '640ab2bae07bedc4c163f679a746f7ab7fb5d1fa'
    string = hasher.fileHashSHA256('file.txt')
    assert string == ('532eaabd9574880dbf76b9b8cc00832c20a6e'
                                       + 'c113d682299550d7a6e0f345e25')
    string = hasher.fileHashSHA384('file.txt')
    assert string == ('7b8f4654076b80eb963911f19cfad1aaf4285'
                                       + 'ed48e826f6cde1b01a79aa73fadb5446e66'
                                       + '7fc4f90417782c91270540f3')
    string = hasher.fileHashSHA512('file.txt')
    assert string == ('c6ee9e33cf5c6715a1d148fd73f7318884b41a'
                                      + 'dcb916021e2bc0e800a5c5dd97f5142178'
                                      + 'f6ae88c8fdd98e1afb0ce4c8d2c54b5f37b30'
                                      + 'b7da1997bb33b0b8a31')

    # remove file
    basedir = os.path.dirname('file.txt')
    if not os.path.exists(basedir):
      os.remove('file.txt')
