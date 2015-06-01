#﻿DocumenFtation

The documentation is still under development

##1. Installation
In the folder *scripts/install* there is a shell script which makes the a generic installation for you, for 
further configurations please see the next sections

###1.1. Requirements

Ce1sus need the following packages:

* python
  * python (2.7+)
  * sqlalchemy (0.7.8+)
  * mysqldb (1.2.3)
  * python-magic (0.4.6+)
  * python-ldap (2.4.10+)
  * dateutil (1.5+)
  * cherrypy3 (3.2.2+)
  * memcache
  * rtkit (0.6.0+)
  * gnupg (0.3.5+)
  * eml_parser
- mysql (5.1+)
- nginx (1.4+)
- uwsgi (1.2.3+, with python-2 support)
- python-stix (1.1.1.5) 
- python-cybox (2.1.0.11)
- openioc-to-stix (0.12+)


###1.1.2 Installation of the requirements

Debian based systems can execute the following command:

``` shell
sudo apt-get install python-cherrypy3 python-dateutil python-gnupg python-ldap python-memcache python-mysqldb python-sqlalchemy mysql-server python-mako git memcached
```

##1.2. Clone the repository

``` shell
git clone https://github.com/GOVCERT-LU/ce1sus
```

###1.2.1 Python magic
 
One possibility to install python-magic is the following

Go to your ce1sus installation directory and:

``` shell
mkdir libs
cd libs
git clone https://github.com/ahupp/python-magic
cd ..
ln -s libs/python-magic/magic.py .
```

The important fact is that the magic package must be accessible with "import magic"

###1.2.2 Email parser

One possibility to install eml_parser is the following

``` shell
mkdir libs
cd libs
git clone https://github.com/sim0nx/eml_parser
cd ..
ln -s libs/eml_parser/eml_parser .
```

###1.2.3 Cybox

One possibility to install eml_parser is the following

``` shell
mkdir libs
cd libs
git clone https://github.com/CybOXProject/python-cybox.git v2.1.0.11
cd ..
ln -s libs/python-cybox/cybox .
```

The other is it to install it via pip.

###1.2.4 Stix

One possibility to install eml_parser is the following

``` shell
mkdir libs
cd libs
git clone https://github.com/STIXProject/python-stix.git v1.1.1.5
cd ..
ln -s libs/python-stix/stix .
```

###1.2.5 rtKit

One possibility to install eml_parser is the following

``` shell
mkdir libs
cd libs
git clone https://github.com/z4r/python-rtkit.git 0.6.0
cd ..
ln -s libs/python-rtkit/rtkit .
```

###1.2.5 OpenIOC

One possibility to install eml_parser is the following

``` shell
mkdir libs
cd libs
git clone https://github.com/STIXProject/openioc-to-stix.git
cd ..
ln -s libs/openioc-to-stix/ioc_observable.py .
ln -s libs/openioc-to-stix/openioc.py .
ln -s libs/openioc-to-strix/opendioc_to_cybox.py .
```

**Note**: This implementation may change in future

##1.3. Database


###1.3.1 Database creation

``` sql
CREATE DATABASE ce1sus;
``` 

###1.3.2 DB User


Create a db user for ce1sus user must have the following grants:

* INSERT
* SELECT
* DELETE
* UPDATE

``` sql
CREATE USER 'ce1sus'@'localhost' IDENTIFIED BY 'password';
GRANT INSERT, SELECT, DELETE, UPDATE  ON 'ce1sus'. * TO 'ce1sus'@'localhost';
FLUSH PRIVILEGES;
```

###1.3.3 DB SCHEMA

The creation of the db schema changed since 0.11.X and is now done via a script. To initialize the database do the following:

``` shell
cd scripts/installation/database
python db_init.py
```

Everything needed will be created automatically. If there should be migrations the scripts for the migration will be provided 
the scripts/migrations folder, use these in order.

**NOTE 1**: db_init.py also will create gpg keys in case they are not existing at the given location. It is perferably to create them
manually as this takes some time to generate them if the system is not busy.

**NOTE 2**: Set for the database initialization the user in the configuration file to a user which has the permissions to create tables.

###1.3.4 Remarks

Depending on your DB server it is advised to have a tmp folder with at least 1 GB space.


##1.4 Ce1sus Configuration


###1.4.1a Celsus.conf

Go to your ce1sus installation directory and create configuration file ce1sus.conf in the config directory 
use the file *config/ce1sus.conf_tmpl* as template

``` shell
cp config/ce1sus.conf_tmpl config/ce1sus.conf
```

The following sections have to be modified to the settings of your system

