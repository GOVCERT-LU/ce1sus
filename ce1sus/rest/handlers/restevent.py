# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.rest.restbase import RestControllerBase
from ce1sus.brokers.event.eventbroker import EventBroker
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.brokers.staticbroker import TLPLevel, Risk, Analysis, Status
from ce1sus.api.restclasses import RestEvent

class RestEventController(RestControllerBase):

  PARAMETER_MAPPER = {'metadata': 'viewMetaData'}

  def __init__(self):
    RestControllerBase.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)

  def viewMetaData(self, uuid, apiKey, **options):
    try:
      event = self.eventBroker.getByUUID(uuid)
      self.checkIfViewable(event, self.getUser(apiKey), False)
      obj = self._objectToJSON(event,
                               self.isEventOwner(event, self.getUserByAPIKey(apiKey)),
                               False,
                               False)
      return self._returnMessage(obj)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def view(self, uuid, apiKey, **options):
    try:
      event = self.eventBroker.getByUUID(uuid)
      self.checkIfViewable(event, self.getUser(apiKey), False)
      withDefinition = options.get('fulldefinitions', False)
      obj = self._objectToJSON(event,
                               self.isEventOwner(event, self.getUserByAPIKey(apiKey)),
                               True,
                               withDefinition)

      return self._returnMessage(obj)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def delete(self, uuid, apiKey, **options):
    try:
      event = self.eventBroker.getByUUID(uuid)
      self.checkIfViewable(event, self.getUser(apiKey), False)
      return self.raiseError('NotImplemented',
                             'The delete method has not been implemented')

    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def update(self, uuid, apiKey, **options):
    if not uuid:
      try:
        restEvent = self.getPostObject()
        # map restEvent on event
        user = self.getUser(apiKey)
        event = self.eventBroker.buildEvent(
                       None,
                       'insert',
                       Status.getByName(restEvent.status),
                       TLPLevel.getByName(restEvent.tlp),
                       restEvent.description,
                       restEvent.title,
                       restEvent.published,
                       restEvent.first_seen,
                       restEvent.last_seen,
                       Risk.getByName(restEvent.risk),
                       Analysis.getByName(restEvent.analysis),
                       user,
                       restEvent.uuid)
        event.bitValue.isRestInsert = True
        if restEvent.share == 1:
          event.bitValue.isSharable = True
        else:
          event.bitValue.isSharable = False
        # flush to DB
        self.eventBroker.insert(event, commit=False)

        for obj in restEvent.objects:
          # create object
          dbObject = self.__convertRestObject(obj, event, event, commit=False)
          event.objects.append(dbObject)

        self.eventBroker.doCommit(True)

        withDefinition = options.get('fulldefinitions', False)
        # obj = self._objectToJSON(event, True, True, withDefinition)
        restEvent = RestEvent()
        restEvent.uuid = event.uuid
        return self._returnMessage(dict(restEvent.toDict(full=True,
                             withDefinition=withDefinition).items()
                 ))

      except BrokerException as e:
        return self.raiseError('BrokerException', e)

    else:
      return self.raiseError('Exception', 'Not Implemented')

  def __convertRestObject(self, obj, parent, event, commit=False):
    dbObject = self._convertToObject(obj, parent, event, commit=commit)
    # generate Attributes
    dbObject.attributes = self._convertToAttribues(obj.attributes,
                                                          dbObject, commit)
    for child in obj.children:
      childDBObj = self.__convertRestObject(child, dbObject, event, commit)
      dbObject.children.append(childDBObj)
    return dbObject

  def getFunctionName(self, parameter, action):
    if action == 'GET':
      return RestEventController.PARAMETER_MAPPER.get(parameter, None)
    return None
