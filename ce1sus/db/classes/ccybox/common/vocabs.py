# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""
from cybox.common.vocabs import ObjectRelationship as VocabObjectRelationship
from ce1sus.db.classes.common.basevocab import BaseVocab


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'




class ObjectRelationship(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            0: VocabObjectRelationship.TERM_ALLOCATED,
            1: VocabObjectRelationship.TERM_ALLOCATED_BY,
            2: VocabObjectRelationship.TERM_BOUND,
            3: VocabObjectRelationship.TERM_BOUND_BY,
            4: VocabObjectRelationship.TERM_CHARACTERIZED_BY,
            5: VocabObjectRelationship.TERM_CHARACTERIZES,
            6: VocabObjectRelationship.TERM_CHILD_OF,
            7: VocabObjectRelationship.TERM_CLOSED,
            8: VocabObjectRelationship.TERM_CLOSED_BY,
            9: VocabObjectRelationship.TERM_COMPRESSED,
            10: VocabObjectRelationship.TERM_COMPRESSED_BY,
            11: VocabObjectRelationship.TERM_COMPRESSED_FROM,
            12: VocabObjectRelationship.TERM_COMPRESSED_INTO,
            13: VocabObjectRelationship.TERM_CONNECTED_FROM,
            14: VocabObjectRelationship.TERM_CONNECTED_TO,
            15: VocabObjectRelationship.TERM_CONTAINED_WITHIN,
            16: VocabObjectRelationship.TERM_CONTAINS,
            17: VocabObjectRelationship.TERM_COPIED,
            18: VocabObjectRelationship.TERM_COPIED_BY,
            19: VocabObjectRelationship.TERM_COPIED_FROM,
            20: VocabObjectRelationship.TERM_COPIED_TO,
            21: VocabObjectRelationship.TERM_CREATED,
            22: VocabObjectRelationship.TERM_CREATED_BY,
            23: VocabObjectRelationship.TERM_DECODED,
            24: VocabObjectRelationship.TERM_DECODED_BY,
            25: VocabObjectRelationship.TERM_DECOMPRESSED,
            26: VocabObjectRelationship.TERM_DECOMPRESSED_BY,
            27: VocabObjectRelationship.TERM_DECRYPTED,
            28: VocabObjectRelationship.TERM_DECRYPTED_BY,
            29: VocabObjectRelationship.TERM_DELETED,
            30: VocabObjectRelationship.TERM_DELETED_BY,
            31: VocabObjectRelationship.TERM_DELETED_FROM,
            32: VocabObjectRelationship.TERM_DOWNLOADED,
            33: VocabObjectRelationship.TERM_DOWNLOADED_BY,
            34: VocabObjectRelationship.TERM_DOWNLOADED_FROM,
            35: VocabObjectRelationship.TERM_DOWNLOADED_TO,
            36: VocabObjectRelationship.TERM_DROPPED,
            37: VocabObjectRelationship.TERM_DROPPED_BY,
            38: VocabObjectRelationship.TERM_ENCODED,
            39: VocabObjectRelationship.TERM_ENCODED_BY,
            40: VocabObjectRelationship.TERM_ENCRYPTED,
            41: VocabObjectRelationship.TERM_ENCRYPTED_BY,
            42: VocabObjectRelationship.TERM_ENCRYPTED_FROM,
            43: VocabObjectRelationship.TERM_ENCRYPTED_TO,
            44: VocabObjectRelationship.TERM_EXTRACTED_FROM,
            45: VocabObjectRelationship.TERM_FQDN_OF,
            46: VocabObjectRelationship.TERM_FREED,
            47: VocabObjectRelationship.TERM_FREED_BY,
            48: VocabObjectRelationship.TERM_HOOKED,
            49: VocabObjectRelationship.TERM_HOOKED_BY,
            50: VocabObjectRelationship.TERM_INITIALIZED_BY,
            51: VocabObjectRelationship.TERM_INITIALIZED_TO,
            52: VocabObjectRelationship.TERM_INJECTED,
            53: VocabObjectRelationship.TERM_INJECTED_AS,
            54: VocabObjectRelationship.TERM_INJECTED_BY,
            55: VocabObjectRelationship.TERM_INJECTED_INTO,
            56: VocabObjectRelationship.TERM_INSTALLED,
            57: VocabObjectRelationship.TERM_INSTALLED_BY,
            58: VocabObjectRelationship.TERM_JOINED,
            59: VocabObjectRelationship.TERM_JOINED_BY,
            60: VocabObjectRelationship.TERM_KILLED,
            61: VocabObjectRelationship.TERM_KILLED_BY,
            62: VocabObjectRelationship.TERM_LISTENED_ON,
            63: VocabObjectRelationship.TERM_LISTENED_ON_BY,
            64: VocabObjectRelationship.TERM_LOADED_FROM,
            65: VocabObjectRelationship.TERM_LOADED_INTO,
            66: VocabObjectRelationship.TERM_LOCKED,
            67: VocabObjectRelationship.TERM_LOCKED_BY,
            68: VocabObjectRelationship.TERM_MAPPED_BY,
            69: VocabObjectRelationship.TERM_MAPPED_INTO,
            70: VocabObjectRelationship.TERM_MERGED,
            71: VocabObjectRelationship.TERM_MERGED_BY,
            72: VocabObjectRelationship.TERM_MODIFIED_PROPERTIES_OF,
            73: VocabObjectRelationship.TERM_MONITORED,
            74: VocabObjectRelationship.TERM_MONITORED_BY,
            75: VocabObjectRelationship.TERM_MOVED,
            76: VocabObjectRelationship.TERM_MOVED_BY,
            77: VocabObjectRelationship.TERM_MOVED_FROM,
            78: VocabObjectRelationship.TERM_MOVED_TO,
            79: VocabObjectRelationship.TERM_OPENED,
            80: VocabObjectRelationship.TERM_OPENED_BY,
            81: VocabObjectRelationship.TERM_PACKED,
            82: VocabObjectRelationship.TERM_PACKED_BY,
            83: VocabObjectRelationship.TERM_PACKED_FROM,
            84: VocabObjectRelationship.TERM_PACKED_INTO,
            85: VocabObjectRelationship.TERM_PARENT_OF,
            86: VocabObjectRelationship.TERM_PAUSED,
            87: VocabObjectRelationship.TERM_PAUSED_BY,
            88: VocabObjectRelationship.TERM_PREVIOUSLY_CONTAINED,
            89: VocabObjectRelationship.TERM_PROPERTIES_MODIFIED_BY,
            90: VocabObjectRelationship.TERM_PROPERTIES_QUERIED,
            91: VocabObjectRelationship.TERM_PROPERTIES_QUERIED_BY,
            92: VocabObjectRelationship.TERM_READ_FROM,
            93: VocabObjectRelationship.TERM_READ_FROM_BY,
            94: VocabObjectRelationship.TERM_RECEIVED,
            95: VocabObjectRelationship.TERM_RECEIVED_BY,
            96: VocabObjectRelationship.TERM_RECEIVED_FROM,
            97: VocabObjectRelationship.TERM_RECEIVED_VIA_UPLOAD,
            98: VocabObjectRelationship.TERM_REDIRECTS_TO,
            99: VocabObjectRelationship.TERM_RELATED_TO,
            100: VocabObjectRelationship.TERM_RENAMED,
            101: VocabObjectRelationship.TERM_RENAMED_BY,
            102: VocabObjectRelationship.TERM_RENAMED_FROM,
            103: VocabObjectRelationship.TERM_RENAMED_TO,
            104: VocabObjectRelationship.TERM_RESOLVED_TO,
            105: VocabObjectRelationship.TERM_RESUMED,
            106: VocabObjectRelationship.TERM_RESUMED_BY,
            107: VocabObjectRelationship.TERM_ROOT_DOMAIN_OF,
            108: VocabObjectRelationship.TERM_SEARCHED_FOR,
            109: VocabObjectRelationship.TERM_SEARCHED_FOR_BY,
            110: VocabObjectRelationship.TERM_SENT,
            111: VocabObjectRelationship.TERM_SENT_BY,
            112: VocabObjectRelationship.TERM_SENT_TO,
            113: VocabObjectRelationship.TERM_SENT_VIA_UPLOAD,
            114: VocabObjectRelationship.TERM_SET_FROM,
            115: VocabObjectRelationship.TERM_SET_TO,
            116: VocabObjectRelationship.TERM_SUB_DOMAIN_OF,
            117: VocabObjectRelationship.TERM_SUPRA_DOMAIN_OF,
            118: VocabObjectRelationship.TERM_SUSPENDED,
            119: VocabObjectRelationship.TERM_SUSPENDED_BY,
            120: VocabObjectRelationship.TERM_UNHOOKED,
            121: VocabObjectRelationship.TERM_UNHOOKED_BY,
            122: VocabObjectRelationship.TERM_UNLOCKED,
            123: VocabObjectRelationship.TERM_UNLOCKED_BY,
            124: VocabObjectRelationship.TERM_UNPACKED,
            125: VocabObjectRelationship.TERM_UNPACKED_BY,
            126: VocabObjectRelationship.TERM_UPLOADED,
            127: VocabObjectRelationship.TERM_UPLOADED_BY,
            128: VocabObjectRelationship.TERM_UPLOADED_FROM,
            129: VocabObjectRelationship.TERM_UPLOADED_TO,
            130: VocabObjectRelationship.TERM_USED,
            131: VocabObjectRelationship.TERM_USED_BY,
            132: VocabObjectRelationship.TERM_VALUES_ENUMERATED,
            133: VocabObjectRelationship.TERM_VALUES_ENUMERATED_BY,
            134: VocabObjectRelationship.TERM_WRITTEN_TO_BY,
            135: VocabObjectRelationship.TERM_WROTE_TO,
            }