- [SessionManager]
- [ce1sus]
- [Logger]
- [LDAP]
- [Plugins]
- [Mailer]
- [MISPAdapter]
- [Errorhandler]

The next paragraphs will explain in more detail what has to be changed and what the different elements in the 
configuration do and their values.

The **[SessionManager]** section stores the settings of the database connection and has the following elements

|variable name | Description |
|--------------|-------------|
|protocol=[mysql+mysqldb,mylsql,sqlite] | Defines the protocol used for the connection |
|username=                         | Username of the db user i.e. "ce1sus" without quotes, can be left blank for sqlite| 
|password=                         | Password of the db user i.e. "ce1sus" without quotes, can be left blank for sqlite |
|host=127.0.0.1                    | IP address of the db server|
|db=                               | Database name i.e. "ce1sus" without quotes|
|                                  |  If the sqlite protocol is chosen the element db must correspond to the absolute path|
|                                  |  to the sqlite file|
|port=3306                         | Port of the db server, is ignored for sqlite|
|debug=[no,yes ]                 | If set to "yes" the sql queries will be shown in the logs| 
|usecherrypy=[yes,no]            | If set to "yes" a single connection is used else multiples|
|                                  |  **Note**: Do not change this value unless you know what you are doing|

The **[ce1sus]** section stores the general settings of ce1sus and has the following elements

|variable name | Description |
|--------------|-------------|
|useldap=[no,yes]                  | If "yes" the users can also be authenticated by ldap|
|                                  |  Note: When set [LDAP] section has to be set and look in section XXXX how ldab users| 
|                                  |        needs to be configured |
|environment=LOCAL_DEV             | Text displayed in the header of the ce1sus web page. Used to separate dev| 
|                                  |  environment and production.|
|                                  |  **Note** This value can be empty|
|baseurl=http://localhost:8080     | The root url of your ce1sus server, this url is needed to build the links in the emails|
|maintenaceuseruuid=               | The user uuid which is used by the maintenance.py script and used for the sync mechanism|
|usebasicauth=[yes,no]             | enable basic authentication|
|salt=                             | A random used to salt the hashes of passwords|

The **[Logger]** section stores the configuration how the logs are stored/processed and has the following elements

|variable name | Description |
|--------------|-------------|
|log=[Yes,No]                                           | If set ce1sus does log|
|                                                       |  **Note**: It is advised that this element is set to "yes"|
|log_file=log/logger.txt                                | Absolute or relative path for storage of log files|
|logConsole = [Yes,No]                                  | If set ce1sus logs to the console and the file|
|level=[CRITICAL,ERROR,WARNING,INFO,DEBUG]              | Log level|
|size=10000000                                          | Size in bytes of the file before it gets rotated|
|backups=1000                                           | Number of log backups|
|syslog=[Yes,No]                                        | Log to syslog|

The **[LDAP]** section stores the configuration of the LDAP plugin and has the following elements

|variable name | Description |
|--------------|-------------|
|server=|The server to use for the ldap connection|
|usetls=[True, False]|Use TLS|
|users_dn=||

The LDAP configuration only makes sense if useldap is set on the ce1sus section and LdapPlugin is set in the Plugins section.

The **[Plugins]** section defines which "Plugins" are available to use

|variable name | Description |
|--------------|-------------|
|LdapPlugin=[Yes,No]                                    | Enables the Ldap plugin|
|                                                       | **Note**: If the ldapplugin is activated the section LDAP and the useldap|
|                                                      |        in the ce1sus section have to be set|
|MailPlugin=[Yes,No]                                    | Enables the mail plugin|
|                                                       |  **Note**: If the mail plugin is not enabled no mails will be send out, this has no impact except that new users have to be activated manually.|

The **[Mailer]** section stores the configuration for sending mails and has the following elements

|variable name | Description |
|--------------|-------------|
|from=ce1sus                                            | Sender email|
|smtp=                                                  | Smtp server|
|port=25                                                | Port of the smtp server|
|user=                                                  | Not implemented|
|password=                                              | Not implemented|
|keyfile=                                               | Folder of the gpp files used to sign or encrypt (i.e. ~/gpgkey)|
|passphrase=                                            | Pass-phrase for unlocking the gpg key|
|keylength=1024                                         | Length of the gpg key in case it should be generated automatically|
|expiredate=[YYYY-MM-DD]                                | Expiry date of the generated key |

The **[MISPAdapter]** section provides you to enable dumping of the gotten Misp events

|variable name | Description |
|--------------|-------------|
|dump=[yes,no]           | Enable dumping of misps|
|file=mispdump           | Absolute path to a folder where the misps should be dumped|

