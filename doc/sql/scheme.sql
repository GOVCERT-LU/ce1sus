
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `APIErrors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `APIErrors` (
  `APIErrors_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `data` longtext NOT NULL,
  `description` text,
  `created` datetime NOT NULL,
  `creator_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`APIErrors_id`),
  KEY `FK_APIErrors_Groups_user_id` (`creator_id`),
  KEY `FK_APIErrors_Groups_group_id` (`group_id`),
  CONSTRAINT `FK_APIErrors_Groups_group_id` FOREIGN KEY (`group_id`) REFERENCES `Groups_has_Events` (`group_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_APIErrors_Groups_user_id` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `APIErrors` WRITE;
/*!40000 ALTER TABLE `APIErrors` DISABLE KEYS */;
/*!40000 ALTER TABLE `APIErrors` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `AttributeHandlers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `AttributeHandlers` (
  `AttributeHandler_id` int(11) NOT NULL AUTO_INCREMENT,
  `moduleClassName` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `config` int(11) DEFAULT '3',
  `uuid` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`AttributeHandler_id`),
  UNIQUE KEY `moduleClassName_UNIQUE` (`moduleClassName`),
  KEY `fk_AttributeHandlers_1` (`config`),
  CONSTRAINT `fk_AttributeHandlers_1` FOREIGN KEY (`config`) REFERENCES `ce1sus` (`ce1sus_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `AttributeHandlers` WRITE;
/*!40000 ALTER TABLE `AttributeHandlers` DISABLE KEYS */;
INSERT INTO `AttributeHandlers` VALUES (1,'generichandler.GenericHandler',NULL,3,'dea62bf0-8deb-11e3-baa8-0800200c9a66'),
(2,'filehandler.FileWithHashesHandler',NULL,3,'e8b47b60-8deb-11e3-baa8-0800200c9a66'),
(3,'linkhandler.RTHandler',NULL,3,'f1509d30-8deb-11e3-baa8-0800200c9a66'),
(5,'linkhandler.CVEHandler',NULL,3,'04cda0b0-8dec-11e3-baa8-0800200c9a66'),
(6,'multiplegenerichandler.MultipleGenericHandler',NULL,3,'08645c00-8dec-11e3-baa8-0800200c9a66'),
(7,'filehandler.FileHandler',NULL,3,'0be5e1a0-8dec-11e3-baa8-0800200c9a66'),
(8,'datehandler.DateHandler',NULL,3,'11406d00-8dec-11e3-baa8-0800200c9a66'),
(9,'cbvaluehandler.CBValueHandler',NULL,3,'141dea70-8dec-11e3-baa8-0800200c9a66'),
(10,'texthandler.TextHandler',NULL,3,'1a8ec7d0-8dec-11e3-baa8-0800200c9a66'),
(11,'linkhandler.LinkHander',NULL,3,'1e18d8f0-8dec-11e3-baa8-0800200c9a66');
/*!40000 ALTER TABLE `AttributeHandlers` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Attribute_Object_Relations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Attribute_Object_Relations` (
  `AOR_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `ref_attribute_id` bigint(20) NOT NULL,
  `attribute_id` bigint(20) NOT NULL,
  `ref_object_id` bigint(20) NOT NULL,
  PRIMARY KEY (`AOR_id`),
  UNIQUE KEY `UNQ_AOR_attribID_refAttribID` (`ref_object_id`,`ref_attribute_id`),
  KEY `IDX_AOR_Attribtues_ref_attribute_id` (`ref_attribute_id`),
  KEY `IDX_AOR_Attribtues_attribute_id` (`attribute_id`),
  KEY `IDX_AOR_Objects_obejct_id` (`ref_object_id`),
  CONSTRAINT `FK_AOR_Attribtues_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_AOR_Attribtues_ref_attribute_id` FOREIGN KEY (`ref_attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_AOR_Objects_obejct_id` FOREIGN KEY (`ref_object_id`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='The ref_object_id is just to keep the relations unique to pr';
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Attribute_Object_Relations` WRITE;
/*!40000 ALTER TABLE `Attribute_Object_Relations` DISABLE KEYS */;
/*!40000 ALTER TABLE `Attribute_Object_Relations` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Attributes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Attributes` (
  `attribute_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `def_attribute_id` bigint(20) NOT NULL,
  `object_id` bigint(20) NOT NULL,
  `creator_id` bigint(20) NOT NULL,
  `modifier_id` bigint(20) DEFAULT NULL,
  `created` datetime NOT NULL,
  `modified` datetime DEFAULT NULL,
  `ioc` int(1) NOT NULL DEFAULT '0',
  `code` int(1) DEFAULT NULL,
  `parent_attr_id` bigint(20) DEFAULT NULL,
  `multiValue` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`attribute_id`),
  KEY `IDX_attr_def_attribute_id` (`def_attribute_id`),
  KEY `IDX_attr_object_id` (`object_id`),
  KEY `IDX_Attr_Objects_object_id` (`object_id`),
  KEY `IDX_Attr_creator_id` (`creator_id`),
  KEY `IDX_Attr_modifier_id` (`modifier_id`),
  KEY `IDX_Attr_id_sharable` (`attribute_id`),
  KEY `FK_Attr_Object_Object_id` (`object_id`),
  KEY `FK_Attr_parent_id_attr_id` (`parent_attr_id`),
  CONSTRAINT `FK_Attr_DAttr_attribute_id` FOREIGN KEY (`def_attribute_id`) REFERENCES `DEF_Attributes` (`def_attribute_id`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `FK_Attr_Object_Object_id` FOREIGN KEY (`object_id`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Attr_parent_id_attr_id` FOREIGN KEY (`parent_attr_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `FK_Attr_Users_creator_id_user_id` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Attr_Users_modifier_id_user_id` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Attributes` WRITE;
/*!40000 ALTER TABLE `Attributes` DISABLE KEYS */;
/*!40000 ALTER TABLE `Attributes` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Comments` (
  `comment_id` int(11) NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) NOT NULL,
  `comment` mediumtext CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `created` datetime NOT NULL,
  `creator_id` bigint(20) NOT NULL,
  `modifier_id` bigint(20) DEFAULT NULL,
  `modified` datetime DEFAULT NULL,
  PRIMARY KEY (`comment_id`),
  KEY `IDX_comments_event_id` (`event_id`),
  KEY `IDX_Comments_User_creator_user_id` (`creator_id`),
  KEY `IDX_Comments_User_modifier_user_id` (`modifier_id`),
  CONSTRAINT `FK_Comments_User_creator_user_id` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Comments_User_modifier_user_id` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_events_comments_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Comments` WRITE;
/*!40000 ALTER TABLE `Comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `Comments` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `DEF_Attributes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DEF_Attributes` (
  `def_attribute_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `description` mediumtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `regex` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '^.*$',
  `classIndex` int(11) NOT NULL DEFAULT '0',
  `handlerIndex` int(11) NOT NULL DEFAULT '0',
  `deletable` int(1) NOT NULL DEFAULT '1',
  `sharable` int(1) NOT NULL DEFAULT '0',
  `relationable` int(1) NOT NULL DEFAULT '0',
  `chksum` varchar(45) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`def_attribute_id`),
  UNIQUE KEY `chksum_UNIQUE` (`chksum`),
  KEY `IDX_def_attributes_name` (`name`),
  KEY `IDX_def_attributes_chksum` (`chksum`),
  KEY `FK_DEF_Attr_AttrHandler_attibute_id` (`handlerIndex`),
  CONSTRAINT `FK_DEF_Attr_AttrHandler_attibute_id` FOREIGN KEY (`handlerIndex`) REFERENCES `AttributeHandlers` (`AttributeHandler_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=668 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `DEF_Attributes` WRITE;
/*!40000 ALTER TABLE `DEF_Attributes` DISABLE KEYS */;
INSERT INTO `DEF_Attributes` VALUES (1,'hash_md5','md5 hash of a file','^[0-9a-fA-F]{32}$',1,6,1,1,1,'8a3975c871c6df7ab9a890b8f0fd1fb6e4e6556e'),
(2,'hash_sha1','sha1 hash of a file','^[0-9a-fA-F]{40}$',1,6,1,1,1,'dc4e8dd46d60912abbfc3dd61c16ef1f91414032'),
(3,'hash_sha256','sha256 hash of a file','^[0-9a-fA-F]{64}$',1,6,1,1,1,'1350a97f87dfb644437814905cded4a86e58a480'),
(4,'hash_sha384','sha384 hash of a file','^[0-9a-fA-F]{96}$',1,6,1,1,1,'40c1ce5808fa21c6a90d27e4b08b7b7171a23b92'),
(5,'hash_sha512','sha512 hash of a file','^[0-9a-fA-F]{128}$',1,6,1,1,1,'6d2cf7df2da95b6f878a9be2b754de1e6d1f6224'),
(6,'hash_ssdeep','ssdeep hash of a file','^\\d+:[a-zA-Z0-9+]+:[a-zA-Z0-9+]+$',1,6,1,1,1,'579955964b6950f03ef86fe4b38cd065800127b6'),
(7,'file_name','The file_name field specifies the name of the file.','^.+$',1,6,1,1,0,'beba24a09fe92b09002616e6d703b3a14306fed1'),
(8,'size_in_bytes','The size_in_bytes field specifies the size of the file, in bytes.','^\\d+$',3,1,1,1,0,'9d99d7a9a888a8bfd0075090c33e6a707625673a'),
(9,'magic_number','The magic_number specifies the particular magic number (typically a hexadecimal constant used to identify a file format) corresponding to the file, if applicable.','^.+$',1,1,1,1,0,'75f5ca9e1dcfd81cdd03751a7ee45a1ef716a05d'),
(10,'reference_internal_identifier','Holds a reference to an internal ID number.','^\\d+$',3,3,1,1,0,'616cdf707dd0a11453502f0f1cc8f29cf0e30b87'),
(11,'vulnerability_cve','CVE reference to a known vulnerability','^CVE-\\d{4}-\\d{4,}$',1,5,1,1,1,'3e1bfba5cd1f0f691f9228a421a96696e4ceec5c'),
(12,'raw_file','The raw file data','^.+$',1,2,1,0,0,'03c710c3265fe4488f559ebda358beb63525bda3'),
(13,'raw_document_file','The raw document (non malicious file)','^.+$',1,7,1,1,0,'1ebe4177af30053b59b349611de8b83874552ccf'),
(14,'hostname','Fully qualified domain name','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,6,1,1,1,'304b44f1d241b7b97a2d658cddf798042d416ca8'),
(15,'description','Contains free text description for an object','^.+$',0,10,1,1,0,'408ae68eee4c289d0aac277963787374ff5ad137'),
(16,'comment','Holds free text for comments about objects and event.','^.+$',0,10,1,0,0,'42dac9882bc6ab5e3c3d52cf5a7019b4c84ed20f'),
(17,'is_malicious','Boolean to identify malicious objects','^yes$|^no$',1,9,1,1,0,'45abf1f8ae6f94c05c68d0627aca6aaaee157fb6'),
(18,'malware_file_type','dropper, trojan, banking trojan, RAT, rogue document, phishing document,....','^virus$|^trojan$|^dropper$|^malware$|^rootkit$|^keylogger$|^worm$',1,9,1,1,0,'1315318855c519151051865b89daf21150ee349f'),
(19,'file_full_path','The File path including the file name.','^.+$',1,1,1,1,0,'0cebf13a5cc2973ccc3b50981a27a033f0ab0d6a'),
(20,'file_extension','The File_Extension field specifies the file extension of the file.','^.+$',1,1,1,1,0,'2032d235730e19920a156a0a800e12540ba25359'),
(21,'file_format','The File_Format field specifies the particular file format of the file, most typically specified by a tool such as the UNIX file command.','^.+$',1,1,1,1,0,'6bb0adbd2fcbd13548e45565da4f1c48b71ad659'),
(22,'digital_signature','The Digital_Signatures field is optional and captures one or more digital signatures for the file.','^.+$',0,10,1,1,1,'89bf3463897168294b65c622e5f910c734c393bf'),
(23,'file_modified_time','The Modified_Time field specifies the date/time the file was last modified.','^.+$',2,8,1,1,0,'46a80748b358f9f33a49bdaab613c6e7f0997037'),
(24,'file_accessed_datetime','The Accessed_Time field specifies the date/time the file was last accessed.','^.+$',2,8,1,1,0,'a3fdb385ba736bc39ee50a56cdfea72a9e8e24dc'),
(25,'file_created_datetime','The Created_Time field specifies the date/time the file was created.','^.+$',2,8,1,1,0,'d1bff3999396458e2472df468bc196ce632b48e2'),
(26,'packer','The Packer_List field specifies any packers that the file may be packed with. The term \'packer\' here refers to packers, as well as things like archivers and installers.','^.+$',1,1,1,1,0,'25137c646a774123e59783860251c1a628bb5273'),
(27,'peak_entropy','The Peak_Entropy field specifies the calculated peak entropy of the file.','^[\\d]{1,}$',3,1,1,1,0,'7f15607b49828b556527ad86c076bf7791c0ae37'),
(28,'encryption_mechanism','The encryption_mechanism field is optional and specifies the protection/encryption algorithm utilized to protect the Raw_Artifact content.','^.+$',0,10,1,1,0,'e11318438c15da0fd5fcb8530856c694b9cc1ae1'),
(29,'discovery_method','The Discovery_Method field is intended to characterize the method and/or tool used to discover the object.','^.+$',0,10,1,1,0,'14120ef941150db0c4e8a2c98b185a38d1f5535c'),
(30,'vulnerability_free_text','Free text description for a vulnerability','^.+$',0,10,1,1,0,'98dd154b5d2fcf245666bacb2fbcda6fcb350478'),
(31,'reference_url','URL pointing to online information','^.+$',1,11,1,1,0,'8c251c717b842f29fa3411219c41b4d1d532894a'),
(32,'reference_free_text','Free text used to give reference information.','^.+$',0,10,1,1,0,'204a2682e62980f6659d3497d87e2daea4fe5218'),
(33,'analysis_free_text','A free text analysis for the object. dd','^.+$',0,10,1,1,0,'452fba47ced447f27f20db54bfe70370447ff5c1'),
(34,'information_source','Free text holding information about the source of an information (e.g where did a document come from).','^.+$',0,10,1,1,0,'56b96a943ae84aa93f4327ad5bff2b6bf34252c4'),
(35,'reference_internal_case','Holds a reference to an internal case to which the event is related.','^.+$',1,1,1,1,0,'bd5c60354d04682952254f0ad7b92ffa94b88f83'),
(36,'reference_external_identifier','Contains an external identifier for the event','^.+$',1,1,1,0,1,'a1833102fe930fd33c55f63f0fefa65e8e94e38c'),
(37,'creation_datetime','The creation time stamp of an object','^.+$',2,8,1,1,0,'7516648da395d83038eeebf09e9b1d1c52d6520f'),
(38,'raw_pcap_file','The raw file data','^.+$',1,7,1,1,0,'187872308675251e2df91cbff7d02c162d99b778'),
(39,'email_attachment_file_name','The Attachments field specifies any files that were attached to the email message. It imports and uses the CybOX FileObjectType from the File_Object to do so.','^.+$',1,1,1,1,0,'4fb9c6a95cef16b5b91084fef34648266cb0cfa7'),
(40,'email_bcc','The BCC field specifies the email addresses of any recipients that were included in the blind carbon copy header of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,6,1,1,0,'79cbb7999bc6a4c75d3ac426b4ea98b90d6dd5b1'),
(41,'email_cc','The CC field specifies the email addresses of any recipients that were included in the carbon copy header of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,6,1,1,0,'cdb410fab4a9bb160da0e266e185a8d9109310ff'),
(42,'email_content_type','The Content-Type field specifies the internet media, or MIME, type of the email message content.','^.+$',1,1,1,1,0,'044cc82f1057d86ba6e468a534d6fef72989a3f3'),
(43,'email_errors_to','The Errors_To field specifies the entry in the (deprecated) errors_to header of the email message.','^.+$',1,1,1,1,0,'6a2417ffe4b6f05fa8bf8604f1076c67b80957ea'),
(44,'email_from','The From field specifies the email address of the sender of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,6,1,1,1,'59cf7eefc377bdc51683521b5f340c40a55c9086'),
(45,'email_in_reply_to','The In_Reply_To field specifies the message ID of the message that this email is a reply to.','^.+$',1,1,1,1,0,'feeef985f623f68a5b7160a22fa306c735a1a426'),
(46,'email_message_id','The Message_ID field specifies the automatically generated ID of the email message.','^.+$',1,1,1,1,0,'08d3555ef4c29fe2ad8e5e916dc20fadd2b1a963'),
(47,'email_mime_version','The MIME-Version field specifies the version of the MIME formatting used in the email message.','^.+$',1,1,1,1,0,'9969f591aaae20457c0d7a90a02a948ea115df3d'),
(48,'email_raw_body','The Raw_Body field specifies the complete (raw) body of the email message.','^.+$',1,7,1,0,0,'27798f7502c9b45329ab14a9a2c797613f21fb77'),
(49,'email_raw_header','The Raw_Header field specifies the complete (raw) headers of the email message.','^.+$',0,10,1,0,0,'29c34a2e442394ab031e94613dd46d907a022547'),
(50,'email_receive_datetime','The Date field specifies the date/time that the email message was received by the mail server.','^.+$',2,8,1,1,0,'b00422663b098074b02b1c252f8464cf03c4dafc'),
(51,'email_relay_ip','This attribute hold the IP address of an MTA used to deliver the mail.','^.+$',1,1,1,1,1,'71e951d917852abe8039abaecfc6ee7805f8cea9'),
(52,'email_reply_to','The Reply_To field specifies the email address that should be used when replying to the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,1,1,1,0,'987f1f8263d855713ebd84c6899640875b1ac719'),
(53,'email_send_datetime','The Date field specifies the date/time that the email message was sent.','^.+$',2,8,1,1,0,'3555502fb6a76e5951da4a8fdc3a90173c4da587'),
(54,'email_sender','The Sender field specifies the email address of the sender who is acting on behalf of the author listed in the From: field','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,1,1,1,0,'94d4c5f854c43acd950d27e0244b650e5767987e'),
(55,'email_server','The Email_Server field is optional and specifies the relevant email server.','^.+$',1,1,1,1,0,'39b2b50c988c163284c966797a605d9fda959cdc'),
(56,'email_subject','The Subject field specifies the subject (a brief summary of the message topic) of the email message.','^.+$',1,1,1,1,0,'2ce464780bd3f8c2215849fd883bf236003d2778'),
(57,'email_to','The To field specifies the email addresses of the recipients of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,6,1,1,0,'e56afb60554c27a596338fb54862bb9f17e5f77f'),
(58,'email_x_mailer','The X-Mailer field specifies the software used to send the email message. This field is non-standard.','^.+$',1,1,1,1,0,'0620ff7527bb1da229bfe531a331178140482bb1'),
(59,'email_x_originating_ip','The X-Originating-IP field specifies the originating IP Address of the email sender, in terms of their connection to the mail server used to send the email message. This field is non-standard.','^.+$',1,1,1,1,0,'21ab432d3a8e45268ad496f8f6dad3babf32a6d4'),
(60,'code_language','The code_language field refers to the code language used in the code characterized in this field.','^.+$',1,1,1,1,0,'e3a69fa7854ae151e85e80c458a9545ceffdd84a'),
(61,'processor_family','The processor_family field specifies the class of processor that the code snippet is targeting. Possible values: x86-32, x86-64, IA-64, PowerPC, ARM, Alpha, SPARC, z/Architecture, eSi-RISC, MIPS, Motorola 68k, Other.','^.+$',1,1,1,1,0,'feef81f0850187fcecb768a0a0b3901280e01a78'),
(62,'targeted_platform','The Targeted_Platforms field specifies a list platforms that this code is targeted for.','^.+$',1,1,1,1,0,'95a363b06982e2b12dfa74bc3dfaaad7fcc67b4f'),
(63,'antivirus_record','The results of one or many antivirus scans for an object. This is a multiline csv value (datetime, engine, result, threat name).','^.+$',1,6,1,1,0,'f0816b53c7dd1f14a5127bf802a5a16f73694e11'),
(64,'ida_pro_file','An IDA pro file.','^.+$',1,7,1,1,0,'56e75ee498e22a82f5d8ff7b4b5ce66cc3e78214'),
(65,'log_records','Free text for storing log information.','^.+$',0,10,1,1,0,'4f5eca66b72a03d44e5663da38147dc55ea7764a'),
(66,'whois','Whois network information','^.+$',0,10,1,1,0,'34bbb09bca2a02158170067847f3447a6c99a188'),
(67,'asn','The asn value specifies an identifier for an autonomous system number.','^.+$',1,1,1,1,1,'f58374950a2493f6c65628853c53c8f3d348b652'),
(68,'domain','Contains a fully qualified domain name','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,6,1,1,1,'90828f4af42b665fb1a426b3a887019b0da61eb4'),
(69,'file_content_pattern','Contains a pattern that can be found in the raw file data','^.+$',1,1,1,1,0,'ae7bb656b0f3c66a349c713c9f8f27f111916c26'),
(70,'file_full_path_pattern','A pattern that matches the full path of a file (including its file name).','^.+$',1,1,1,1,0,'f930e4d37fa2a8ef374bc61e1f8cf7c8d632d96c'),
(71,'file_name_pattern','A pattern that matches the file name','^.+$',1,1,1,1,0,'d057a7295b689bc157701a9dbd5915c3787eea95'),
(72,'hostname_c&c','Fully qualified domain name of a host hosting a command and control server','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,6,1,1,1,'1ddc87499788f4e241a00dc109ff92532b00059f'),
(73,'ids_rules','Holds IDS rules. These rules need to be prefixed with the used format (e.g. snort).','^.+$',0,6,1,1,0,'d66dc46c3d6c003104e56bfb7510239416d6588f'),
(74,'ipv4_addr','The IPv4-addr value specifies an IPV4 address.','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$',1,6,1,1,1,'cdfd7afaf21cede78d8d09e36aae52c82ebe1f69'),
(75,'ipv4_addr_c&c','IPv4 address hosting a command and control server','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$',1,6,1,1,1,'4832af9c21e301a5c957576f39764b715aa08cbf'),
(76,'ipv4_net','IPv4 CIDR block','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}/\\d{1,2}$',1,6,1,1,0,'d2c4f5ac5fe93b08a8527734ddde58ba84fa8aac'),
(77,'ipv6_addr','The IPv6-addr value specifies an IPv6 address.','^.+$',1,6,1,1,1,'7fa231f4cd8e63ddd64a3ca8d2e3e0184290e6c2'),
(78,'ipv6_addr_c&c','IPv6 address hosting a command and control server','^.+$',1,6,1,1,1,'c2ee2f470c24a5b99ae0d5b0f46236746a40ef2a'),
(79,'ipv6_net','IPv6 sub-network','^.+$',1,6,1,1,0,'fa08732c96cbae117fb166b44dc6d95a040182a7'),
(80,'mutex','The Mutex object is intended to characterize generic mutual exclusion (mutex) objects.','^.+$',1,6,1,1,1,'6b6612510088b40d84d4efa687e03b4cf9ba476f'),
(81,'open_ioc_definition','Hold open IOC definitions.','^.+$',1,7,1,1,0,'4098d7b47789dbad918d1681305c61ff760d4fff'),
(82,'traffic_content_pattern','Pattern matching network traffic content.','^.+$',1,1,1,1,0,'cc35a2e8d1fe7b658f5124797572d6041abca614'),
(83,'url','Holds a complete URL (e.g. http://www.govcert.lu/en/index.hmtl)','^.+$',1,6,1,1,0,'ed3f523221541f4318716ace3c51ebd44ef593e9'),
(84,'url_path','Holds only the path part of an URL. (e.g. /en/index.html)','^.+$',1,6,1,1,0,'8839eb1c1aec5a82fe09e9b0a29ef007395ef7ad'),
(85,'url_pattern','Holds a pattern that matches URL.','^.+$',1,6,1,1,0,'97992b35806bb95123fe5698eb739419d556ccf7'),
(86,'win_registry_key','The WindowsRegistryObjectType type is intended to characterize Windows registry objects, including Keys and Key/Value pairs.','^.+$',0,10,1,1,1,'2687dcd982aced325ba5476d19c100897ab9df47'),
(87,'yara_rule','Holds YARA rules used to identify and classify malware samples.','^.+$',0,10,1,1,1,'98fc9e6a364ad850765c20a0eb55ad7b2df7b3ee'),
(88,'mime_type','mime_type','^.+$',0,1,1,1,0,'b7cc0982923b2a26f8665b44365b590400cff9bf'),
(89,'compromized_hostname','compromized_hostname','^.+$',1,1,1,1,1,'62f87cdb0deddb0359a1ff0cc06eb0446f10eb11'),
(90,'ipv4_addr_phishingSite','ipv4_addr_phishingSite','^.+$',1,1,1,1,1,'d5c2621b1861a94a654149c745f81a291b60a2e2'),
(91,'ip_port','IP port','^[\\d]{1,}$',3,1,1,1,0,'5b64983419e14b6e14b5c1b7dc88df8e519a5650'),
(101,'ip_protocol','IP protocol','^tcp$|^udp$|^icmp$',1,9,1,1,0,'1b451a5443e2fa80e03757dddc78b3d6471d425c'),
(111,'file_id','File description as returned by unix \"file\" command','^.+$',1,1,1,1,0,'745af7b7cf3bf4c5a0b2b04ad9cd2c9b8da39fc1'),
(121,'xor_pattern','The xor_pattern field contains a hexadecimal-character hex string','^(?:0x)?[a-fA-F0-9-:]+$',1,6,1,1,1,'b2fa4aa6d962c9defb974e355910505e6688f2ed'),
(131,'username','The Username field specifies the particular username of the user account','^[a-zA-Z0-9._-]+$',1,1,1,1,0,'7deec7c49b69c77efecaa39ea3e72b5d043afd6a'),
(141,'password','Passwords are clear text stings used to authenticated a user','^.+$',1,1,1,1,1,'8bda7d81460bea54192da176f1700b9c313aa962'),
(151,'full_name','The Full_Name field specifies the full name of the user','^.+$',1,1,1,0,0,'e40de7dccb534b85f9db42e5b990b8a06a5027cf'),
(161,'encryption_key','Clear text stings used along with an encryption algorithm in order to cypher data','^.+$',0,10,1,1,1,'a73a20f8e9d91b906683e35108c28f2770923606'),
(171,'email_address','The associated email address','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,6,1,1,0,'c98c68de457bcadfdeb6347b1add00f147b87320'),
(181,'http_user_agent','HTTP defines methods (sometimes referred to as verbs) to indicate the desired action to be performed on the identified resource. What this resource represents, whether pre-existing data or data that is generated dynamically, depends on the implementation of the server. Often, the resource corresponds to a file or the output of an executable residing on the server.','^.+$',1,1,1,1,0,'0343b882c2156d8a62f3d5ab9dea5523af2cf8fb'),
(191,'http_method','The Hypertext Transfer Protocol (HTTP) identifies the client software originating the request, using a \"User-Agent\" header, even when the client is not operated by a user.','^GET$|^HEAD$|^POST$|^PUT$|^DELETE$|^TRACE$|^OPTIONS$|^CONNECT$|^PATCH$',1,9,1,1,0,'94c4b13a5acca85cc227ee43aa958f67151152d1'),
(201,'http_version','HTTP uses a \"<major>.<minor>\" numbering scheme to indicate versions of the protocol.','^\\d+\\.\\d+$',1,1,1,1,0,'16fbca2bbca4eedfd50b6400c7b21412b6bdcfa6'),
(214,'Test_attribute','test description','^.+$',0,10,1,1,0,'13c857889d8e393be8a2961e868e21730b330f3e'),
(667,'memory_pattern','Contains a memory pattern','^.+$',0,10,1,1,0,'1204c194109b6716fcdae9b6e03f0614e8248843');
/*!40000 ALTER TABLE `DEF_Attributes` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `DEF_Objects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DEF_Objects` (
  `def_object_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `description` mediumtext CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `chksum` varchar(45) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `sharable` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`def_object_id`),
  UNIQUE KEY `chksum_UNIQUE` (`chksum`),
  KEY `IDX_def_objects_chksum` (`chksum`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `DEF_Objects` WRITE;
/*!40000 ALTER TABLE `DEF_Objects` DISABLE KEYS */;
INSERT INTO `DEF_Objects` VALUES (1,'generic_file','Generic file','7a6272431a4546b99081d50797201ddc25a38f4c',1),
(2,'reference_document','reference_document','dee32f113d56844d27b15c236d7fb66afdbef085',1),
(3,'references','references','f4c9a69f715c3c60aa2fc15795b3834d2dc51b9d',1),
(4,'network_traffic','network_traffic','468bc69e746c453763f1c1ed644742628ca4bb38',1),
(5,'email','email','a88b7dcd1a9e3e17770bbaa6d7515b31a2d7e85d',1),
(6,'executable_file','executable_file\r\n\r\nThis includes all kind of compiled code','f82c52727e0d45c79cd3810704314d6c08fed47a',1),
(7,'forensic_records','forensic_records','fc771f573182da23515be31230903ec2c45e8a3a',1),
(8,'ioc_records','ioc_records','4ffb865c9d6950a643fd29d7170e849b1d077b9a',1),
(9,'malicious_website','malicious_website','e34bafaf6afd4a30188913d181fce87d85fcf037',1),
(10,'source_code','source_code\r\n\r\nThis includes all uncompiled code','0c4fa34ab948d93a78795a5301c11f772a635620',1),
(11,'user_account','User profile','4ab2df0a57a74fdf904e0e27086676ed9c4c3cdf',1),
(16,'test_object','test description sdf 2','fc20ab0360ba35c4e29401c286d995b761a3cfc0',1);
/*!40000 ALTER TABLE `DEF_Objects` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `DObj_has_DAttr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DObj_has_DAttr` (
  `def_object_id` bigint(20) NOT NULL,
  `def_attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`def_object_id`,`def_attribute_id`),
  KEY `IDX_DOhDA_def_object_id` (`def_attribute_id`),
  KEY `IDX_DOhDA_def_attribute_id` (`def_object_id`),
  CONSTRAINT `FK_DAttrs_DObjs_DAttrID` FOREIGN KEY (`def_attribute_id`) REFERENCES `DEF_Attributes` (`def_attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_DObjs_DAttrs_DOId` FOREIGN KEY (`def_object_id`) REFERENCES `DEF_Objects` (`def_object_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `DObj_has_DAttr` WRITE;
/*!40000 ALTER TABLE `DObj_has_DAttr` DISABLE KEYS */;
INSERT INTO `DObj_has_DAttr` VALUES (1,1),
(5,1),
(6,1),
(8,1),
(10,1),
(1,2),
(5,2),
(6,2),
(8,2),
(10,2),
(1,3),
(5,3),
(6,3),
(8,3),
(10,3),
(1,4),
(5,4),
(6,4),
(8,4),
(10,4),
(1,5),
(5,5),
(6,5),
(8,5),
(1,6),
(2,6),
(6,6),
(8,6),
(10,6),
(1,7),
(6,7),
(8,7),
(10,7),
(1,8),
(6,8),
(10,8),
(1,9),
(6,9),
(10,9),
(3,10),
(1,11),
(3,11),
(5,11),
(6,11),
(9,11),
(10,11),
(1,12),
(6,12),
(1,13),
(2,13),
(6,13),
(10,13),
(8,14),
(9,14),
(1,15),
(2,15),
(3,15),
(4,15),
(6,15),
(7,15),
(8,15),
(9,15),
(10,15),
(11,15),
(1,16),
(2,16),
(3,16),
(4,16),
(6,16),
(7,16),
(8,16),
(9,16),
(10,16),
(11,16),
(1,17),
(5,17),
(6,17),
(10,17),
(1,18),
(6,18),
(10,18),
(1,19),
(6,19),
(8,19),
(10,19),
(1,20),
(6,20),
(10,20),
(1,21),
(6,21),
(10,21),
(1,22),
(6,22),
(8,22),
(10,22),
(1,23),
(6,23),
(10,23),
(1,24),
(6,24),
(10,24),
(1,25),
(6,25),
(10,25),
(1,26),
(6,26),
(10,26),
(1,27),
(6,27),
(10,27),
(1,28),
(6,28),
(10,28),
(1,29),
(4,29),
(6,29),
(10,29),
(1,30),
(3,30),
(5,30),
(6,30),
(9,30),
(10,30),
(1,31),
(2,31),
(3,31),
(4,31),
(5,31),
(6,31),
(7,31),
(8,31),
(9,31),
(10,31),
(1,32),
(2,32),
(3,32),
(4,32),
(5,32),
(6,32),
(7,32),
(8,32),
(9,32),
(10,32),
(1,33),
(4,33),
(5,33),
(6,33),
(7,33),
(9,33),
(10,33),
(3,35),
(3,36),
(4,37),
(4,38),
(5,39),
(8,39),
(5,40),
(5,41),
(5,42),
(5,43),
(5,44),
(8,44),
(5,45),
(5,46),
(5,47),
(5,48),
(5,49),
(5,50),
(5,51),
(5,52),
(5,53),
(5,54),
(5,55),
(5,56),
(8,56),
(5,57),
(5,58),
(5,59),
(6,60),
(10,60),
(6,61),
(10,61),
(6,62),
(10,62),
(7,63),
(7,64),
(7,65),
(7,66),
(9,66),
(8,67),
(8,68),
(8,69),
(1,70),
(6,70),
(8,70),
(1,71),
(6,71),
(8,71),
(8,72),
(8,73),
(8,74),
(9,74),
(8,75),
(8,76),
(8,77),
(9,77),
(8,78),
(8,79),
(8,80),
(8,81),
(8,82),
(8,83),
(9,83),
(11,83),
(8,84),
(8,85),
(8,86),
(1,88),
(6,88),
(8,91),
(8,101),
(1,111),
(6,111),
(8,121),
(11,131),
(8,141),
(11,141),
(11,151),
(8,161),
(11,171),
(8,181),
(8,191),
(8,201),
(8,667);
/*!40000 ALTER TABLE `DObj_has_DAttr` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `DateValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DateValues` (
  `DateValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` datetime DEFAULT NULL,
  `attribute_id` bigint(20) NOT NULL,
  `event_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`DateValue_id`),
  KEY `IDX_DateValues_attribute_id` (`attribute_id`),
  KEY `IDX_DateValues_Value` (`value`),
  KEY `attribute_id` (`attribute_id`),
  KEY `IDX_DateValues_event_event_id` (`event_id`),
  CONSTRAINT `FK_DateValues_Attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_DateValues_event_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `DateValues` WRITE;
/*!40000 ALTER TABLE `DateValues` DISABLE KEYS */;
/*!40000 ALTER TABLE `DateValues` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `EventRelations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `EventRelations` (
  `EventRelations_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) NOT NULL,
  `rel_event_id` bigint(20) NOT NULL,
  `attribute_id` bigint(20) NOT NULL,
  `rel_attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`EventRelations_id`),
  KEY `IDX_ER_EVENT_event_id` (`event_id`),
  KEY `IDX_ER_EVENT_rel_event_id` (`rel_event_id`),
  KEY `idx_EventRelations_attr_attribute_id` (`attribute_id`),
  KEY `idx_EventRelations_attr_rel_attribute_id` (`rel_attribute_id`),
  CONSTRAINT `FK_ER_EVENT_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_ER_EVENT_rel_event_id` FOREIGN KEY (`rel_event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_EventRelations_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_EventRelations_attr_rel_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Nerf` FOREIGN KEY (`rel_attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `EventRelations` WRITE;
/*!40000 ALTER TABLE `EventRelations` DISABLE KEYS */;
/*!40000 ALTER TABLE `EventRelations` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Events` (
  `event_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `title` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `created` datetime NOT NULL,
  `first_seen` datetime NOT NULL,
  `last_seen` datetime DEFAULT NULL,
  `modified` datetime DEFAULT NULL,
  `published` tinyint(1) NOT NULL DEFAULT '0',
  `status_id` int(11) NOT NULL DEFAULT '0',
  `tlp_level_id` int(1) NOT NULL DEFAULT '3',
  `risk_id` int(11) NOT NULL,
  `analysis_status_id` int(11) NOT NULL,
  `creator_id` bigint(20) NOT NULL,
  `modifier_id` bigint(20) DEFAULT NULL,
  `uuid` varchar(45) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `creatorGroup` int(11) NOT NULL,
  `code` int(1) NOT NULL,
  PRIMARY KEY (`event_id`),
  KEY `IDX_Events_uuid` (`uuid`),
  KEY `IDK_Events_creator_id` (`creator_id`),
  KEY `IDX_Events_modifier_ID` (`modifier_id`),
  KEY `IDX_Events_creatorGroup` (`creatorGroup`),
  CONSTRAINT `FK_Events_Groups_creator` FOREIGN KEY (`creatorGroup`) REFERENCES `Groups` (`group_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Events_User_creator_user_ID` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Events_User_modifier_user_ID` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Events` WRITE;
/*!40000 ALTER TABLE `Events` DISABLE KEYS */;
/*!40000 ALTER TABLE `Events` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Events_has_Objects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Events_has_Objects` (
  `event_id` bigint(20) NOT NULL,
  `object_id` bigint(20) NOT NULL,
  PRIMARY KEY (`event_id`,`object_id`),
  KEY `IDX_EhO_event_id` (`object_id`),
  KEY `IDX_EhO_object_id` (`event_id`),
  CONSTRAINT `fk_Eho_Event_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_Eho_Object_object_id` FOREIGN KEY (`object_id`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Events_has_Objects` WRITE;
/*!40000 ALTER TABLE `Events_has_Objects` DISABLE KEYS */;
/*!40000 ALTER TABLE `Events_has_Objects` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `ExtCe1sus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ExtCe1sus` (
  `extce1sus_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `url` varchar(255) NOT NULL,
  `apikey` varchar(45) NOT NULL,
  `last_full_sync` datetime DEFAULT NULL,
  `name` varchar(45) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`extce1sus_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `ExtCe1sus` WRITE;
/*!40000 ALTER TABLE `ExtCe1sus` DISABLE KEYS */;
/*!40000 ALTER TABLE `ExtCe1sus` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Groups` (
  `group_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `description` mediumtext CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `canDownlad` int(1) NOT NULL DEFAULT '0',
  `tlplvl` int(1) NOT NULL,
  `email` varchar(255) CHARACTER SET utf32 COLLATE utf32_unicode_ci NOT NULL,
  `usermails` int(1) NOT NULL DEFAULT '0',
  `pgpKey` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `ce1sus_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`group_id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  KEY `IDK_Groups_tlplvl` (`tlplvl`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Groups` WRITE;
/*!40000 ALTER TABLE `Groups` DISABLE KEYS */;
INSERT INTO `Groups` VALUES (1,'Default_Group','Default Group, for all users',0,3,'a@a.com',0,NULL,NULL);
/*!40000 ALTER TABLE `Groups` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Groups_has_Events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Groups_has_Events` (
  `group_id` int(11) NOT NULL,
  `event_id` bigint(20) NOT NULL,
  PRIMARY KEY (`group_id`,`event_id`),
  KEY `IDX_GhE_group_id` (`event_id`),
  KEY `IDX_GhE_event_id` (`group_id`),
  CONSTRAINT `FK_Events_Groups_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Groups_Events_Group_id` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Groups_has_Events` WRITE;
/*!40000 ALTER TABLE `Groups_has_Events` DISABLE KEYS */;
/*!40000 ALTER TABLE `Groups_has_Events` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Mails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Mails` (
  `mail_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `body` text NOT NULL,
  `function_id` int(11) NOT NULL,
  `subject` varchar(255) NOT NULL,
  PRIMARY KEY (`mail_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Mails` WRITE;
/*!40000 ALTER TABLE `Mails` DISABLE KEYS */;
/*!40000 ALTER TABLE `Mails` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `NumberValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `NumberValues` (
  `NumberValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` decimal(10,0) DEFAULT NULL,
  `attribute_id` bigint(20) NOT NULL,
  `event_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`NumberValue_id`),
  KEY `IDX_numberValue_attribute_id` (`attribute_id`),
  KEY `IDX_NumberValue_value` (`value`),
  KEY `idx_NumberValues_event_event_id` (`event_id`),
  CONSTRAINT `fk_NumberValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_NumberValues_event_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `NumberValues` WRITE;
/*!40000 ALTER TABLE `NumberValues` DISABLE KEYS */;
/*!40000 ALTER TABLE `NumberValues` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Obj_links_Obj`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Obj_links_Obj` (
  `object_id_to` bigint(20) NOT NULL,
  `object_id_from` bigint(20) NOT NULL,
  PRIMARY KEY (`object_id_to`,`object_id_from`),
  KEY `IDX_OlO_from` (`object_id_from`),
  KEY `IDX_OlO_to` (`object_id_to`),
  CONSTRAINT `FK_Olo_Obj_object_id_from` FOREIGN KEY (`object_id_from`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Olo_Obj_object_id_to` FOREIGN KEY (`object_id_to`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Obj_links_Obj` WRITE;
/*!40000 ALTER TABLE `Obj_links_Obj` DISABLE KEYS */;
/*!40000 ALTER TABLE `Obj_links_Obj` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Objects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Objects` (
  `object_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `creator_id` bigint(20) NOT NULL,
  `def_object_id` bigint(20) NOT NULL,
  `event_id` bigint(20) DEFAULT NULL,
  `created` datetime NOT NULL,
  `parentObject` bigint(20) DEFAULT NULL,
  `parentEvent` bigint(20) DEFAULT NULL,
  `code` int(1) NOT NULL DEFAULT '0',
  `modifier_id` bigint(20) DEFAULT NULL,
  `uuid` varchar(45) NOT NULL,
  PRIMARY KEY (`object_id`),
  KEY `IDX_DObj_objects_def_object_id` (`def_object_id`),
  KEY `IDX_objects_events_event_id` (`event_id`),
  KEY `IDX_objects_events_event_id_parentEvent` (`parentEvent`),
  KEY `IDX_Obj_creator_id` (`creator_id`),
  KEY `IDX_Obj_modifier_id` (`modifier_id`),
  KEY `IDX_obj_id_shareable` (`object_id`),
  KEY `FK_Obj_Obj_parent_id_object_id` (`parentObject`),
  CONSTRAINT `FK_DObj_objects_def_object_id` FOREIGN KEY (`def_object_id`) REFERENCES `DEF_Objects` (`def_object_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_objects_events_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_objects_events_event_id_parentEvent` FOREIGN KEY (`parentEvent`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Obj_Obj_parent_id_object_id` FOREIGN KEY (`parentObject`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Obj_user_creator_id_user_id` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Obj_user_modifier_id_user_id` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Objects` WRITE;
/*!40000 ALTER TABLE `Objects` DISABLE KEYS */;
/*!40000 ALTER TABLE `Objects` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `PushErrors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PushErrors` (
  `error_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `error_message` varchar(255) NOT NULL,
  `subgroup_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  `data` longtext NOT NULL,
  `created` datetime NOT NULL,
  `resolution_id` int(11) NOT NULL DEFAULT '0',
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`error_id`),
  KEY `FK_PError_Group_group_id_idx` (`user_id`),
  KEY `FK_PError_User_user_id_idx` (`subgroup_id`),
  KEY `fk_PushErrors_1_idx` (`group_id`),
  CONSTRAINT `FK_PError_Group_group_id` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_PError_SubGroup_subgroup_id` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_PError_User_user_id` FOREIGN KEY (`subgroup_id`) REFERENCES `SubGroups_has_Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `PushErrors` WRITE;
/*!40000 ALTER TABLE `PushErrors` DISABLE KEYS */;
/*!40000 ALTER TABLE `PushErrors` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `StringValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `StringValues` (
  `StringValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `attribute_id` bigint(20) NOT NULL,
  `event_id` bigint(20) NOT NULL,
  PRIMARY KEY (`StringValue_id`),
  KEY `IDX_StrValues_attr_id` (`attribute_id`),
  KEY `IDX_StringValues_event_event_id` (`event_id`),
  CONSTRAINT `fk_StringValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_StringValues_event_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `StringValues` WRITE;
/*!40000 ALTER TABLE `StringValues` DISABLE KEYS */;
/*!40000 ALTER TABLE `StringValues` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `SubGroups_has_Events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SubGroups_has_Events` (
  `subgroup_id` int(11) NOT NULL,
  `event_id` bigint(20) NOT NULL,
  PRIMARY KEY (`subgroup_id`,`event_id`),
  KEY `IDX_EhS_subgroup_id` (`subgroup_id`),
  KEY `IDX_EhS_event_id` (`event_id`),
  CONSTRAINT `FK_Events_SubGroups_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_SUBGroups_Events_subgroup_id` FOREIGN KEY (`subgroup_id`) REFERENCES `Subgroups` (`subgroup_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `SubGroups_has_Events` WRITE;
/*!40000 ALTER TABLE `SubGroups_has_Events` DISABLE KEYS */;
/*!40000 ALTER TABLE `SubGroups_has_Events` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Subgroups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Subgroups` (
  `subgroup_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`subgroup_id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Subgroups` WRITE;
/*!40000 ALTER TABLE `Subgroups` DISABLE KEYS */;
INSERT INTO `Subgroups` VALUES (1,'Default_Subgroup','Default_Subgroup');
/*!40000 ALTER TABLE `Subgroups` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Subgroups_has_Groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Subgroups_has_Groups` (
  `subgroup_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`subgroup_id`,`group_id`),
  KEY `IDX_subgroups_groups_group_id` (`group_id`),
  KEY `IDX_subgroups_groups_subgroup_id` (`subgroup_id`),
  CONSTRAINT `fk_subgroups_groups_group_id` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_subgroups_groups_subgroup_id` FOREIGN KEY (`subgroup_id`) REFERENCES `Subgroups` (`subgroup_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Subgroups_has_Groups` WRITE;
/*!40000 ALTER TABLE `Subgroups_has_Groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `Subgroups_has_Groups` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `TextValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TextValues` (
  `TextValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `attribute_id` bigint(20) NOT NULL,
  `event_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`TextValue_id`),
  KEY `IDX_TextValues_attribute_id` (`attribute_id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `FK_TextValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `TextValues` WRITE;
/*!40000 ALTER TABLE `TextValues` DISABLE KEYS */;
/*!40000 ALTER TABLE `TextValues` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Users` (
  `user_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(45) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `privileged` int(1) DEFAULT '0',
  `last_login` datetime DEFAULT NULL,
  `email` varchar(45) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `disabled` int(1) NOT NULL DEFAULT '1',
  `apikey` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  `pgpKey` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `activated` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `apikey_UNIQUE` (`apikey`),
  KEY `fk_users_groups_mainGroup` (`group_id`),
  CONSTRAINT `FK_User_Group_Group_id` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`group_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES (1,'admin','dd94709528bb1c83d08f3088d4043f4742891f4f',1,'2014-02-13 08:58:39','admin@admin.com',0,NULL,11,NULL,0);
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `ce1sus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ce1sus` (
  `ce1sus_id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(45) NOT NULL,
  `value` text NOT NULL,
  PRIMARY KEY (`ce1sus_id`),
  UNIQUE KEY `key_UNIQUE` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `ce1sus` WRITE;
/*!40000 ALTER TABLE `ce1sus` DISABLE KEYS */;
INSERT INTO `ce1sus` VALUES (1,'app_rev','0.7.0'),
(2,'db_shema','0.8.0'),
(3,'handler_config','{\"files\": \"/home/jhemp/workspace/myCels1us/files\", \"rt_url\": \"https://rt.govcert.etat.lu/rt/\", \"cveurl\": \"http://cve.mitre.org/cgi-bin/cvename.cgi?name=\", \"rt_password\": \"D6imjht9t3VRtU3\", \"rt_user\": \"botuser\"}');
/*!40000 ALTER TABLE `ce1sus` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

