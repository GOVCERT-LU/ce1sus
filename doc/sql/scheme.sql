
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='The ref_object_id is just to keep the relations unique to pr';
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
  PRIMARY KEY (`attribute_id`),
  KEY `IDX_attr_def_attribute_id` (`def_attribute_id`),
  KEY `IDX_attr_object_id` (`object_id`),
  KEY `IDX_Attr_Objects_object_id` (`object_id`),
  KEY `IDX_Attr_creator_id` (`creator_id`),
  KEY `IDX_Attr_modifier_id` (`modifier_id`),
  KEY `IDX_Attr_id_sharable` (`attribute_id`),
  KEY `FK_Attr_Object_Object_id` (`object_id`),
  CONSTRAINT `FK_Attr_DAttr_attribute_id` FOREIGN KEY (`def_attribute_id`) REFERENCES `DEF_Attributes` (`def_attribute_id`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `FK_Attr_Object_Object_id` FOREIGN KEY (`object_id`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Attr_Users_creator_id_user_id` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Attr_Users_modifier_id_user_id` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
  `comment` mediumtext COLLATE utf8_unicode_ci,
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
  `name` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `description` mediumtext COLLATE utf8_unicode_ci NOT NULL,
  `regex` varchar(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '^.*$',
  `classIndex` int(11) NOT NULL DEFAULT '0',
  `handlerIndex` int(11) NOT NULL DEFAULT '0',
  `deletable` int(1) NOT NULL DEFAULT '1',
  `sharable` int(1) NOT NULL DEFAULT '0',
  `relationable` int(1) NOT NULL DEFAULT '0',
  `chksum` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`def_attribute_id`),
  UNIQUE KEY `chksum_UNIQUE` (`chksum`),
  KEY `IDX_def_attributes_name` (`name`),
  KEY `IDX_def_attributes_chksum` (`chksum`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `DEF_Attributes` WRITE;
/*!40000 ALTER TABLE `DEF_Attributes` DISABLE KEYS */;
INSERT INTO `DEF_Attributes` VALUES (1,'hash_md5','md5 hash of a file','^[0-9a-fA-F]{32}$',1,0,0,1,1,'710cda5f85a850ff78ee81a1aaab03de3ccb76b5'),
(2,'hash_sha1','sha1 hash of a file','^[0-9a-fA-F]{40}$',1,0,0,1,1,'a5d768f77a0dca70177599571f4a3445cd887b42'),
(3,'hash_sha256','sha256 hash of a file','^[0-9a-fA-F]{64}$',1,0,0,1,1,'bf8ac6258c334061ba51b2c9898f0f5debef9a38'),
(4,'hash_sha384','sha384 hash of a file','^[0-9a-fA-F]{96}$',1,0,0,1,1,'93eda17e4533ceac8c64ebbb2f51917ac4722694'),
(5,'hash_sha512','sha512 hash of a file','^[0-9a-fA-F]{128}$',1,0,0,1,1,'ae04a03de397188df7a65bdb5457244b71674310'),
(6,'hash_ssdeep','ssdeep hash of a file','^\\d+:[a-zA-Z0-9+]+:[a-zA-Z0-9+]+$',1,0,1,1,0,'f08ceb4026de2cf444043c37eb4bfc30f8a6af95'),
(7,'file_name','The file_name field specifies the name of the file.','^.+$',1,0,0,1,0,'15134f8e4624e2bb95081b8a722e0ac5cfc65360'),
(8,'size_in_bytes','The size_in_bytes field specifies the size of the file, in bytes.','^\\d+$',3,0,0,1,0,'c4c41b957024f6cc39031e0c308c9f4374686914'),
(9,'magic_number','The magic_number specifies the particular magic number (typically a hexadecimal constant used to identify a file format) corresponding to the file, if applicable.','^.+$',1,0,0,1,0,'aead9058ae162ae69b8dd577954cba1708bb950c'),
(10,'reference_internal_identifier','Holds a reference to an internal ID number.','^\\d+$',3,2,1,1,0,'98d581d2db295797fb9f1d62a5f6a1c1e2ead5ca'),
(11,'vulnerability_cve','CVE reference to a known vulnerability','^CVE-\\d{4}-\\d{4,}$',1,3,1,1,1,'5e657c7ec029bd474780a8df501b21f2ebe6d19c'),
(12,'raw_file','The raw file data','^.+$',1,1,1,0,0,'af63475e83cecea5ffc19a452af00d7501e2c711'),
(13,'raw_document_file','The raw document (non malicious file)','^.+$',1,6,1,0,0,'6a87aaf90f09cd74b2737fe2bb2249a5709b3a70'),
(14,'hostname','Fully qualified domain name','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,1,'e7c2e1eb3ee6e75b2012a16b57f6a74494e0a443'),
(15,'description','Contains free text description for an object','^.+$',0,9,1,1,0,'c6dc0d16ffed78c3b7a120e0d8d02877e9acf570'),
(16,'comment','Holds free text for comments about objects and event.','^.+$',0,9,1,0,0,'430b6a193d99d8a5057cf5ad004a61be8e6feadd'),
(17,'is_malicious','Boolean to identify malicious objects','^yes$|^no$',1,8,1,1,0,'ece1d0c31862c111c2bac1d8b1d711a67c8c0249'),
(18,'malware_file_type','dropper, trojan, banking trojan, RAT, rogue document, phishing document,....','^virus$|^trojan$|^dropper$|^malware$|^rootkit$|^key_logger$|^worm$',1,8,1,1,0,'b0390069069c0e7d5ad5b8e7132aeddbc2c8d9b8'),
(19,'file_full_path','The File path including the file name.','^.+$',1,0,1,1,0,'5b8891608448182881c02417189849e6e6adefdc'),
(20,'file_extension','The File_Extension field specifies the file extension of the file.','^.+$',1,0,1,1,0,'1dcaf962129d243bffe97e85c48a0259a4e847f3'),
(21,'file_format','The File_Format field specifies the particular file format of the file, most typically specified by a tool such as the UNIX file command.','^.+$',1,0,1,1,0,'2b6e1b4bbe233fcebf2f4ced9509110083afeab0'),
(22,'digital_signature','The Digital_Signatures field is optional and captures one or more digital signatures for the file.','^.+$',0,9,1,1,1,'684b4c98911838d9e116f4e1ad948e28c3dcc3b9'),
(23,'file_modified_time','The Modified_Time field specifies the date/time the file was last modified.','^.+$',2,7,1,1,0,'9421c43b78f6047a20c2da256acb09466885771a'),
(24,'file_accessed_datetime','The Accessed_Time field specifies the date/time the file was last accessed.','^.+$',2,7,1,1,0,'1719b29262feb1a2851dc3eff3ba2634d944e698'),
(25,'file_created_datetime','The Created_Time field specifies the date/time the file was created.','^.+$',2,7,1,1,0,'2603127f5d19e51c1df1bd3b2aae63d3d473d800'),
(26,'packer','The Packer_List field specifies any packers that the file may be packed with. The term \'packer\' here refers to packers, as well as things like archivers and installers.','^.+$',1,0,1,1,0,'ef494d61a1375dc75527af844802292ae39c6261'),
(27,'peak_entropy','The Peak_Entropy field specifies the calculated peak entropy of the file.','^[\\d]{1,}$',3,0,1,1,0,'546daa267c02838a4d0891d971e3db9bb9863b8b'),
(28,'encryption_mechanism','The encryption_mechanism field is optional and specifies the protection/encryption algorithm utilized to protect the Raw_Artifact content.','^.+$',0,9,1,1,0,'73a268a6ed42833f9ad28c42de3b898cd757cb6b'),
(29,'discovery_method','The Discovery_Method field is intended to characterize the method and/or tool used to discover the object.','^.+$',0,9,1,1,0,'e20aef80c742f7e842d3b210a91fa7edc1d9006e'),
(30,'vulnerability_free_text','Free text description for a vulnerability','^.+$',0,9,1,1,0,'b0e618b9a5e55027844e136ad5ff6082bcbf08e1'),
(31,'reference_url','URL pointing to online information','^.+$',1,0,1,1,0,'eb84e41a67b33479e52c9f79c8572079d2940eae'),
(32,'reference_free_text','Free text used to give reference information.','^.+$',0,9,1,1,0,'4582851ae280227277852673a91285b950864991'),
(33,'analysis_free_text','A free text analysis for the object.','^.+$',0,0,1,1,0,'266760cc3b37f5086c9b4e9455b4eb5c207dc01c'),
(34,'information_source','Free text holding information about the source of an information (e.g where did a document come from).','^.+$',0,9,1,1,0,'644e0e0cad61eb55f749878f0a2fa901d2db5f59'),
(35,'reference_internal_case','Holds a reference to an internal case to which the event is related.','^.+$',1,0,1,1,0,'0f1c92e7ade6f1ab4b6219877109aac440e9c313'),
(36,'reference_external_identifier','Contains an external identifier for the event','^.+$',1,0,1,1,1,'1d58a5982c43fe50bf480eb669af5de85cd8e348'),
(37,'creation_datetime','The creation time stamp of an object','^.+$',2,7,1,0,0,'d54cae514479783420d78ac5c2d87662fe50b0df'),
(38,'raw_pcap_file','The raw file data','^.+$',1,6,1,0,0,'dd28670ef179af6106be1e80294710c7fd882ba0'),
(39,'email_attachment_file_name','The Attachments field specifies any files that were attached to the email message. It imports and uses the CybOX FileObjectType from the File_Object to do so.','^.+$',1,0,1,1,0,'52bf9cc8a1663e6a6bc07454ecc49033ce5bf939'),
(40,'email_bcc','The BCC field specifies the email addresses of any recipients that were included in the blind carbon copy header of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,'94e55ceac0cc1949d72a8c73c019e3ca46b80332'),
(41,'email_cc','The CC field specifies the email addresses of any recipients that were included in the carbon copy header of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,'a2ee7be2e14824a4964d8e20927680d377f1e431'),
(42,'email_content_type','The Content-Type field specifies the internet media, or MIME, type of the email message content.','^.+$',1,0,1,1,0,'5fd561616d38112cd19a766e098a5c380a25c6f7'),
(43,'email_errors_to','The Errors_To field specifies the entry in the (deprecated) errors_to header of the email message.','^.+$',1,0,1,1,0,'519e8026052656395b599f4af24250898b123987'),
(44,'email_from','The From field specifies the email address of the sender of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,1,'cea13bd7128110529cec97dee27c940f78fa5b88'),
(45,'email_in_reply_to','The In_Reply_To field specifies the message ID of the message that this email is a reply to.','^.+$',1,0,1,1,0,'0b9c04e77556bb4f91c56befecb9b04e48c917ee'),
(46,'email_message_id','The Message_ID field specifies the automatically generated ID of the email message.','^.+$',1,0,1,1,0,'7b5e8f7fa7233ed9db160bc8f40f184cd55286b1'),
(47,'email_mime_version','The MIME-Version field specifies the version of the MIME formatting used in the email message.','^.+$',1,0,1,1,0,'aa6b853aea94f0a74f786af9b69736187858ea88'),
(48,'email_raw_body','The Raw_Body field specifies the complete (raw) body of the email message.','^.+$',1,6,1,0,0,'19a4a04d13db5a993458f40032232b72fbeeb0b9'),
(49,'email_raw_header','The Raw_Header field specifies the complete (raw) headers of the email message.','^.+$',0,9,1,1,0,'910330bfbd0f1748e326a8bcc2c39cba048251ea'),
(50,'email_receive_datetime','The Date field specifies the date/time that the email message was received by the mail server.','^.+$',2,7,1,1,0,'185baf13aac8b23c08e0fd11abd46c5635f0b8ca'),
(51,'email_relay_ip','This attribute hold the IP address of an MTA used to deliver the mail.','^.+$',1,0,1,1,1,'d8241bcaf63e12098e34381bd993ec85ef1373a0'),
(52,'email_reply_to','The Reply_To field specifies the email address that should be used when replying to the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,0,1,1,0,'6acf31ab48931ff6a93730b1e3bcb72ae3444085'),
(53,'email_send_datetime','The Date field specifies the date/time that the email message was sent.','^.+$',2,7,1,1,0,'24c2d02ff19de0a60a15145b71cea1efb9d39859'),
(54,'email_sender','The Sender field specifies the email address of the sender who is acting on behalf of the author listed in the From: field','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,0,1,1,0,'b2156d500840c3cf94cbd05cc5addd451a256fb1'),
(55,'email_server','The Email_Server field is optional and specifies the relevant email server.','^.+$',1,0,1,1,0,'3dc7363568f6e5ccc9490ecb1698e1fa15b278d4'),
(56,'email_subject','The Subject field specifies the subject (a brief summary of the message topic) of the email message.','^.+$',1,0,1,1,0,'bdaa346755b82b6535b1a9119681f449e9980d8e'),
(57,'email_to','The To field specifies the email addresses of the recipients of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,'1d0d62acb2b715970a72645649c56cd464374d13'),
(58,'email_x_mailer','The X-Mailer field specifies the software used to send the email message. This field is non-standard.','^.+$',1,0,1,1,0,'ba389ab569843d1d63e2733492967d7810b006b5'),
(59,'email_x_originating_ip','The X-Originating-IP field specifies the originating IP Address of the email sender, in terms of their connection to the mail server used to send the email message. This field is non-standard.','^.+$',1,0,1,1,0,'a8b21de160874f5eacf84275898ec4d87f2dea19'),
(60,'code_language','The code_language field refers to the code language used in the code characterized in this field.','^.+$',1,0,1,1,0,'30ee4bba4ab0edf1bab12b6270df92b5aa8fdaa9'),
(61,'processor_family','The processor_family field specifies the class of processor that the code snippet is targeting. Possible values: x86-32, x86-64, IA-64, PowerPC, ARM, Alpha, SPARC, z/Architecture, eSi-RISC, MIPS, Motorola 68k, Other.','^.+$',1,0,1,1,0,'c55801b8570ed68ff5298ed0e7f1e5062f0ec426'),
(62,'targeted_platform','The Targeted_Platforms field specifies a list platforms that this code is targeted for.','^.+$',1,0,1,1,0,'dbef2bc67f90d1ca8ce9dc5012105568c3b2b643'),
(63,'antivirus_record','The results of one or many antivirus scans for an object. This is a multiline csv value (datetime, engine, result, threat name).','^.+$',1,5,1,1,0,'dfea5097b9d29f3b1f6537250e60676ff121e2b8'),
(64,'ida_pro_file','An IDA pro file.','^.+$',1,6,1,1,0,'0d9ae7b3b61d29cd2c60f1f0ecc8ae061afce579'),
(65,'log_records','Free text for storing log information.','^.+$',0,9,1,1,0,'3fa76562b8e0a967bc40b4768e8f921d202aee73'),
(66,'whois','Whois network information','^.+$',0,9,1,1,0,'36c87187a4b57ced3aed6aa173d7d18e6052bf37'),
(67,'asn','The asn value specifies an identifier for an autonomous system number.','^.+$',1,0,1,1,1,'a6a4149cd52832b516c6f0b279e6c40b11caeb55'),
(68,'domain','Contains a fully qualified domain name','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,'b724ebab01bfc1787c0178ca75585ede241af2f3'),
(69,'file_content_pattern','Contains a pattern that can be found in the raw file data','^.+$',1,0,1,1,0,'db5237d68da8b94976eb225f9ec6d3c49074c885'),
(70,'file_full_path_pattern','A pattern that matches the full path of a file','^.+$',1,0,1,1,0,'d41da12a88034970b577efb0a5487cae0c4ade60'),
(71,'file_name_pattern','A pattern that matches the file name','^.+$',1,0,1,1,0,'6df1b1a589081be58bdf3bc7a636c840bc2ae23a'),
(72,'hostname_c&c','Fully qualified domain name of a host hosting a command and control server','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,1,'6f5904cb25891a47046f4bdb308bb087a6efe82a'),
(73,'ids_rules','Holds IDS rules. These rules need to be prefixed with the used format (e.g. snort).','^.+$',0,9,1,1,0,'809f700d75e908e52dc71d4384d37224b485842a'),
(74,'ipv4_addr','The IPv4-addr value specifies an IPV4 address.','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$',1,5,1,1,0,'b4ef36d45a2c7f709cc23c705a3ec24014323c11'),
(75,'ipv4_addr_c&c','IPv4 address hosting a command and control server','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$',1,5,1,1,1,'2e97cdcc10f5d377a788e09fbf417e9ae0f2670a'),
(76,'ipv4_net','IPv4 CIDR block','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}/\\d{1,2}$',1,5,1,1,0,'8a7a31f46f394c4f1de4d7ae7b982edd1ce8def2'),
(77,'ipv6_addr','The IPv6-addr value specifies an IPv6 address.','^.+$',1,5,1,1,0,'d33db9a5ebbae9db02153ae9307cddb290333303'),
(78,'ipv6_addr_c&c','IPv6 address hosting a command and control server','^.+$',1,5,1,1,1,'0eede3e798cbc59e2059bd53040b4a4afcbbf791'),
(79,'ipv6_net','IPv6 sub-network','^.+$',1,5,1,1,0,'2da7fc45043cc7beb8ea72445d9b216b2c02807d'),
(80,'mutex','The Mutex object is intended to characterize generic mutual exclusion (mutex) objects.','^.+$',1,0,1,1,0,'ff9768d8e6c680578e2e3c918c97f451fe96b839'),
(81,'open_ioc_definition','Hold open IOC definitions.','^.+$',1,6,1,1,0,'83c9a2c44fdfb0b7afc06ba47df8ad74c73dc8e9'),
(82,'trafic_content_pattern','Pattern matching network traffic content.','^.+$',1,0,1,1,0,'44ca21ee6cf2487110c81b8cd2e2f31182a0e9cf'),
(83,'url','Holds a complete URL (e.g. http://www.govcert.lu/en/index.hmtl)','^.+$',1,5,1,1,0,'c337a1cd392abf95c06697f29210a16cfae616bb'),
(84,'url_path','Holds only the path part of an URL. (e.g. /en/index.html)','^.+$',1,5,1,1,0,'7cd6806a3c6896a5d5b21b2c105396e5169ee975'),
(85,'url_pattern','Holds a pattern that matches URL.','^.+$',1,5,1,1,0,'82b13d30fe8643789b92e6c6e49a7958e4a2e871'),
(86,'win_registry_key','The WindowsRegistryObjectType type is intended to characterize Windows registry objects, including Keys and Key/Value pairs.','^.+$',0,9,1,1,1,'8199c3fbbdd1cfe481253c95b931fbf1fce86716'),
(87,'yara_rule','Holds YARA rules used to identify and classify malware samples.','^.+$',0,9,1,1,1,NULL),
(88,'mime_type','File mime-type','^.+$',0,0,0,1,0,'ba70870d91e289a4d8be5aaf1ba5900c50ae6cfe'),
(89,'compromized_hostname','compromized_hostname','^.+$',1,0,1,1,1,'0ad54543ef9ebdb20014aec3b1e18b48fbbf4e7b'),
(90,'ipv4_addr_phishingSite','ipv4_addr_phishingSite','^.+$',1,0,1,1,1,'bb8e1e82eb12c1a303e3d2f64b7c0f9f824a48cc'),
(91,'ip_port','IP Port','^[\\d]{1,}$',3,0,1,1,0,'10c8e9e03ac8d1983f925ef47712853de5045c60'),
(101,'ip_protocol','IP Protocol','^tcp$|^udp$|^icmp$',1,8,1,1,0,'b67398701c224b4f57ea23d58efa6f702378cef6'),
(111,'file_id','File description as returned by unix \'file\' command','^.+$',1,0,1,1,0,'dcc780e76fd89826e494738f2649382a7c2dc999'),
(112,'email_address','The associated email address','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,'4fc989b3947c7bc4efd52948617520410b303f08'),
(113,'encryption_key','Clear text stings used along with an encryption algorithm in order to cypher data','^.+$',0,9,1,1,1,'8b503a0548c57c28cc9177f00454899d57c83b09'),
(114,'full_name','The Full_Name field specifies the full name of the user','^.+$',1,0,1,0,0,'923c6021b434d7ca52a02d1dfdb75c7b393ee696'),
(115,'password','Passwords are clear text stings used to authenticated a user','^.+$',1,0,1,1,1,'bc20213461f41568aeb20cf3903cf67f15014e7c'),
(116,'username','The Username field specifies the particular username of the user account','^[a-zA-Z0-9._-]+$',1,0,1,1,0,'52b67ba5c365cf6fe9c222228ee17533f92cf75b'),
(117,'xor_pattern','The xor_pattern field contains a hexadecimal-character hex string','^(?:0x)?[a-fA-F0-9-:]+$',1,5,1,1,1,NULL),
(118,'http_user_agent','HTTP defines methods (sometimes referred to as verbs) to indicate the desired action to be performed on the identified resource. What this resource represents, whether pre-existing data or data that is generated dynamically, depends on the implementation of the server. Often, the resource corresponds to a file or the output of an executable residing on the server.','^.+$',1,0,1,1,0,'7b33c55cd57b13ff1e4aef1db2ba148858d4f4b7'),
(119,'http_method','The Hypertext Transfer Protocol (HTTP) identifies the client software originating the request, using a \"User-Agent\" header, even when the client is not operated by a user.','^GET$|^HEAD$|^POST$|^PUT$|^DELETE$|^TRACE$|^OPTIONS$|^CONNECT$|^PATCH$',1,8,1,1,0,'403aa7f69a9d886c59f3d04bcbb22fcdd7d4e9e4'),
(120,'http_version','HTTP uses a \"<major>.<minor>\" numbering scheme to indicate versions of the protocol.','^\\d+\\.\\d+$',1,0,1,1,0,'50d7bdcdbe959bdbae14818c884e84025f9d3ce6');
/*!40000 ALTER TABLE `DEF_Attributes` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `DEF_Objects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DEF_Objects` (
  `def_object_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `description` mediumtext COLLATE utf8_unicode_ci,
  `chksum` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `sharable` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`def_object_id`),
  UNIQUE KEY `chksum_UNIQUE` (`chksum`),
  KEY `IDX_def_objects_chksum` (`chksum`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
(11,'user_account','User profile','4ab2df0a57a74fdf904e0e27086676ed9c4c3cdf',1);
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
(10,5),
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
(5,11),
(6,11),
(9,11),
(10,11),
(1,12),
(6,12),
(10,12),
(2,13),
(8,14),
(9,14),
(1,15),
(2,15),
(3,15),
(4,15),
(5,15),
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
(5,16),
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
(11,31),
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
(11,32),
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
(6,70),
(8,70),
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
(8,87),
(1,88),
(6,88),
(8,91),
(8,101),
(1,111),
(6,111),
(11,112),
(8,113),
(11,114),
(8,115),
(11,115),
(11,116),
(8,117),
(8,118),
(8,119),
(8,120);
/*!40000 ALTER TABLE `DObj_has_DAttr` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `DateValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DateValues` (
  `DateValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` datetime DEFAULT NULL,
  `attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`DateValue_id`),
  KEY `IDX_DateValues_attribute_id` (`attribute_id`),
  KEY `IDX_DateValues_Value` (`value`),
  CONSTRAINT `FK_DateValues_Attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `DateValues` WRITE;
/*!40000 ALTER TABLE `DateValues` DISABLE KEYS */;
/*!40000 ALTER TABLE `DateValues` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Events` (
  `event_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `description` text COLLATE utf8_unicode_ci,
  `title` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
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
  `uuid` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `creatorGroup` int(11) NOT NULL DEFAULT '1',
  `code` int(1) NOT NULL,
  PRIMARY KEY (`event_id`),
  UNIQUE KEY `uuid_UNIQUE` (`uuid`),
  KEY `IDX_Events_uuid` (`uuid`),
  KEY `IDK_Events_creator_id` (`creator_id`),
  KEY `IDX_Events_modifier_ID` (`modifier_id`),
  KEY `IDX_Events_creatorGroup` (`creatorGroup`),
  KEY `fk_Events_1` (`creatorGroup`),
  KEY `FK_Events_Groups_creatorGroup_groupID` (`creatorGroup`),
  CONSTRAINT `FK_Events_Groups_creatorGroup_groupID` FOREIGN KEY (`creatorGroup`) REFERENCES `Groups` (`group_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Events_User_creator_user_ID` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Events_User_modifier_user_ID` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Events` WRITE;
/*!40000 ALTER TABLE `Events` DISABLE KEYS */;
/*!40000 ALTER TABLE `Events` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `Groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Groups` (
  `group_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `description` mediumtext COLLATE utf8_unicode_ci,
  `canDownlad` int(1) NOT NULL DEFAULT '0',
  `tlplvl` int(1) DEFAULT NULL,
  `email` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `usermails` int(1) NOT NULL DEFAULT '0',
  `pgpKey` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`group_id`),
  KEY `IDK_Groups_tlplvl` (`tlplvl`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Groups` WRITE;
/*!40000 ALTER TABLE `Groups` DISABLE KEYS */;
INSERT INTO `Groups` VALUES (1,'Default_Group','Default Group, for all users',1,3,'a@a.com',0,NULL),
(3,'test','sdfasdfsafd',1,3,'a@a.com',0,NULL);
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Groups_has_Events` WRITE;
/*!40000 ALTER TABLE `Groups_has_Events` DISABLE KEYS */;
/*!40000 ALTER TABLE `Groups_has_Events` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `NumberValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `NumberValues` (
  `NumberValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` decimal(10,0) DEFAULT NULL,
  `attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`NumberValue_id`),
  KEY `IDX_numberValue_attribute_id` (`attribute_id`),
  KEY `IDX_NumberValue_value` (`value`),
  CONSTRAINT `fk_NumberValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `NumberValues` WRITE;
/*!40000 ALTER TABLE `NumberValues` DISABLE KEYS */;
/*!40000 ALTER TABLE `NumberValues` ENABLE KEYS */;
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
  `uuid` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
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
  CONSTRAINT `FK_objects_events_event_id_parentEvent` FOREIGN KEY (`parentEvent`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_Obj_Obj_parent_id_object_id` FOREIGN KEY (`parentObject`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Obj_user_creator_id_user_id` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Obj_user_modifier_id_user_id` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Objects` WRITE;
/*!40000 ALTER TABLE `Objects` DISABLE KEYS */;
/*!40000 ALTER TABLE `Objects` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `StringValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `StringValues` (
  `StringValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`StringValue_id`),
  KEY `IDX_StrValues_attr_id` (`attribute_id`),
  KEY `IDX_StrValue_Value` (`value`),
  CONSTRAINT `fk_StringValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
  `name` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`subgroup_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Subgroups` WRITE;
/*!40000 ALTER TABLE `Subgroups` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Subgroups_has_Groups` WRITE;
/*!40000 ALTER TABLE `Subgroups_has_Groups` DISABLE KEYS */;
INSERT INTO `Subgroups_has_Groups` VALUES (1,1),
(2,1);
/*!40000 ALTER TABLE `Subgroups_has_Groups` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `TextValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TextValues` (
  `TextValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` longtext COLLATE utf8_unicode_ci,
  `attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`TextValue_id`),
  KEY `IDX_TextValues_attribute_id` (`attribute_id`),
  CONSTRAINT `FK_TextValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
  `username` varchar(45) COLLATE utf8_unicode_ci NOT NULL COMMENT '\n',
  `password` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `privileged` int(1) DEFAULT '0',
  `last_login` datetime DEFAULT NULL,
  `email` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `disabled` int(1) NOT NULL DEFAULT '1',
  `apikey` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `group_id` int(11) DEFAULT '1',
  `pgpKey` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `apikey_UNIQUE` (`apikey`),
  KEY `IDX_User_Group_Group_id` (`group_id`),
  CONSTRAINT `FK_User_Group_Group_id` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`group_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES (1,'admin','dd94709528bb1c83d08f3088d4043f4742891f4f',1,'2013-12-17 12:42:50','admin@admin.com',0,NULL,1,NULL);
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `ce1sus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ce1sus` (
  `key` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `value` varchar(100) COLLATE utf8_unicode_ci DEFAULT 'None',
  PRIMARY KEY (`key`),
  UNIQUE KEY `key_UNIQUE` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `ce1sus` WRITE;
/*!40000 ALTER TABLE `ce1sus` DISABLE KEYS */;
INSERT INTO `ce1sus` VALUES ('app_rev','0.4.5'),
('db_shema','0.5.0'),
('definitions','5.9.7'),
('rest_api','0.2.0');
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

