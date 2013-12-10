
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='The ref_object_id is just to keep the relations unique to pr';
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  `comment` mediumtext,
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  `name` varchar(45) NOT NULL,
  `description` mediumtext NOT NULL,
  `regex` varchar(255) NOT NULL DEFAULT '^.*$',
  `classIndex` int(11) NOT NULL DEFAULT '0',
  `handlerIndex` int(11) NOT NULL DEFAULT '0',
  `deletable` int(1) NOT NULL DEFAULT '1',
  `sharable` int(1) NOT NULL DEFAULT '0',
  `relationable` int(1) NOT NULL DEFAULT '0',
  `chksum` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`def_attribute_id`),
  UNIQUE KEY `chksum_UNIQUE` (`chksum`),
  KEY `IDX_def_attributes_name` (`name`),
  KEY `IDX_def_attributes_chksum` (`chksum`)
) ENGINE=InnoDB AUTO_INCREMENT=112 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `DEF_Attributes` WRITE;
/*!40000 ALTER TABLE `DEF_Attributes` DISABLE KEYS */;
INSERT INTO `DEF_Attributes` VALUES (1,'hash_md5','md5 hash of a file','^[0-9a-fA-F]{32}$',1,0,0,1,1,'8b5b60262a070b4e86bdeee771df1c5f82af411d'),
(2,'hash_sha1','sha1 hash of a file','^[0-9a-fA-F]{40}$',1,0,0,1,1,'071eb20cd80ea3d874dfad489c822a2016daa00d'),
(3,'hash_sha256','sha256 hash of a file','^[0-9a-fA-F]{64}$',1,0,0,1,1,'2551d42b10cf0a1716671436b77698f90fed0c27'),
(4,'hash_sha384','sha384 hash of a file','^[0-9a-fA-F]{96}$',1,0,0,1,1,'7e44a3ebb32e48e812c3301277e96b695cc0ed89'),
(5,'hash_sha512','sha512 hash of a file','^[0-9a-fA-F]{128}$',1,0,0,1,1,'782f49137df2fc3589ff472664036e64621e2b66'),
(6,'hash_ssdeep','ssdeep hash of a file','^\\d+:[a-zA-Z0-9+]+:[a-zA-Z0-9+]+$',1,0,1,1,0,'a92dbb7f7bf68020e6fd74b0de2de661c716d128'),
(7,'file_name','The file_name field specifies the name of the file.','^.+$',1,0,0,1,0,'9802f41df84b79d361e9aafe62386299a77c76f8'),
(8,'size_in_bytes','The size_in_bytes field specifies the size of the file, in bytes.','^\\d+$',3,0,0,1,0,'32c393fd3ea0ea1f5439d5b7e1db310e283a1cc1'),
(9,'magic_number','The magic_number specifies the particular magic number (typically a hexadecimal constant used to identify a file format) corresponding to the file, if applicable.','^.+$',1,0,1,1,0,'12764f37a8f9997ebdd5c7f2f4905d4ed17ab1df'),
(10,'reference_internal_identifier','Holds a reference to an internal ID number.','^\\d+$',3,2,1,1,0,'c0695d0f2113b426fd5355f49c27979034de2ee3'),
(11,'vulnerability_cve','CVE reference to a known vulnerability','^CVE-(19|20)\\d{2}-[\\d]{4}$',1,3,1,1,1,'fd669897a7768fbfd703a2cd033fc48d54f17c83'),
(12,'raw_file','The raw file data','^.+$',1,1,1,0,0,'ddb88c41be6b708aaf6309bcfc4bb3762ec387e8'),
(13,'raw_document_file','The raw document (non malicious file)','^.+$',1,6,1,0,0,'dbfd4fd4cc323f1063ce1ab03586bc03e0944537'),
(14,'hostname','Fully qualified domain name','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,1,'2376b03d4148c212c63cc1904a04e17b1baa26ac'),
(15,'description','Contains free text description for an object','^.+$',0,9,1,1,0,'b248f7d94db2e4da5188d7d8ba242f23ba733012'),
(16,'comment','Holds free text for comments about objects and event.','^.+$',0,9,1,0,0,'cc9cd84564e9d314ad638af0ed55ba878d6f9bc8'),
(17,'is_malicious','Boolean to identify malicious objects','^yes$|^no$',1,8,1,1,0,'edab2b114e8e2d727c5e0e226aae1b8aa1ddd4f1'),
(18,'malware_file_type','dropper, trojan, banking trojan, RAT, rogue document, phishing document,....','^virus$|^trojan$|^dropper$|^malware$|^rootkit$|^key_logger$|^worm$',1,8,1,1,0,'d792cabf19e21de61666fef24e9767679bc9400c'),
(19,'file_full_path','The File path including the file name.','^.+$',1,0,1,1,0,'6354375248dfc43a70cab71553392c3918534075'),
(20,'file_extension','The File_Extension field specifies the file extension of the file.','^.+$',1,0,1,1,0,'735c8591b0e10f6dae47d4fe94c65c4d340b6a91'),
(21,'file_format','The File_Format field specifies the particular file format of the file, most typically specified by a tool such as the UNIX file command.','^.+$',1,0,1,1,0,'93f88eb103448bf84b332535a0f9ded721aaae0c'),
(22,'digital_signature','The Digital_Signatures field is optional and captures one or more digital signatures for the file.','^.+$',0,9,1,1,1,'ff6f1e3f3814b88261d6bb4f41710395d89fcd80'),
(23,'file_modified_time','The Modified_Time field specifies the date/time the file was last modified.','^.+$',2,7,1,1,0,'23dbb232d5c045fdaf45d1d0e2963758649ec9ff'),
(24,'file_accessed_datetime','The Accessed_Time field specifies the date/time the file was last accessed.','^.+$',2,7,1,1,0,'6cc63a956e62effc14868b23a9ae47cf80012c28'),
(25,'file_created_datetime','The Created_Time field specifies the date/time the file was created.','^.+$',2,7,1,1,0,'7e57114f701bea9d407e6d921ed06867ca69c6b5'),
(26,'packer','The Packer_List field specifies any packers that the file may be packed with. The term \'packer\' here refers to packers, as well as things like archivers and installers.','^.+$',1,0,1,1,0,'4ebdf814d95f7225af11511476beada1c7bd7628'),
(27,'peak_entropy','The Peak_Entropy field specifies the calculated peak entropy of the file.','^[\\d]{1,}$',3,0,1,1,0,'1d6a8927167fad3035de083b0c2c2e389b386e8f'),
(28,'encryption_mechanism','The encryption_mechanism field is optional and specifies the protection/encryption algorithm utilized to protect the Raw_Artifact content.','^.+$',0,9,1,1,0,'e6216dd1a1c17e6cbcc5043b503ab8e6b918f8fa'),
(29,'discovery_method','The Discovery_Method field is intended to characterize the method and/or tool used to discover the object.','^.+$',0,9,1,1,0,'e3d34e69981d1aa2a1d7a8de4f8797a90b100664'),
(30,'vulnerability_free_text','Free text description for a vulnerability','^.+$',0,9,1,1,0,'f044a402f0b814a2793bb7bb5c87543d346fd16c'),
(31,'reference_url','URL pointing to online information','^.+$',1,0,1,1,0,'1aadfbb852f3a7f0011860ac73827b74b092f3a3'),
(32,'reference_free_text','Free text used to give reference information.','^.+$',0,9,1,1,0,'0c4cc172541bd84db2f8f174ff584335e28d807b'),
(33,'analysis_free_text','A free text analysis for the object.','^.+$',0,0,1,1,0,'3e736b49ccf3e6fcd8b4461e75db71d2a989a620'),
(34,'information_source','Free text holding information about the source of an information (e.g where did a document come from).','^.+$',0,9,1,1,0,'35eb5619ec22bdd899d9b4a835fd335ad11d3c4f'),
(35,'reference_internal_case','Holds a reference to an internal case to which the event is related.','^.+$',1,0,1,1,0,'b15c8ba0fa7fd16f67fdd7e7e04c47487e935fc2'),
(36,'reference_external_identifier','Contains an external identifier for the event','^.+$',1,0,1,1,1,'6a83cfd07cb7832ef48a753e305944c3a03b6ebf'),
(37,'creation_datetime','The creation time stamp of an object','^.+$',2,7,1,0,0,'8769e7ee65c31e29324f6e3e4251a7265f210862'),
(38,'raw_pcap_file','The raw file data','^.+$',1,6,1,0,0,'4235363ecfe479f90e10e1a1140d714ea13d2e42'),
(39,'email_attachment_file_name','The Attachments field specifies any files that were attached to the email message. It imports and uses the CybOX FileObjectType from the File_Object to do so.','^.+$',1,0,1,1,0,'cee2d150d43cfa299b36daa62daa9a9765d0e76b'),
(40,'email_bcc','The BCC field specifies the email addresses of any recipients that were included in the blind carbon copy header of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,'6a48759f51e3d8a66b835301b1a727d262a6b3ef'),
(41,'email_cc','The CC field specifies the email addresses of any recipients that were included in the carbon copy header of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,'68371fc79d742ff2db529c44acaf099be3a67a70'),
(42,'email_content_type','The Content-Type field specifies the internet media, or MIME, type of the email message content.','^.+$',1,0,1,1,0,'b6ab55163e3af397c5d82cb580e4fe3ec6af2d10'),
(43,'email_errors_to','The Errors_To field specifies the entry in the (deprecated) errors_to header of the email message.','^.+$',1,0,1,1,0,'0c11492a0b736671417e0e9b3131e2eb7a0092fb'),
(44,'email_from','The From field specifies the email address of the sender of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,0,1,1,1,'9cfa1e1b74a725ac80fd0dfb152c69795b956540'),
(45,'email_in_reply_to','The In_Reply_To field specifies the message ID of the message that this email is a reply to.','^.+$',1,0,1,1,0,'77b560640d7f6e65c17062fe3d05a5f7c0a7e1fb'),
(46,'email_message_id','The Message_ID field specifies the automatically generated ID of the email message.','^.+$',1,0,1,1,0,'3653ff4cccfe55bb2fed6ea3ea719391a062b771'),
(47,'email_mime_version','The MIME-Version field specifies the version of the MIME formatting used in the email message.','^.+$',1,0,1,1,0,'d14e8733628955dadf696d216aaec048cf87b1e4'),
(48,'email_raw_body','The Raw_Body field specifies the complete (raw) body of the email message.','^.+$',1,6,1,0,0,'f5239ebbe8cf71d51ef677daeae0f44127ccb400'),
(49,'email_raw_header','The Raw_Header field specifies the complete (raw) headers of the email message.','^.+$',0,9,1,1,0,'daf734a6e8be0d50df78677781de72f028b8c46a'),
(50,'email_receive_datetime','The Date field specifies the date/time that the email message was received by the mail server.','^.+$',2,7,1,1,0,'3d9a7ca28b3b3ff62f2781d55b31c4b16d8645e7'),
(51,'email_relay_ip','This attribute hold the IP address of an MTA used to deliver the mail.','^.+$',1,0,1,1,1,'53d2d3d8710d87f30e0dbf9c9e3402e5591d9c4b'),
(52,'email_reply_to','The Reply_To field specifies the email address that should be used when replying to the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,0,1,1,0,'e7e13244a1c3a1001179988839e47190c2cf626d'),
(53,'email_send_datetime','The Date field specifies the date/time that the email message was sent.','^.+$',2,7,1,1,0,'abc6f6f3777583b597092c0090f2f1c9929a449c'),
(54,'email_sender','The Sender field specifies the email address of the sender who is acting on behalf of the author listed in the From: field','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,0,1,1,0,'24050f8ebda3f3df834ffd5ee62e5a318190363f'),
(55,'email_server','The Email_Server field is optional and specifies the relevant email server.','^.+$',1,0,1,1,0,'a1280bfd768d3e8893e6b6351abc0cf6f9256ae5'),
(56,'email_subject','The Subject field specifies the subject (a brief summary of the message topic) of the email message.','^.+$',1,0,1,1,0,'c65e25f2cb5dd8b3d06304140c4b32630da90072'),
(57,'email_to','The To field specifies the email addresses of the recipients of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,'bbf38bcd3885244a12cb810555a228202f0b42c8'),
(58,'email_x_mailer','The X-Mailer field specifies the software used to send the email message. This field is non-standard.','^.+$',1,0,1,1,0,'070462f965613c3b0724bd8bc44325f918c3391b'),
(59,'email_x_originating_ip','The X-Originating-IP field specifies the originating IP Address of the email sender, in terms of their connection to the mail server used to send the email message. This field is non-standard.','^.+$',1,0,1,1,0,'c70df9c50334a3a293c4668106eaf82ce144916d'),
(60,'code_language','The code_language field refers to the code language used in the code characterized in this field.','^.+$',1,0,1,1,0,'460ee7310df5fe214a27a4e1d37cd0b3a8c97634'),
(61,'processor_family','The processor_family field specifies the class of processor that the code snippet is targeting. Possible values: x86-32, x86-64, IA-64, PowerPC, ARM, Alpha, SPARC, z/Architecture, eSi-RISC, MIPS, Motorola 68k, Other.','^.+$',1,0,1,1,0,'7f6112d4ff60ca53698ebf41089d26e394cb6803'),
(62,'targeted_platform','The Targeted_Platforms field specifies a list platforms that this code is targeted for.','^.+$',1,0,1,1,0,'ca79fd7458448da044aa8d00fb8e5ef284786edb'),
(63,'antivirus_record','The results of one or many antivirus scans for an object. This is a multiline csv value (datetime, engine, result, threat name).','^.+$',1,5,1,1,0,'527763bd485569daa6932fd54f26a2097989a891'),
(64,'ida_pro_file','An IDA pro file.','^.+$',1,6,1,1,0,'ac40cb187dae87fb3df620d6e9e0dd0911dd5bee'),
(65,'log_records','Free text for storing log information.','^.+$',0,9,1,1,0,'1eb94af819d5d07fcd0d9796e831782ba3df2eda'),
(66,'whois','Whois network information','^.+$',0,9,1,1,0,'f70a4f20e5aac42543af7ebd6fd0102cd7b20b52'),
(67,'asn','The asn value specifies an identifier for an autonomous system number.','^.+$',1,0,1,1,1,'c4b7ba59f89604d79e518bf8b48fe434ff8b20c7'),
(68,'domain','Contains a fully qualified domain name','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,'61f2d8f22ad9225e600c3eefb1f73aed0a4249b4'),
(69,'file_content_pattern','Contains a pattern that can be found in the raw file data','^.+$',1,0,1,1,0,'f49f038063fbfdc016812993978936de8278f80b'),
(70,'file_full_path_pattern','A pattern that matches the full path of a file','^.+$',1,0,1,1,0,'44527df11fe11a85e442473dc14b7c3cb516b631'),
(71,'file_name_pattern','A pattern that matches the file name','^.+$',1,0,1,1,0,'1b06f42af72052dd3b244575099044c9ef948499'),
(72,'hostname_c&c','Fully qualified domain name of a host hosting a command and control server','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,1,'3030c45848fa71ebe5a658ba69ebe9c80eb51fa7'),
(73,'ids_rules','Holds IDS rules. These rules need to be prefixed with the used format (e.g. snort).','^.+$',0,9,1,1,0,'c70c84d41c9cdb556aa01cf5b052881e286569ea'),
(74,'ipv4_addr','The IPv4-addr value specifies an IPV4 address.','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$',1,5,1,1,0,'9ea7c45fc7512c4b99e2c072ae24e495f2007a60'),
(75,'ipv4_addr_c&c','IPv4 address hosting a command and control server','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$',1,5,1,1,1,'bc0a065aa9458c8332517e678dc2cf11d2e47ab7'),
(76,'ipv4_net','IPv4 CIDR block','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}/\\d{1,2}$',1,5,1,1,0,'6821ac2b0f1e0285be361410421b134fd7b02cdb'),
(77,'ipv6_addr','The IPv6-addr value specifies an IPv6 address.','^.+$',1,5,1,1,0,'8eec76aa6579e1daa7b5ea48e82d4c5499a72840'),
(78,'ipv6_addr_c&c','IPv6 address hosting a command and control server','^.+$',1,5,1,1,1,'1788e4f3bf6fd6a2b4ccd1e1761d851d3a8b5721'),
(79,'ipv6_net','IPv6 sub-network','^.+$',1,5,1,1,0,'2e46a68d600ea213f16f13e6560d2a460dc4fde0'),
(80,'mutex','The Mutex object is intended to characterize generic mutual exclusion (mutex) objects.','^.+$',1,0,1,1,0,'52e2ac163496946c6f89f7749dcfa1b30498521f'),
(81,'open_ioc_definition','Hold open IOC definitions.','^.+$',1,6,1,1,0,'77c72fa92a2a84b3176f9f101a7465b0fa6cd583'),
(82,'trafic_content_pattern','Pattern matching network traffic content.','^.+$',1,0,1,1,0,'afb1630220f294fa14c62bc7be5dba8f3973c704'),
(83,'url','Holds a complete URL (e.g. http://www.govcert.lu/en/index.hmtl)','^.+$',1,5,1,1,0,'a3ca7d9357ed835069fc1e4e0969608c43178cf4'),
(84,'url_path','Holds only the path part of an URL. (e.g. /en/index.html)','^.+$',1,5,1,1,0,'4d966ad1d920da2053bdbdf29e1b8e012bc7aa96'),
(85,'url_pattern','Holds a pattern that matches URL.','^.+$',1,5,1,1,0,'89d93b434b4aae1c9845fafc626f54d2adf05291'),
(86,'win_registry_key','The WindowsRegistryObjectType type is intended to characterize Windows registry objects, including Keys and Key/Value pairs.','^.+$',0,9,1,1,1,'2d110b2d1019751b7e09ed5831320364b88626de'),
(87,'yara_rule','Holds YARA rules used to identify and classify malware samples.','^.+$',0,9,1,1,1,'cdb3d8e146f88e7ab652207429afa5458da55dd1'),
(88,'mime_type','File mime-type','^.+$',0,0,0,1,0,'1498236cfea91bc2b7fe82625ec223e9dc6f4710'),
(89,'compromized_hostname','compromized_hostname','^.+$',1,0,1,1,1,'64f2717e8ceb9f660e776399d022476a276d9dcd'),
(90,'ipv4_addr_phishingSite','ipv4_addr_phishingSite','^.+$',1,0,1,1,1,'9ba844adf500b08be89a389d2cbba0716d554da6'),
(91,'ip_port','IP Port','^[\\d]{1,}$',3,0,1,1,0,'2c4312677d38a636ba1d77fe150bce7ecea345ac'),
(101,'ip_protocol','IP Protocol','^tcp$|^udp$|^icmp$',1,8,1,1,0,'5271302bbb13211bb4f2e09c4a5b7628b8520506'),
(111,'file_id','File description as returned by unix “file” command','^.+$',1,0,0,1,0,'2a4380007eec26779e9cf203dda1da3094a3d1db');
/*!40000 ALTER TABLE `DEF_Attributes` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `DEF_Objects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DEF_Objects` (
  `def_object_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` mediumtext,
  `chksum` varchar(45) DEFAULT NULL,
  `sharable` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`def_object_id`),
  UNIQUE KEY `chksum_UNIQUE` (`chksum`),
  KEY `IDX_def_objects_chksum` (`chksum`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
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
(10,'source_code','source_code\r\n\r\nThis includes all uncompiled code','0c4fa34ab948d93a78795a5301c11f772a635620',1);
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `DObj_has_DAttr` WRITE;
/*!40000 ALTER TABLE `DObj_has_DAttr` DISABLE KEYS */;
INSERT INTO `DObj_has_DAttr` VALUES (1,1),
(5,1),
(6,1),
(10,1),
(1,2),
(5,2),
(6,2),
(10,2),
(1,3),
(5,3),
(6,3),
(10,3),
(1,4),
(5,4),
(6,4),
(10,4),
(1,5),
(5,5),
(6,5),
(10,5),
(1,6),
(2,6),
(6,6),
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
(6,15),
(7,15),
(8,15),
(9,15),
(10,15),
(1,16),
(2,16),
(3,16),
(4,16),
(6,16),
(7,16),
(8,16),
(9,16),
(10,16),
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
(5,40),
(5,41),
(5,42),
(5,43),
(5,44),
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
(8,84),
(8,85),
(8,86),
(8,87),
(1,88),
(6,88),
(8,91),
(8,101),
(1,111),
(6,111);
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  `description` text,
  `title` varchar(255) DEFAULT NULL,
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
  `uuid` varchar(45) DEFAULT NULL,
  `creatorGroup` int(11) NOT NULL DEFAULT '1',
  `code` int(1) NOT NULL,
  PRIMARY KEY (`event_id`),
  KEY `IDX_Events_uuid` (`uuid`),
  KEY `IDK_Events_creator_id` (`creator_id`),
  KEY `IDX_Events_modifier_ID` (`modifier_id`),
  KEY `IDX_Events_creatorGroup` (`creatorGroup`),
  KEY `fk_Events_1` (`creatorGroup`),
  KEY `FK_Events_Groups_creatorGroup_groupID` (`creatorGroup`),
  CONSTRAINT `FK_Events_Groups_creatorGroup_groupID` FOREIGN KEY (`creatorGroup`) REFERENCES `Groups` (`group_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Events_User_creator_user_ID` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Events_User_modifier_user_ID` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
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
  `name` varchar(45) DEFAULT NULL,
  `description` mediumtext,
  `canDownlad` int(1) NOT NULL DEFAULT '0',
  `tlplvl` int(1) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `usermails` int(1) NOT NULL DEFAULT '0',
  `pgpKey` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`group_id`),
  KEY `IDK_Groups_tlplvl` (`tlplvl`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Groups` WRITE;
/*!40000 ALTER TABLE `Groups` DISABLE KEYS */;
INSERT INTO `Groups` VALUES (1,'Default_Group','Default Group, for all users',0,3,'a@a.com',0,NULL);
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Groups_has_Events` WRITE;
/*!40000 ALTER TABLE `Groups_has_Events` DISABLE KEYS */;
INSERT INTO `Groups_has_Events` VALUES (1,1);
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  `uuid` varchar(45) DEFAULT NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  `value` varchar(255) DEFAULT NULL,
  `attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`StringValue_id`),
  KEY `IDX_StrValues_attr_id` (`attribute_id`),
  KEY `IDX_StrValue_Value` (`value`),
  CONSTRAINT `fk_StringValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  `name` varchar(45) NOT NULL,
  `description` varchar(255) NOT NULL,
  PRIMARY KEY (`subgroup_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  `value` longtext,
  `attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`TextValue_id`),
  KEY `IDX_TextValues_attribute_id` (`attribute_id`),
  CONSTRAINT `FK_TextValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  `username` varchar(45) CHARACTER SET latin1 COLLATE latin1_bin NOT NULL COMMENT '\n',
  `password` varchar(255) NOT NULL,
  `privileged` int(1) DEFAULT '0',
  `last_login` datetime DEFAULT NULL,
  `email` varchar(45) CHARACTER SET latin1 COLLATE latin1_bin NOT NULL,
  `disabled` int(1) NOT NULL DEFAULT '1',
  `apikey` varchar(255) DEFAULT NULL,
  `group_id` int(11) DEFAULT '1',
  `pgpKey` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `apikey_UNIQUE` (`apikey`),
  KEY `IDX_User_Group_Group_id` (`group_id`),
  CONSTRAINT `FK_User_Group_Group_id` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`group_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES (1,'admin','dd94709528bb1c83d08f3088d4043f4742891f4f',1,'2013-12-10 11:57:14','admin@admin.com',0,NULL,1,NULL);
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `ce1sus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ce1sus` (
  `key` varchar(45) NOT NULL,
  `value` varchar(100) DEFAULT 'None',
  PRIMARY KEY (`key`),
  UNIQUE KEY `key_UNIQUE` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `ce1sus` WRITE;
/*!40000 ALTER TABLE `ce1sus` DISABLE KEYS */;
INSERT INTO `ce1sus` VALUES ('app_rev','0.4.0'),
('db_shema','0.5.0'),
('definitions','5.9.2'),
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