The [OpenIOCAdapter] section provides you to enable dumping of the gotten Misp events

|variable name | Description |
|--------------|-------------|
|dump=[yes,no]           | Enable dumping of openIOC xml|
|file=openiocdump        | Absolute path to a folder where the misps should be dumped|


The **[ErrorMails]** section stores the configuration of the error mails. These mails are send in case a HTTP 500 error occurs.

|variable name | Description |
|--------------|-------------|
|enable=[no,yes]                                        | When set an mail is sent to the receiver with the error stack trace|
|sender=ce1sus                                          | Sender email|
|receiver=ce1sus                                        | The destiation address. Only one can be specified|
|subject=ErrorOccureredForCelsus                        | Email subject for error mails|
|smtp=                                                  | Smtp server|
|port=25                                                | Port of the smtp server|
|level=info                                             | Not used yet|
|user=                                                  | Not implemented|
|password                                               ||

###1.4.1b handler.conf

Go to your ce1sus installation directory and create configuration file handlers.conf in the config directory 
use the file *config/handlers.conf_tmpl* as template

``` shell
cp config/handlers.conf_tmpl config/handlers.conf
```
The following sections have to be modified to the settings of your system

**[FileHandler]**

|variable name | Description |
|--------------|-------------|
|files=/path/to/ce1sus/files                           | The absolute file path where ce1sus can store/archive the| 
|                                                      |  uploaded files as attributes.|
|                                                      |  The user (i.e 'www-data') of ce1sus must have access on that directory|

**[CVEHandler]**

|variable name | Description |
|--------------|-------------|
|cveUrl=http://cve.mitre.org/cgi-bin/cvename.cgi?name=     | Base url for cves. (used by the CVEHandler)|

**[RTHandler]**

