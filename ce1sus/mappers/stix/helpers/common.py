# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 12, 2014
"""
from datetime import datetime


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def set_properties(instance):
    instance.properties.is_rest_instert = True
    instance.properties.is_proposal = False
    instance.properties.is_web_insert = False
    instance.properties.is_validated = False
    instance.properties.is_shareable = True


def set_extended_logging(instance, user, group):
    if not instance.originating_group:
        instance.originating_group = group
    instance.creator_group = group
    instance.owner_group = user.group

    set_simple_logging(instance, user)


def set_simple_logging(instance, user):
    if not instance.created_at:
        instance.created_at = datetime.utcnow()
    instance.modified_on = datetime.utcnow()
    instance.creator = user
    instance.modifier = user


def extract_uuid(stix_identifier):
    uuid = stix_identifier[-36:]
    return uuid


def make_dict_definitions(definitions):
    result = dict()
    for definition in definitions:
        result[definition.name] = definition
    return result


def relation_definitions():
    return {'Created': 'Specifies that this object created the related object.',
            'Created_By': 'Specifies that this object was created by the related object.',
            'Deleted': 'Specifies that this object deleted the related object.',
            'Deleted_By': 'Specifies that this object was deleted by the related object.',
            'Modified_Properties_Of': 'Specifies that this object modified the properties of the related object.',
            'Properties_Modified_By': 'Specifies that the properties of this object were modified by the related object.',
            'Read_From': 'Specifies that this object was read from the related object.',
            'Read_From_By': 'Specifies that this object was read from by the related object.',
            'Wrote_To': 'Specifies that this object wrote to the related object.',
            'Written_To_By': 'Specifies that this object was written to by the related object.',
            'Downloaded_From': 'Specifies that this object was downloaded from the related object.',
            'Downloaded_To': 'Specifies that this object downloaded the related object.',
            'Downloaded': 'Specifies that this object downloaded the related object.',
            'Downloaded_By': 'Specifies that this object was downloaded by the related object.',
            'Uploaded': 'Specifies that this object uploaded the related object.',
            'Uploaded_By': 'Specifies that this object was uploaded by the related object.',
            'Uploaded_To': 'Specifies that this object was uploaded to the related object.',
            'Received_Via_Upload': 'Specifies that this object received the related object via upload.',
            'Uploaded_From': 'Specifies that this object was uploaded from the related object.',
            'Sent_Via_Upload': 'Specifies that this object sent the related object via upload.',
            'Suspended': 'Specifies that this object suspended the related object.',
            'Suspended_By': 'Specifies that this object was suspended by the related object.',
            'Paused': 'Specifies that this object paused the related object.',
            'Paused_By': 'Specifies that this object was paused by the related object.',
            'Resumed': 'Specifies that this object resumed the related object.',
            'Resumed_By': 'Specifies that this object was resumed by the related object.',
            'Opened': 'Specifies that this object opened the related object.',
            'Opened_By': 'Specifies that this object was opened by the related object.',
            'Closed': 'Specifies that this object closed the related object.',
            'Closed_By': 'Specifies that this object was closed by the related object.',
            'Copied_From': 'Specifies that this object was copied from the related object.',
            'Copied_To': 'Specifies that this object was copied to the related object.',
            'Copied': 'Specifies that this object copied the related object.',
            'Copied_By': 'Specifies that this object was copied by the related object.',
            'Moved_From': 'Specifies that this object was moved from the related object.',
            'Moved_To': 'Specifies that this object was moved to the related object.',
            'Moved': 'Specifies that this object moved the related object.',
            'Moved_By': 'Specifies that this object was moved by the related object.',
            'Searched_For': 'Specifies that this object searched for the related object.',
            'Searched_For_By': 'Specifies that this object was searched for by the related object.',
            'Allocated': 'Specifies that this object allocated the related object.',
            'Allocated_By': 'Specifies that this object was allocated by the related object.',
            'Initialized_To': 'Specifies that this object was initialized to the related object.',
            'Initialized_By': 'Specifies that this object was initialized by the related object.',
            'Sent': 'Specifies that this object sent the related object.',
            'Sent_By': 'Specifies that this object was sent by the related object.',
            'Sent_To': 'Specifies that this object was sent to the related object.',
            'Received_From': 'Specifies that this object was received from the related object.',
            'Received': 'Specifies that this object received the related object.',
            'Received_By': 'Specifies that this object was received by the related object.',
            'Mapped_Into': 'Specifies that this object was mapped into the related object.',
            'Mapped_By': 'Specifies that this object was mapped by the related object.',
            'Properties_Queried': 'Specifies that the object queried properties of the related object.',
            'Properties_Queried_By': 'Specifies that the properties of this object were queried by the related object.',
            'Values_Enumerated': 'Specifies that the object enumerated values of the related object.',
            'Values_Enumerated_By': 'Specifies that the values of the object were enumerated by the related object.',
            'Bound': 'Specifies that this object bound the related object.',
            'Bound_By': 'Specifies that this object was bound by the related object.',
            'Freed': 'Specifies that this object freed the related object.',
            'Freed_By': 'Specifies that this object was freed by the related object.',
            'Killed': 'Specifies that this object killed the related object.',
            'Killed_By': 'Specifies that this object was killed by the related object.',
            'Encrypted': 'Specifies that this object encrypted the related object.',
            'Encrypted_By': 'Specifies that this object was encrypted by the related object.',
            'Encrypted_To': 'Specifies that this object was encrypted to the related object.',
            'Encrypted_From': 'Specifies that this object was encrypted from the related object.',
            'Decrypted': 'Specifies that this object decrypted the related object.',
            'Decrypted_By': 'Specifies that this object was decrypted by the related object.',
            'Packed': 'Specifies that this object packed the related object.',
            'Packed_By': 'Specifies that this object was packed by the related object.',
            'Unpacked': 'Specifies that this object unpacked the related object.',
            'Unpacked_By': 'Specifies that this object was unpacked by the related object.',
            'Packed_From': 'Specifies that this object was packed from the related object.',
            'Packed_Into': 'Specifies that this object was packed into the related object.',
            'Encoded': 'Specifies that this object encoded the related object.',
            'Encoded_By': 'Specifies that this object was encoded by the related object.',
            'Decoded': 'Specifies that this object decoded the related object.',
            'Decoded_By': 'Specifies that this object was decoded by the related object.',
            'Compressed_From': 'Specifies that this object was compressed from the related object.',
            'Compressed_Into': 'Specifies that this object was compressed into the related object.',
            'Compressed': 'Specifies that this object compressed the related object.',
            'Compressed_By': 'Specifies that this object was compressed by the related object.',
            'Decompressed': 'Specifies that this object decompressed the related object.',
            'Decompressed_By': 'Specifies that this object was decompressed by the related object.',
            'Joined': 'Specifies that this object joined the related object.',
            'Joined_By': 'Specifies that this object was joined by the related object.',
            'Merged': 'Specifies that this object merged the related object.',
            'Merged_By': 'Specifies that this object was merged by the related object.',
            'Locked': 'Specifies that this object locked the related object.',
            'Locked_By': 'Specifies that this object was locked by the related object.',
            'Unlocked': 'Specifies that this object unlocked the related object.',
            'Unlocked_By': 'Specifies that this object was unlocked by the related object.',
            'Hooked': 'Specifies that this object hooked the related object.',
            'Hooked_By': 'Specifies that this object was hooked by the related object.',
            'Unhooked': 'Specifies that this object unhooked the related object.',
            'Unhooked_By': 'Specifies that this object was unhooked by the related object.',
            'Monitored': 'Specifies that this object monitored the related object.',
            'Monitored_By': 'Specifies that this object was monitored by the related object.',
            'Listened_On': 'Specifies that this object listened on the related object.',
            'Listened_On_By': 'Specifies that this object was listened on by the related object.',
            'Renamed_From': 'Specifies that this object was renamed from the related object.',
            'Renamed_To': 'Specifies that this object was renamed to the related object.',
            'Renamed': 'Specifies that this object renamed the related object.',
            'Renamed_By': 'Specifies that this object was renamed by the related object.',
            'Injected_Into': 'Specifies that this object injected into the related object.',
            'Injected_As': 'Specifies that this object injected as the related object.',
            'Injected': 'Specifies that this object injected the related object.',
            'Injected_By': 'Specifies that this object was injected by the related object.',
            'Deleted_From': 'Specifies that this object was deleted from the related object.',
            'Previously_Contained': 'Specifies that this object previously contained the related object.',
            'Loaded_Into': 'Specifies that this object loaded into the related object.',
            'Loaded_From': 'Specifies that this object was loaded from the related object.',
            'Set_To': 'Specifies that this object was set to the related object.',
            'Set_From': 'Specifies that this object was set from the related object.',
            'Resolved_To': 'Specifies that this object was resolved to the related object.',
            'Related_To': 'Specifies that this object is related to the related object.',
            'Dropped': 'Specifies that this object dropped the related object.',
            'Dropped_By': 'Specifies that this object was dropped by the related object.',
            'Contains': 'Specifies that this object contains the related object.',
            'Contained_Within': 'Specifies that this object is contained within the related object.',
            'Extracted_From': 'Specifies that this object was extracted from the related object.',
            'Installed': 'Specifies that this object installed the related object.',
            'Installed_By': 'Specifies that this object was installed by the related object.',
            'Connected_To': 'Specifies that this object connected to the related object.',
            'Connected_From': 'Specifies that this object was connected to from the related object.',
            'Sub-domain_Of': 'Specifies that this object is a sub-domain of the related object.',
            'Supra-domain_Of': 'Specifies that this object is a supra-domain of the related object.',
            'Root_Domain_Of': 'Specifies that this object is the root domain of the related object.',
            'FQDN_Of': 'Specifies that this object is an FQDN of the related object.',
            'Parent_Of': 'Specifies that this object is a parent of the related object.',
            'Child_Of': 'Specifies that this object is a child of the related object.',
            'Characterizes': 'Specifies that this object describes the properties of the related object. This is most applicable in cases where the related object is an Artifact Object and this object is a non-Artifact Object.',
            'Characterized_By': 'Specifies that the related object describes the properties of this object. This is most applicable in cases where the related object is a non-Artifact Object and this object is an Artifact Object.',
            'Used': 'Specifies that this object used the related object.',
            'Used_By': 'Specifies that this object was used by the related object.',
            'Redirects_To': 'Specifies that this object redirects to the related object.'}