|variable name | Description |
|--------------|-------------|
|rt_user=                                               | The user used for accessing the RESTAPI for RT|
|                                                       | (Used by RTHandler)|
|rt_password=                                           | The user password used for accessing the RESTAPI for RT|
|rt_url=                                                | Base url of RT (i.e https://localhost/rt/Ticket/Display.html?id=)|

**[FileReferenceHandler]**

|variable name | Description |
|--------------|-------------|
|files=/path/to/ce1sus/reference_files                 | The absolute file path where ce1sus can store/archive the| 
|                                                      |  uploaded files in the refrence section.|
|                                                      |  The user (i.e 'www-data') of ce1sus must have access on that directory|

**[FileWithHashesHandler]**

|variable name | Description |
|--------------|-------------|
|files=/path/to/ce1sus/files                            | The absolute file path where ce1sus can store/archive the| 
|                                                       | uploaded files as attributes.|
|                                                       | The user (i.e 'www-data') of ce1sus must have access on that directory|

###1.4.2 Cherrypy.conf

Go to your ce1sus installation directory and create configuration file cherrypy.conf in the config directory 
use the file *config/cherrypy.conf_tmpl* as template

``` shell
cp config/cherrypy.conf_tmpl config/cherrypy.conf
``` 

The following lines must be modified according to your installation

``` ini
tools.staticdir.root='/path/to/ce1sus/htdocs'
```

The session handling can be done in two ways:

For memcache (when memcached is installed) used the following:

tools.sessions.storage_type = 'Memcached'

For files use:

``` ini
tools.sessions.timeout = 15
tools.sessions.storage_type = "file"
tools.sessions.storage_path = "/path/to/ce1sus/sessions"
``` 

But we strongly advise you to use memcache
 
**Note**: This is a standart cherrypy configuration file. For more information on that subject see http://cherrypy.readthedocs.org/en/latest/tutorial/config.html

##1.5 Test configurations

Go to your ce1sus installation directory and launch
``` shell
python ce1sus-run.py
```

and access http://localhost:8080, except you configured in the cherrypy.conf that sockets had to be used

This is a method to see if ce1sus can start correctly. If this is the case continue to section 1.6

###1.5.1 Troubleshooting

If you are reading this you may have encoutered troubles when launching a local copy of ce1sus (see section 1.5). 

Errors during stat:

```
*'MySQLConnection' object has no attribute 'get_characterset_info'*
-> connector issues try change it to mysql+mysqldb or mysql
```

##1.6 uwsgi

Install uwsgi and uwsgi-plugin-python
``` shell
apt-get install uwsgi uwgsi-plugin-python
``` 

In the config folder of your ce1sus installation folder you'll find ce1sus.ini_tmpl a template for the configuration of 
uwsgi. 

Copy the file to uwsgi:
``` shell
cp scripts/install/uwsgi/ce1sus.ini_tmpl config/ce1sus.conf /etc/uwsgi/apps-available/ce1sus.ini
```

Edit /etc/uwsgi/apps-available/ce1sus.ini and replace "/path/to/ce1sus" with your ce1sus installation path

Enable ce1sus in uwsgi:
``` shell
ln -s /etc/uwsgi/apps-available/ce1sus.ini /etc/uwsgi/apps-enabled/
``` 

Restart service
``` shell
/etc/init.d/uwsgi restart
```

##1.7 nginx

Install nginx

``` shell
apt-get install nginx
```

In the config folder of your ce1sus installation folder you'll find ce1sus_tmpl a template for the configuration of nginx. 

Copy the file to uwsgi:

``` shell
cp scripts/install/nginx/ce1sus_tmpl config/ce1sus.conf /etc/nginx/sites-available/ce1sus
``` 
Create a self signed certificate for ce1sus:

``` shell
openssl req -x509 -nodes -days 7300 -newkey rsa:2048 -keyout /etc/ssl/private/ce1sus.key -out /etc/ssl/certs/ce1sus.pem
chmod 600 /etc/ssl/certs/ce1sus.pem
chmod 600 /etc/ssl/private/ce1sus.key
```

Edit /etc/nginx/sites-available/ce1sus and replace "/path/to/ce1sus" with your ce1sus installation path

**Note**: If you have own already a certificat you need to adapt the confuration file of nginx accordingly.

Enable the ce1sus site:
``` shell
ln -s /etc/nginx/sites-available/ce1sus /etc/nginx/sites-enabled/
```

Restart service

``` shell
/etc/init.d/nginx restart
``` 
Login as admin with password admin

###1.7.1 Troubleshooting

Nginx shows a 404 or 403:

403: means that the folder is accessible but the file i.e. index.html is not available, location element is missing from the folder

404: the root folder was set up incorrectly

##1.8. Scheduler

The scheduler has to run in the background to performs the following actions:


* Publication
** Send Publication mail
** Pushes the event to the syncronization servers
* Pull (pulls all the scheduled events from a remote servers)
* Push (Push all the scheduled events to a remote servers)
* Proposal (Sends notification mails that a proposal has been inserted)
* Relations (Generates the relations in the background)
* Publish update (Sends out update mails for events)


To activate the scheduler create a cronjob. The following example is set to run every 5 minutes.
 
 ``` shell
-------
5 * * * * python /path/to/ce1sus/scheduler.py
 ```

##1.9 DB migration

If you are migrating from 0.10 to 0.11.0 proceed like stated below

First dump your current database.

``` shell
cd scripts/migration
python dump_0.10.py -c ../../config/ce1sus.conf --dest dumps
```

The script will use the settings in the ce1sus.conf and dumps it into the folder ./dumps

The next step is to setup a new db schema (drop the old one) and follow the steps described in 1.3.3

Finally migrate the dropped data into the new database

``` shell
cd scripts/migration
python migrate_0.10_to_0.11.0.py  -d dumps
```

The script used the configuration of the later instance. 

**Note** the migration can take some time depending on the volume of your database.


#2. Web Interface

The web interface of Ce1sus has two sections:

1. Administration
  The administration section is used to:
     * Validate events inserted over the RESTAPI
     * Define definitions for objects, attributes, references
     * User management
     * Group management
     * Server managment
     * Editing mail templates

2. User interface
The event view is used to:
  * Search for attributes
  * Add/Edit events
  * View events
     * Overview
     * Observables
     * Indicators
     * Relations
     * Reports
     * Groups
            
3. Event details

##2.1 Administration


This section describes the administration interface. This interface is only accessible to users with with the 
privileged flag set.

###2.1.1 Validation


This list shows the unvalidated Events inserted via REST. The operations which can be performed are similar to the one 
described in section 2.2.3 except that the main event overview cannot be edited.

To validate an event one has only to click on the "Validate" button. 

**Note**: Unvalidated Events will not be viewable in the RecentEvent section, nor via search, nor in relations until they got
      validated.

###2.1.2 Usermanagment

![ce1sus user mgt](/docs/images/ce1sus_usermgt.png)

Ce1sus offers, when ldap is enabled, to insert users from ldap. This is done by selecting the user from the list when "Add LDAP" is pressed. In case ldap is not enabled the button will not be shown. 

A user has the following properties:

|Field | description|
|------|------------|
|Identifier   | Generated id|
|Name         ||
|SirName      ||
|Username     ||
|Password     | The password's minimal requirements are lower, upper case, numbers, symbols and have a length of 8 characters.|
|             | **Note** if the password 'EXTERNALAUTH' is dispalyed the user is authenticated by LDAP (see section 1.4.1 for| 
|             | LDAP Configuration)|
|Email        | The email has to be specified if the ce1sus is configured to sendmails.|
|Get notifications | If this is set the user gets nofitications on updates or publishing of new events|
|GPGKey       | If no gpg key was specified the user receives only mails for events with TLP White.|
|             | **Note**: Depending on the group settings the user may not recieve any mails. See section 2.1.6|
|API Key  | The key to access the api|
          | This key can be generated automatically over the button Gen. in the edit or add window.|
|Privileged   | If set the user can access the administration area|
|Disabled     | If set the user cannot log in anymore|
|Manage own group | Not used yet | 
|Group   | The group the user belongs to. This group is also denoted by creator group. |

**Note**: 
*If ce1sus/sendmail is set the user will receive an activation mail and his account has to be activated within 24 hours.
*If the user account is not activated within 24 hours, the account stays in disabled mode to reenable it either activate it manually or resend the activation mail.
*In case the sendmail is not set one must activate the user manually.
          
###2.1.3 Groups

![ce1sus group mgt](/docs/images/ce1sus_usermgt.png)


The Groups specify the group for users and have the following properties:

|Field|Description|
|---------------------------|---------------------|
|Identifier                 | Generated identifier|
|Name                       | Name of the group|
|Description                | Description of the group|
|Email                      | group email|
|GPGKey                     | If no gpg key was specified the group receives only mails for events with TLP White.|
|                           | **Note**: Depending on the group settings the user may not receive any mails. See section 2.1.6|
|Get notifications | If this is set the user gets nofitications on updates or publishing of new events|
|TLP                        | TLP level for this group. If this is set i.e. Amber it is possible for this group to access all amber and lower events|
|Can download files             | If set the users of the group can download files|
|TLP Propagation | If this is set the highest level will be chosen from the group itself and its associcated groups|
|Associated Groups       | Groups which are associvated to this group|

The default event permissions are the permissions set by default when the group is associated to an event. Please look section 2.2.3 for more informations on the different permissions.

**Note**: It is enough that a group has an associated group to let the users of the group view an event.

###2.1.4 Definitions

####2.1.4.1 Object

![ce1sus object mgt](/docs/images/ce1sus_objmgt.png)

The objects definitions can be considered as attribute containers. These containers limit the choice of attributes and 
ease the use for the user to choose an appropriate attribute, without being overwhelmed by attributes which may be 
ambiguous. These object containers will be refereed by object definitions. These containers are based on the Cybox standart. The object definitions which cannot be edited and show the cybox logo, are part of the 
standard. 

*Example*: Object Email cannot have a mutex, therefore the attribute mutex is not part of the object container

An object definition has the following properties:

|Field|Description|
|-----|-----------|
|Identifier                 | Generated identifier|
|Name                       | Name of the object container (i.e. Email)|
|Checksum                   | Checksum of the object container. This checksum is used to identify an object container|
|                           | Note: The checksum is the SHA1 hash of the name|
|Description                | Description of the object|
|Default Shareable          | The default value for sharing|
|                           | Note: These values can be overridden, by the user|
|Associated Attributes      | Attributes which belong to the object container|

Objects definitions can be added, edited and deleted. The deletion only works if the object is not referenced anymore.

**Note**: Do not forget to add attribute definitions to the object else one is only able to add the object to the event.

####2.1.4.2 Attributes

![ce1sus object mgt](/docs/images/ce1sus_attrmgt.png)

The attribute definition are the definition what an attribute can be.

An attribute definition has the following properties:

|Field | Description|
|------|------------|
|Identifier                 | Generated identifier|
|Name                       | Name of the attribtue (i.e. mutex)|
|Checksum                   | Checksum of the object container. This checksum is used to identify an object container|
|                           | **Note**: Checksum is SHA1(name + regex + class_index + handler.uuid)|
|Description                | Description of the attribute|
|Regular expression         | A regex of the value which the value has to be checked against|
|                           | Default is "^.+$"|
|Data Type                  | The type of the value of the attribute.(i.e. String, Number)|
|                           | Possible types are String, Text, Number, Date|
|                           | Note: Each type is stored in a different table, to keep a proper database|
|Input handler              | The handler used for the attribute. For more informations on handlers see section 2.1.4.2|
|Base type|Not implemented yet|
|Default condifiton| The condition which is set by default. (i.e. Equals or Fits Pattern)|
|Relation-able              | If this value is set relations between objects are created on entering an attribute or via| 
|                           | the maintenance tools |
|Default Shareable          | The default value for sharing|
|                           | **Note**: These values can be overridden, by the user|
|Associated Object          | Objects which have the attribute definiton associated|

#####2.1.4.2.1 Handlers

Ce1sus support custom handlers, these handlers are used to perform additional operations (i.e. parsing of the email) and
display the attribute values depending on their configuration. The handlers can even create complex structures. One also
must know that the handlers can also provide an complex input form which can be used to create a basic structure for the event for instance.

The handler will be in near future exchangeable therefore the uuid is required, note also that the uuid of the 
AttribtueHandlers table should correspond to the one specified in the handler

Ce1sus supports the following handlers:

|Handler Name          | Supoorted Types      | Description|
|----------------------|----------------------|------------|
|CBValueHandler        | String               | Handles values as combo-box. |
|                      |                      | The regex has to be under a similar form as "^yes$|^no$" for yes, no values|
|                      |                      | Note the number of "|^no$" blocks is not limited|
|CVEHandler            | String               | Handler for CVEs|
|                      |                      | Creates a link to the entered CVE|
|DateHandler           | Date                 | Handler for dates|
|                      |                      | Note: Currently supports only text dates under the form of "YYYY-mm-dd| 
|                      |                      | HH:MM:SS"|
|FileHandler           | String               | Handles fileuploads and generates additional attributes as filename,| 
|                      |                      | hash_sha1 of the file|
|                      |                      | When uploaded the file can be downloaded as a zip file|
|FileWithHashedHandler | String               | Handles fileuploads and generates additional attributes as filename, |
|                      |                      | hash_md5, hash_sha1, hash_sha256, hash_sha384, hash_sha512 of the file|
|                      |                      | When uploaded the file can be downloaded as a zip file|
|GernericHandler       | String, Text, Number | Generic one line handler|
|LinkHandler           | String               | Handler for links|
|                      |                      | The link is displayed as link|
|MultipleGenericHandler| String, Text, Number | Generic multiple line hander|
|                      |                      | Each new line is considered as new attribute with the same properties|
|RTHandler             | Number               | Handler for RT Tickets|
|                      |                      | RT Tickets can be chosen from a table or entered manually.|
|                      |                      | Multiple RT Ticket numbers can be entered in a CSV format|
|TextHandler           | Text                 | Handler for large text i.e. YARA Rules|


######2.1.4.2.1.1 Manual handler insertion

There is not yet an automated installation of such handlers therefore they have to be installed manually. The process is
be explained below

1. Create a handler extending either the Generichandler or HandlerBase
2. Place it in ce1sus.handlers.attribute for attribute handlers or ce1sus.handlers.references for report references.
3. Insert into the Table AttributeHanlders or Referencehandlers
    * The module and classname i.e. generichandler.GenericHandler
    * The uuid for the handler
    * A descripiton
3b. (Optional) Create a configuration in the *config/handlers.conf*

####2.1.4.3 Conditions

The conditions are straigt forward this is only to specify custom contitions on which the attribute can be used. This means that for instance "Equals" means that the attribute value matches 1:1, or "FitsPattern" for a value with wildcards.

####2.1.4.4 Types

Not yet implemented

###2.1.4 Mails

Ce1sus offers the possibility to send mails on different occasions. This however depends on the configuration. 
Therefore the section **[Mailer]** has to be configured. 

**Note**: It is recommended to supply an GPG key for ce1sus else it is only possible to get notifications on event which 
      have a TLP level of white. This folder/key has to be owned by the owner of ce1sus (i.e. www-data) 

If the configuration ce1sus/sendmail is set then ce1sus will send out mails for the following events:

* Event publication/updates
* Event validation if the event is published
* Adding a user

Each mail of the above events use a template which can be configured via the admin interface, for more informations see 
the descriptions of each template.

**Note**:
* If an events gets published or updated only the users who are in the group or subgroup of an event will receive 
  the mail, regardless which TLP level it is.
* If a user in one of the event groups has no GPG key specified, he will only receive a mail it the event is TLP 
  while.
    

###2.1.5 BackgroundJobs

Ce1sus processes some processing in the background, for instance sending emails or syncronisation. In this view one can see
all the jobs which are sceduled.


The view offers the possibility to reschedule, stop, delete the scheduled event.

###2.1.5 SyncServers

This is the view to ass severs which ce1sus syncs with. Currently only MISP and ce1sus instances can be entered.

The fields for a sync server are the following:

|Field|Description|
|-----|-----------|
|Type| The type of the server currently only MISP and ce1sus|
|Name                       | Name of the sever (i.e. circl misp)|
|Description                | Description for the server|
|Associated user | the user which has the informations to access the server. |
|                | **Note**: The user should have the api key and username have to be set to the ones from the remote server|
|Mode | The supported modes by the remote server|
|     | **Push**: means that events can be pushed to this server|
|     | **Pull**: means that events can be pulled from this server|
|Certificate||
|CA Certificate||
|Verify ssl||

**Note**: In this view one can also perform push all or pull all operations, by clicking on the corresponding buttons in the overview of the servers.

##2.2 User interface

The next sections describes the elements of the user interface.

###2.2.1 Events

The event details are composed of the following views:

|Field|Description|
|-----|-----------|
|Overview          | General details of the event, show also Relations beween other events and a possibility to add event comments|
|                  | Note: The event comments are only viewable by priviledged users and the users of the creator group|
|Observables | Lists all the elements seen though the event, the view can be seen under a list or strucktured form|
|Indicators | Lists all the indicators seen though the event, the view can be seen under a list or strucktured form|
|           | **Note**: Currently these indicators are generated automatically. For the attribtues with the IOC flag set|
|Relations         | The relations of the event. These are more detailed as the one on the overview page. These relations|
|                  | show the related event, object and the attribute who made the relation, it the attribute is relation-able.|
|                  | See section 2.1.5 for more information on relations.|
|Groups            | Group management of the event. Ech group associated to the event permits the users of that group to| 
|                  |  view the event. |
|                  |  **Note**: Only users of groups with the *set group* flag set view/change the associated goups.|

####2.2.1.1  Overview

The Overview view gives a genral view of the event, like the other related events, wich group it inserted and from which group it came to you. And comments.

**Note**: The comments are only viewable by the owner of the event. These are mainly used for comments related to the evnet.

**Note2**: Owners or priviledged users can change the ownership of the evnet via the *Change ownership* button. 

####2.2.1.2  Observables

The observables are an implementation of the observables found in Cybox/STIX. 

The observable does not require anything every field is optional.

Inside such observable one can specify objects which then represent the item of an event like a File with all its attributes. The objects can have child objects. This is how the structures are set up.

Currently combined observables can only be created via the REST API. 

The observables can be viewed in their structured form or in a list like view. The view can be changed by selecting the desired view via the button *View Mode*

####2.2.1.3 Indicators

The indicator view show the indicators of the event. It can also similar as the observables shown in a structured or list view.

**Note** The indicators are created automatically for the attributes with the IOC flag set.

**Note2** Indicators can currently only be created via the REST API, but as soon as indicators have been manually created, one must take care for all of the indicators are the automatically generated ones will not be available anymore.

####2.2.1.4 Relations
The relations view shows all the relations found between events on their attribute level. 

This view is not editable

####2.2.1.5 Reports

####2.2.1.6 Groups

The groups associated to the event, provide the users of the group to view the event, event if the TLP level is too high. This is servers the purpose to cooperate/share informations of the event with all the parties involved.
The other thing is that every associated group can have serveral permissions, which are only valdi for the event in context.

The permissions available are the following

|Permission|Description|
|-----|-----------|
|Add|Permission to add items to the event|
|Modify| Permission to modify items in the event|
|      | **Note** This does not imply that the add right or delete is also granted|
|Delete| Permission to delete items|
|      | **Note** This does not imply that the add right or modify is also granted|
|Validate| Permission to validate items on the event|
|Set Groups| Permissions to change the groups/permissions of groups|

####2.2.2 Adding/Edit of an Event

#####2.2.2.1 Adding/Edit an Event

The event has the following properties:

|Field | description|
|------|------------|
|UUID                                           | Generated UUID to uniquely identify an event|
|Title*                                         | Title (or Name) of the event|
|                                               | **Note**: Is mandatory|
|Description                                    | Short description of the event|
|                                               | **Note**: This description will aways shown| 
|Published                                      | If set the event is visible to the users who access is granted to, if| 
|                                               | not the event is only visible by the users of the same group as the creator.|
|                                               | **Note1**: Unpublished events are marked in a reddish color|
|                                               | **Note2**: If an event was published and changes are made i.e adding an| 
|                                               |        attribute the event will unpublish|
|Status[Confirmed,Deleted,Draft,Expired]        | |
|Analysis[Completed,Opened,None,Unknown,Stalled]||
|Risk[High,Low,Medium,None,Undefined]           ||
|TLP[Red,Amber,Green,White]                     ||
|First seen                                     | When the event was first seen. Default "now()"|
|Last seen                                      | When the event was last seen. Default "now()"|
|                                               | **Note**: This value is updated by "now() as soon there are attributes/objects| 
|                                               |       added to the event|

**Note**: If ce1sus is configured to send mails, each time an events gets published the users allowed to see the events gets 
a notification mail of the changes

**Note**: The add event interface offers also the possibility to add the event via files. The currently supported formats are:
* STIX xmls
* MISP 2.3 xmls
* OpenIOCs ioc files
 

####2.2.2.2 Adding/Edit Observables/Objects

To add an object the user must just select the object he wants and if this object should be shared. If the object is not
shared the attribute will automatically be not shared.

**Note**: Not shared means that they are only visible by the owner of the event and the users of the creator group.

The object will be displayed as a container, where the object can be modified with the following options:

|Field|Description|
|-----|-----------|
|Add Attribute     (Plus sign)  | See section 2.2.1.2|
|Add child object  (Arrow down) | Add a new object as child|
|Modify object     (Lines)      | Offers the possibility to change the child parent relations|
|Modify properties (Pencil)     | Change the value for shearing|
|                               | Note: If an object is unshared all its attributes and children will also be unshared|
|View details      (Eye)        | Shows the details of the object and its creation date|
|Delete            (Cross)      | Removes an object|
|                               | **Note**: If an object has children it is not possible to delete that object until its| 
|                               |       children are removed|

**Notes**: 
       * If the object header has a lock icon the object is not shared
       * If the object header is yellow the object has been proposed, for more informations on proposals see section 2.2.1.3

####2.2.2.3 Adding/Edit Attributes


Attributes can only be added if an object exits. The attribtues can change for every object as they were configured in 
the administration section (see section 2.1.4 & 2.1.5). 

To add an attribute one has first to select its type, depending on which type is selected the input fields may vary. 
The configured handler (see section 2.1.5.1) specifies how the input fields look like and how the entered values are 
handled.

These are the possible properties of an attribute:

|Field|Description|
|-----|-----------|
|Type          | See attribute definitions in section 2.1.4|
|Value         | The attribute value|
|              | Note: These values are checked against the regex specified in their definition.|
|Shared        | Defines if the attribute is shared. The default value depends in the attribute definition.|
|              | Note: Not shared means that they are only visible by privileged users and the users of the creator group.|
|Is an IOC     | Set the value if it is an IOC|

**Notes**: 
* If the attribute identifier is marked red the event is unpulbished.
* If the attribute identifier is marked yellow the event got some proposals, for more informations on proposals see section 2.2.1.3
* Depending on the handler used the properties may vary.

####2.2.2.4 Proposal of objects/Attributes

Every user can propose attributes and objects to an event which is viewable to him. The proposals are made as if the proposing user is the owner of the event he wants to provide additional informations. The difference is that these proposed attributes will be marked (yellow color) to denote them as proposals. These proposals will only be visible by the proposing user and the event owner. As long as the proposed attribute had not been acknowledged by the owner, they can be deleted at any time, by the proposing user.

**Note**: These attributes will not be visible to other users, unless the owner acknowledge them and then they will be part of the event and shown normally to all the users having access to the corresponding event.

Remark: A future release will provide this feature also via REST.

####2.2.2.5 Remarks



###2.2.2 Search


The search supports currently only the search on attributes and reports. The search results work the same way as the Recent events described
in section 2.2.3.

WORK IN PROGRESS

###2.2.3 Events

The recent events list the last 200 entered events, by clicking, either on the identifier (number) or the eye icon in the
options column, one enters view of the event. 

**Notes:** 
* If the event identifier is marked red the event is unpulbished.
* If the event identifier is marked yellow the event got some proposals, for more informations on proposals see section 2.2.1.3

#3. REST API

For viewing the REST API Documentation please access on the server with the frontend the "/swagger" path (i.e. http://localhost:8080/swagger).

#4. Maintenance tools

The maintenance tool is a command line application, wich is deployed on the server. It offers the following functionalities:

- Rebuild all relations according to the definitions
    Note: This finctionality is used to recreate and remove relations in case there were changes made to the definitions.
          The relations which are existing but the definition is not relationable anyloger will also be removed
- Rebuild relations according to the definitions for a specific event
- Verify the checksums of all definitions and change them to the correct value if needed
- Clear all the relations

Use the following command for the syntax

``` shell
python maintenance.py -h
```

#5. Developing Handlers

WORK IN PROGRESS

#4. Known Issues

None
