

app.controller("eventController", function($scope, Restangular,messages,
    $log, $routeSegment,eventmenus, $location, statuses, risks, tlps, analyses) {
  $scope.statuses=statuses;
  $scope.risks=risks;
  $scope.tlps=tlps;
  $scope.anlysises=analyses;
  $scope.eventMenus = eventmenus;
  $scope.openedEvents = [];
  $scope.valiation = false;

  $scope.dropdownexport = [
                     {
                       "text": "STIX xml",
                       "click": "showStructured()",
                       "html": true
                     },
                     {
                       "text": "MISP xml",
                       "click": "showFlat()",
                       "html": true
                     },
                     {
                       "text": "JSON",
                       "click": "showFlat()",
                       "html": true
                     },
                   ];
  
  $scope.pushItem = function(event, guiOpen) {
    found = false;
    angular.forEach($scope.openedEvents, function(value, index) {
      if (value.identifier == event.identifier){
        found = true;
      }
    }, $log);
    var url = '/events/event/'+event.identifier;
    if (!found) {
      $scope.openedEvents.push({
        icon: '',
        title: event.stix_header.title,
        section: 'main.layout.events.event',
        reload: false,
        close: true,
        href: url,
        identifier: event.identifier
      });
      if (guiOpen){
        $location.path(url);
      }
    } else {
      $location.path(url);
    }
  };

  $scope.removeItem = function(element_id) {
    gotoRoot = false;
    angular.forEach($scope.openedEvents, function(value, index) {
      if (value.identifier) {
        if (value.identifier == element_id) {
          $scope.openedEvents.splice(index, 1);
          gotoRoot = true;
        }
      }
    }, $log);
    if (gotoRoot){
      $location.path("/events/all");
    }
  };
  
  $scope.reloadPage = function() {
    $routeSegment.chain[3].reload();
  };
  $scope.$routeSegment = $routeSegment;
});

app.controller("viewEventController", function($scope, Restangular, messages,
    $log, $routeSegment, $location,$event, groups) {
  $scope.event = $event;
  $scope.pushItem($scope.event);
  $scope.groups = groups;
  $scope.reloadPage = function(){
    var index = $routeSegment.chain.length;
    
    $routeSegment.chain[index-1].reload();
  };
  
  $scope.getRolesName = function(roles){
    var rolesStr = '[';
    angular.forEach(roles, function(role) {
      rolesStr = rolesStr + role.name + ', '; 
    });
    
    
    return rolesStr + ']';
  };
});

app.controller("eventObservableController", function($scope, Restangular, messages,
    $log, $routeSegment, $location,observables, $anchorScroll, Pagination) {
  $scope.permissions=$scope.event.userpermissions;
  $scope.getAttributes=function(){
    var attributes = [];
    function generateItems(object, observable, composed){
      if (object.attributes.length > 0) {
        angular.forEach(object.attributes, function(attribute, index) {
          var item = {};
          item.value = attribute.value;
          item.definition = attribute.definition;
          item.ioc = attribute.ioc;
          item.shared = attribute.shared;
          item.object = object.definition.name;
          item.observable = observable.title;
          if (attribute){
            item.properties = attribute.properties;
          } else {
            if (object) {
              item.properties = object.properties;
            } else {
              item.properties = observable.properties;
            }
          }
          
          if (composed) {
            item.composed = composed.title;
            item.composedoperator = composed.operator;
            item.composedlength = composed.observables.length;
          }
          attributes.push(item);
        }, $log);
      } else {
        var item = {};
        item.observable = observable.title;
        item.object = object.definition.name;
        item.value = 'No attributes were definied';
        attributes.push(item);
      }
      // continue with the related objects
      angular.forEach(object.related_objects, function(relObject) {
        generateItems(relObject.object, observable);
      }, $log);
    }
    
    function processObservavle(observable, composed){
      if (observable.observable_composition){
        angular.forEach(observable.observable_composition.observables, function(compobservable, index) {
          processObservavle(compobservable, observable.observable_composition);
        },$log);
      } else {
        if (observable.object) {
          generateItems(observable.object, observable, composed);
        } else {
          var item = {};
          item.observable = observable.title;
          item.object = 'No objects were definied';
          attributes.push(item);
        }
      }
    }
    
    angular.forEach($scope.observables, function(observable) {
      processObservavle(observable, null);
    }, $log);
    return attributes;
  };
  
  $scope.observables = observables;
  $scope.flat=false;
  $scope.showFlat=function(){
    $scope.flat=true;
    $scope.flatAttributes = $scope.getAttributes();
    $scope.pagination = Pagination.getNew(10,'flatAttributes');
    $scope.pagination.numPages = Math.ceil($scope.flatAttributes.length/$scope.pagination.perPage);
    $scope.pagination.setPages();
  };
  $scope.showStructured=function(){
    $scope.flat=false;
  };

  $scope.writeTD=function(attribute, pagination){
    var currentPosition = $scope.flatAttributes.indexOf(attribute);
    if (currentPosition> 0){
      if ($scope.flatAttributes[currentPosition-1].composedlength == attribute.composedlength){
        if (currentPosition == pagination.page * pagination.perPage){
          return true;
        }
        return false;
      }
      return true;
    } 
    return true;
  };
  
  $scope.getFlatTitle = function(attributeflat){
    if (attributeflat.composedoperator){
      if (attributeflat.composed){
        return attributeflat.composed;
      } else {
        return "Composed";
      }
    } else {
      if (attributeflat.observable){
        return attributeflat.observable;
      } else {
        return "Observable";
      }
    }
    return "Unknown";
  };

  $scope.getRowSpan = function(attribute, pagination){
    var rowspan = 0;
    if (attribute.composedlength) {
      var currentLength = attribute.composedlength;
      var currentPosition = $scope.flatAttributes.indexOf(attribute);
      var startindex = 0;
      for (var i = currentPosition; i >= 0; i--){
        if ($scope.flatAttributes[i].composedlength){
          if (currentLength != $scope.flatAttributes[i].composedlength){
            startindex = i;
            break;
          }
        }
      }
      var endPosition = (startindex + currentLength);
      var remaining = endPosition - (pagination.page * pagination.perPage);
      //TODO review I wonder why this works!? td is set incorrectly but stops where expected
      if (remaining > 0) {
        rowspan = remaining;
        if (startindex > 0){
          rowspan++;
        }
      } else {
        rowspan = pagination.perPage+remaining;
      }
      

    } else {
      rowspan = 1;
    }
      
    return rowspan;
  };
  $scope.dropdown = [
                       {
                         "text": "Structured",
                         "click": "showStructured()",
                         "html": true
                       },
                       {
                         "text": "Flat",
                         "click": "showFlat()",
                         "html": true
                       },
                     ];


});

app.controller("eventIndicatorController", function($scope, Restangular, messages,
    $log, $routeSegment, $location,indicators, $anchorScroll, Pagination) {
  $scope.permissions=$scope.event.userpermissions;
  
  $scope.getAttributes=function(){
    var attributes = [];
    function generateItems(object, observable, composed){
      if (object.attributes.length > 0) {
        angular.forEach(object.attributes, function(attribute, index) {
          var item = {};
          item.value = attribute.value;
          item.definition = attribute.definition;
          item.ioc = attribute.ioc;
          item.shared = attribute.shared;
          item.object = object.definition.name;
          item.observable = observable.title;
          if (attribute){
            item.properties = attribute.properties;
          } else {
            if (object) {
              item.properties = object.properties;
            } else {
              item.properties = observable.properties;
            }
          }
          
          if (composed) {
            item.composed = composed.title;
            item.composedoperator = composed.operator;
            item.composedlength = composed.observables.length;
          }
          attributes.push(item);
        }, $log);
      } else {
        var item = {};
        item.observable = observable.title;
        item.object = object.definition.name;
        item.value = 'No attributes were definied';
        attributes.push(item);
      }
      // continue with the related objects
      angular.forEach(object.related_objects, function(relObject) {
        generateItems(relObject.object, observable);
      }, $log);
    }
    
    function processObservavle(observable, composed){
      if (observable.observable_composition){
        angular.forEach(observable.observable_composition.observables, function(compobservable, index) {
          processObservavle(compobservable, observable.observable_composition);
        },$log);
      } else {
        if (observable.object) {
          generateItems(observable.object, observable, composed);
        } else {
          var item = {};
          item.observable = observable.title;
          item.object = 'No objects were definied';
          attributes.push(item);
        }
      }
    }
    
    angular.forEach($scope.indicators, function(indicator) {
      angular.forEach(indicator.observables, function(observable) {
        processObservavle(observable, null);
      }, $log);
    }, $log);
    return attributes;
  };
  
  $scope.indicators = indicators;
  $scope.flat=false;
  $scope.showFlat=function(){
    $scope.flat=true;
    $scope.flatAttributes = $scope.getAttributes();
    $scope.pagination = Pagination.getNew(10,'flatAttributes');
    $scope.pagination.numPages = Math.ceil($scope.flatAttributes.length/$scope.pagination.perPage);
    $scope.pagination.setPages();
  };
  $scope.showStructured=function(){
    $scope.flat=false;
  };

  $scope.writeTD=function(attribute, pagination){
    var currentPosition = $scope.flatAttributes.indexOf(attribute);
    if (currentPosition> 0){
      if ($scope.flatAttributes[currentPosition-1].composedlength == attribute.composedlength){
        if (currentPosition == pagination.page * pagination.perPage){
          return true;
        }
        return false;
      }
      return true;
    } 
    return true;
  };
  
  $scope.getFlatTitle = function(attributeflat){
    if (attributeflat.composedoperator){
      if (attributeflat.composed){
        return attributeflat.composed;
      } else {
        return "Composed";
      }
    } else {
      if (attributeflat.observable){
        return attributeflat.observable;
      } else {
        return "Indicator";
      }
    }
    return "Unknown";
  };

  $scope.getRowSpan = function(attribute, pagination){
    var rowspan = 0;
    if (attribute.composedlength) {
      var currentLength = attribute.composedlength;
      var currentPosition = $scope.flatAttributes.indexOf(attribute);
      var startindex = 0;
      for (var i = currentPosition; i >= 0; i--){
        if ($scope.flatAttributes[i].composedlength){
          if (currentLength != $scope.flatAttributes[i].composedlength){
            startindex = i;
            break;
          }
        }
      }
      var endPosition = (startindex + currentLength);
      var remaining = endPosition - (pagination.page * pagination.perPage);
      //TODO review I wonder why this works!? td is set incorrectly but stops where expected
      if (remaining > 0) {
        rowspan = remaining;
        if (startindex > 0){
          rowspan++;
        }
      } else {
        rowspan = pagination.perPage+remaining;
      }
      

    } else {
      rowspan = 1;
    }
      
    return rowspan;
  };
  $scope.dropdown = [
                       {
                         "text": "Structured",
                         "click": "showStructured()",
                         "html": true
                       },
                       {
                         "text": "Flat",
                         "click": "showFlat()",
                         "html": true
                       },
                     ];


});

app.controller("addEventController", function($scope, Restangular, messages,
    $log, $routeSegment, $location) {

  $scope.dropdownFile = [
                     {
                       "text": "Add STIX XML file",
                       "click": "addStixXML()",
                       "html": true
                     },
                     {
                       "text": "Add MISP XML file",
                       "click": "addMISPXML()",
                       "html": true
                     },
                     {
                       "text": "Add OpenIOC file",
                       "click": "addOpenIOCXML()",
                       "html": true
                     },
                     {
                       "text": "Add Manual",
                       "click": "addManual()",
                       "html": true
                     },
                   ];
  
  $scope.addMISPFile=false;
  $scope.addSTIXFile=false;
  $scope.addOpenIOCFile=false;
  $scope.addManual=false;
  
  $scope.addManual=function(){
    $scope.addMISPFile=false;
    $scope.addSTIXFile=false;
    $scope.addOpenIOCFile=false;
    $scope.addManual=true;
  };
  
  $scope.addMISPXML=function(){
    $scope.addMISPFile=true;
    $scope.addSTIXFile=false;
    $scope.addOpenIOCFile=false;
    $scope.addManual=false;
  };
  
  $scope.addStixXML=function(){
    $scope.addSTIXFile=true;
    $scope.addMISPFile=false;
    $scope.addOpenIOCFile=false;
    $scope.addManual=false;
  };
  
  $scope.addOpenIOCXML=function(){
    $scope.addSTIXFile=false;
    $scope.addMISPFile=false;
    $scope.addOpenIOCFile=true;
    $scope.addManual=false;
  };
  
  var original_event = {};
  $scope.event={};
  
  $scope.eventChanged = function ()
  {
    return !angular.equals($scope.event, original_event);
  };
  
  $scope.resetEvent = function ()
  {
    //Could also be done differently, but for this case the validation errors will also be resetted
    $routeSegment.chain[3].reload();
  };
  
  $scope.submitEvent = function(){
    Restangular.all("event").post($scope.event).then(function (data) {
      
      if (data) {
        $location.path("/events/event/"+ data.identifier);
      } else {
        $location.path("/events/all");
      }
      messages.setMessage({'type':'success','message':'Event sucessfully added'});
      
    }, function (response) {
      $scope.event = angular.copy(original_event);
      handleError(response, messages);
    });
  };
});

app.controller("editEventController", function($scope, Restangular, messages,
    $log, $routeSegment, $location) {

  var original_event = angular.copy($scope.event);

  $scope.eventChanged = function ()
  {
    return !angular.equals($scope.event, original_event);
  };
  
  $scope.resetEvent = function ()
  {
    $scope.event = angular.copy(original_event);
  };
  
  $scope.submitEvent = function(){
    $scope.event.put().then(function (data) {
      if (data) {
        $scope.event = data;
        //update username in case
        angular.forEach($scope.openedEvents, function(entry) {
          if (entry.identifier === data.identifier){
            entry.title = data.title;
          }
        }, $log);
        
      }
      
      messages.setMessage({'type':'success','message':'Event sucessfully edited'});
      
    }, function (response) {
      $scope.event = angular.copy(original_event);
      handleError(response, messages);
    });
    $scope.$hide();
  };

  $scope.closeModal = function(){
    $scope.event = angular.copy(original_event);
    $scope.$hide();
  };
});
app.controller("eventOverviewController", function($scope, Restangular, messages,
    $log, $routeSegment, $location, useradmin, $modal, relations, Pagination) {
  if (useradmin){
    $scope.isAdmin = true;
  } else {
    $scope.isAdmin = false;
  }
  
  $scope.relations = relations;
  $scope.pagination = Pagination.getNew(5,'relations');
  $scope.pagination.numPages = Math.ceil($scope.relations.length/$scope.pagination.perPage);
  $scope.pagination.setPages();
  $scope.validateEvent = function(){
    //validates an event and publishes it as only users who can enter the validate section (lesser admin) can validate
    $scope.event.one('validate').put().then(function (data) {
      if (data) {
        messages.setMessage({'type':'success','message':'Event sucessfully validated'});
        $scope.removeItem($scope.event.identifier);
      }
    }, function (response) {
      handleError(response, messages);
    });
  };
  
  
  $scope.removeEvent = function(){
    
    if (confirm('Are you sure you want to delete this event?')) { 
      $scope.event.remove().then(function (data) {
        if (data) {
          //remove the selected user and then go to the first one in case it exists
          var index = 0;
          angular.forEach($scope.openedEvents, function(entry) {
            if (entry.identifier === $scope.event.identifier){
              $scope.openedEvents.splice(index, 1);
              $location.path("/events/all");
            }
            index++;
          }, $log);
          messages.setMessage({'type':'success','message':'Event sucessfully removed'});
        }
      }, function (response) {
        handleError(response, messages);
      });
    }
  };
  
  $scope.publishEvent = function(){

    Restangular.one("event", $routeSegment.$routeParams.id).post('publish',$scope.event).then(function (data) {
      if (data) {
        messages.setMessage({'type':'success','message':'Event sucessfully published'});
        $scope.event.published = true;
        $scope.event.properties.shared = true;
      } else {
        messages.setMessage({'type':'danger','message':'An unexpected error occured'});
      }
    }, function (response) {
      handleError(response, messages);
    });
  };
  
  $scope.removeComment = function(comment){
    if (confirm('Are you sure you want to delete this comment?')) {
      //restangularize Element
      restangularComment = Restangular.restangularizeElement($scope.event, comment, 'comment');
      restangularComment.remove().then(function (data) {
        if (data) {
          //remove the selected user and then go to the first one in case it exists
          var index = $scope.event.comments.indexOf(comment);
          $scope.event.comments.splice(index, 1);
          messages.setMessage({'type':'success','message':'Comment sucessfully removed'});
        }
      }, function (response) {
        handleError(response, messages);
      });
    }
  };
  
  $scope.showCommentDetails = function(comment){
    $scope.commentDetails = comment;
    $modal({scope: $scope, template: 'pages/events/event/modals/commentdetails.html', show: true});
  };
  
  $scope.editCommentDetails = function(comment){
    $scope.commentDetails = comment;
    $modal({scope: $scope, template: 'pages/events/event/modals/editcomment.html', show: true});
  };
  
});

app.controller("changeOwnerController", function($scope, Restangular, messages,
    $log, $routeSegment, $http) {
  var original_group = angular.copy($scope.event.creator_group.identifier);
  $scope.ownergroup = $scope.event.creator_group.identifier;
  
  $scope.groupChanged = function (){
    return !angular.equals($scope.ownergroup, original_group);
  };
  
  $scope.resetGroup = function (){
    $scope.ownergroup = angular.copy(original_group);
  };
  
  $scope.submitGroup = function(){
    var group = null;
    angular.forEach($scope.groups, function(entry) {
      if (entry.identifier === $scope.ownergroup){
        group = entry;
      }
    }, $log);
    
    $http.put("/REST/0.3.0/event/"+$scope.event.identifier+'/changegroup', {'identifier': $scope.ownergroup}).success(function(data, status, headers, config) {
      if (data == 'OK') {
        $scope.event.creator_group = group;
        messages.setMessage({'type':'success','message':'Event owner sucessfully changed'});
      } else {
        messages.setMessage({'type':'danger','message':'Could not change group'});
      }
    }).error(function(data, status, headers, config) {
      var message = extractBodyFromHTML(data);
      
      if (status === 500) {
        message = "Internal Error occured, please contact your system administrator";
      }
      if (status === 0) {
        message = "Server is probaly gone offline";
      }
      error = new Ce1susException('Message');
      error.code = status;
      error.type = "danger";
      error.message = 'Error occured';
      error.description = message;
      message = {"type":"danger","message":status+" - "+getTextOutOfErrorMessage(error)};
      messages.setMessage(message);
    });

    $scope.$hide();

  };

  $scope.closeModal = function(){
    $scope.$hide();
  };
});

app.controller("addEventCommentController", function($scope, Restangular, messages,
    $log, $routeSegment) {
  var original_comment = {};
  $scope.comment = {};
  
  $scope.commentChanged = function (){
    return !angular.equals($scope.comment, original_comment);
  };
  
  $scope.resetComment = function (){
    $scope.comment = angular.copy(original_comment);
  };
  
  $scope.submitComment = function(){
    Restangular.one("event", $routeSegment.$routeParams.id).post('comment',$scope.comment).then(function (data) {
      if (data) {
        messages.setMessage({'type':'success','message':'Comment sucessfully added'});
        $scope.event.comments.push(data);
      } else {
        messages.setMessage({'type':'danger','message':'An unexpected error occured'});
      }
    }, function (response) {
      $scope.comment = angular.copy(original_comment);
      handleError(response, messages);
    });
    $scope.$hide();
  };

  $scope.closeModal = function(){
    $scope.comment = angular.copy(original_comment);
    $scope.$hide();
  };
});

app.controller("editEventCommentController", function($scope, Restangular, messages,
    $log, $routeSegment) {
  var original_comment = angular.copy($scope.commentDetails);
  
  $scope.commentChanged = function (){
    return !angular.equals($scope.commentDetails, original_comment);
  };
  
  $scope.resetComment = function (){
    $scope.commentDetails = angular.copy(original_comment);
  };
  
  $scope.submitComment = function(){
    restangularComment = Restangular.restangularizeElement($scope.event, $scope.commentDetails, 'comment');
    restangularComment.put().then(function (data) {
      if (data) {
        messages.setMessage({'type':'success','message':'Comment sucessfully editied'});
      } else {
        messages.setMessage({'type':'danger','message':'An unexpected error occured'});
      }
    }, function (response) {
      $scope.commentDetails = angular.copy(original_comment);
      handleError(response, messages);
    });
    $scope.$hide();
  };

  $scope.closeModal = function(){
    $scope.commentDetails = angular.copy(original_comment);
    $scope.$hide();
  };
});

app.controller("eventGroupController", function($scope, Restangular, messages,
    $log, $routeSegment) {
  $scope.multiple = false;
  $scope.permissions = {};
  
  $scope.remaining = angular.copy($scope.groups);
  if (!$scope.event.groups){
    $scope.associated =[];
  } else {
     $scope.associated = angular.copy($scope.event.groups);
  }
  $scope.setRemaining = function() {
    var index = 0;
    var items_to_remove = [];
    angular.forEach($scope.remaining, function(item) {
      // remove selected from the group
      if (item.identifier == $scope.event.creator_group.identifier) {
        items_to_remove.push(index);
      } else {
        if ($scope.associated.length > 0) {
          angular.forEach($scope.associated, function(associatedEntry) {
            var id1 = associatedEntry.group.identifier;
            var id2 = item.identifier;
            if (id1.toLowerCase() == id2.toLowerCase()){
              items_to_remove.push(index);
              
            }
            
          }, $log);
        }
      }
      index++;
    }, $log);
    //sort array from big to log
    items_to_remove = items_to_remove.reverse();
    angular.forEach(items_to_remove, function(index){
      $scope.remaining.splice(index, 1);
    });
  };
  $scope.setRemaining();
  var original_values = {};
  $scope.setPropeties = function(){
    $scope.showBtn = true;
    $scope.selected_remaining = [];
    if ($scope.selected_accociated.length == 1){
      //Get Permissions from selected
      angular.forEach($scope.associated, function(associatedEntry) {
        $scope.multiple = false;
        if (associatedEntry.group.identifier == $scope.selected_accociated[0]) {
          $scope.permissions = angular.copy(associatedEntry.permissions);
          original_values = angular.copy(associatedEntry.permissions);
        }
      }, $log);
      
    } else {
      $scope.multiple = true;
    }
  };
  
  $scope.setRemPropeties = function(){
    $scope.selected_accociated = [];
    $scope.showBtn = false;
    if ($scope.selected_remaining.length == 1){
      //Get Permissions from selected
      angular.forEach($scope.remaining, function(entry) {
        $scope.multiple = false;
        if (entry.identifier == $scope.selected_remaining[0]) {
          $scope.permissions = angular.copy(entry.default_event_permissions);
          original_values = angular.copy(entry.default_event_permissions);
        }
      }, $log);
      
    } else {
      $scope.multiple = true;
    }
  };
  
  $scope.setDefaults = function(){
    var uuid = null;
    if ($scope.selected_accociated.length == 1) {
      uuid = $scope.selected_accociated[0];
    } else {
      if ($scope.selected_remaining.length == 1) {
        uuid = $scope.selected_remaining[0];
      }
    }
    if (uuid) {
      angular.forEach($scope.groups, function(item) {
        if (item.identifier == uuid) {
          $scope.permissions = angular.copy(item.default_event_permissions);
        }
      }, $log);
    } else {
      $scope.permissions = {};
    }
  };
  
  $scope.resetPermissions = function() {
    if ($scope.selected_accociated.length == 1) {
      $scope.permissions = angular.copy(original_values);
    }
  };
  
  $scope.permissionsChanged = function ()
  {
    return !angular.equals($scope.permissions, original_values);
  };
  
  $scope.submitPermissionChanges = function(){
    var eventPermission = null;
    angular.forEach($scope.associated, function(associatedEntry) {
      $scope.multiple = false;
      if (associatedEntry.group.identifier == $scope.selected_accociated[0]) {
        eventPermission = associatedEntry;
      }
    }, $log);
    eventPermission.permissions = $scope.permissions;
    restangularPermission = Restangular.restangularizeElement($scope.event, eventPermission, 'group');
    restangularPermission.put().then(function (data) {
      if (data){
        messages.setMessage({'type':'success','message':'Group sucessfully edited'});
        //update group in browser
        angular.forEach($scope.associated, function(associatedEntry) {
          $scope.multiple = false;
          if (associatedEntry.group.identifier == $scope.selected_accociated[0]) {
            associatedEntry = data;
          }
        }, $log);
      } else {
        messages.setMessage({'type':'danger','message':'An unexpected error occured'});
      }
      
    }, function (response) {
      $scope.comment = angular.copy(original_comment);
      handleError(response, messages);
    });
  };
  
  $scope.groupAdd = function(){
    var original_associated = angular.copy($scope.associated);
    angular.forEach($scope.selected_remaining, function(addedItemID) {
      // remove selected from the group
      var index = 0;
      angular.forEach($scope.remaining, function(remEntry) {
        if (addedItemID == remEntry.identifier){
          $scope.remaining.splice(index, 1);
        }
        index++;
      }, $log);
      //get the original details
      angular.forEach($scope.groups, function(itemEntry) {
        if (itemEntry.identifier == addedItemID){
          //check if only one is selected then append the set permissions else take the default ones
          var permissions = itemEntry.default_event_permissions;
          if ($scope.selected_remaining.length == 1) {
            permissions = $scope.permissions;
          }
          
          Restangular.one('event', $scope.event.identifier).all('group').post({'group': {'identifier':itemEntry.identifier,'name':itemEntry.name}, 'permissions': permissions}).then(function (item) {
            if (item) {
              messages.setMessage({'type':'success','message':'Item sucessfully associated'});
              $scope.associated.push(item);
              
            } else {
              
              messages.setMessage({'type':'danger','message':'Unkown error occured'});
            }

          }, function (response) {
            $scope.associated = original_associated;
            handleError(response, messages);
          });
        }
      }, $log);
      
    }, $log);
    $scope.permissions = {};
    $scope.selected_accociated = [];
    $scope.selected_remaining = [];
  };
  $scope.groupRemove = function(){
    var original_associated = angular.copy($scope.associated);
    angular.forEach($scope.selected_accociated, function(addedItemID) {
      // remove selected from the group
      var index = 0;
      angular.forEach($scope.associated, function(item) {
        if (addedItemID == item.group.identifier){
          $scope.associated.splice(index, 1);
          restangularPermission = Restangular.restangularizeElement($scope.event, item, 'group');
          restangularPermission.remove().then(function (item) {
            if (item) {
              messages.setMessage({'type':'success','message':'Item sucessfully removed'});
            } else {
              
              messages.setMessage({'type':'danger','message':'Unkown error occured'});
            }

          }, function (response) {
            $scope.remaining = angular.copy($scope.groups);
            $scope.associated = original_associated;
            $scope.setRemaining();
            handleError(response, messages);
          });
          
        }
      index++;
      }, $log);
      
    }, $log);
    $scope.remaining = angular.copy($scope.groups);
    $scope.setRemaining();
    $scope.permissions = {};
    $scope.selected_accociated = [];
    $scope.selected_remaining = [];
  };
});

app.controller("eventRelationsController", function($scope, Restangular, messages,
    $log, $routeSegment, relations, $filter, ngTableParams) {
  var relations_data = relations;
  $scope.tableParams = new ngTableParams({
    page: 1,            // show first page
    count: 10,          // count per page
  }, {
      total: relations_data.length, // length of data
      getData: function($defer, params) {
          // use build-in angular filter
          var orderedData = params.filter() ? $filter('filter')(relations_data, params.filter()) : relations_data;
          orderedData = params.sorting() ? $filter('orderBy')(orderedData, params.orderBy()) : orderedData;
          $scope.relations = orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count());
          params.total(orderedData.length); // set total for recalc pagination
          $defer.resolve($scope.relations);
      }
  }); 
});

app.controller("uploadController", function($scope, $timeout, $log, Restangular,$location, messages) {
  $scope.file = {};
  function converToRestFile(file) {
    if (window.File && window.FileReader && window.FileList && window.Blob) {
      // Great success! All the File APIs are supported.
      if (file) {
          var data;
          $timeout(function() {
            var fileReader = new FileReader();
            fileReader.readAsDataURL(file);
            fileReader.onload = function(e) {
              $timeout(function() {
                //I am only interested in the base 64 encodings
                file.data =  e.target.result.split(",")[1];
              });
            };
          });
      } else {
        alert('Error No file provided');
      }
    } else {
      alert('The File APIs are not fully supported in this browser.');
    }
  }

  
  $scope.setFileValue = function(files){
    var file = files[0];
    
    converToRestFile(file);
    $scope.file = {};
    $scope.file.data = file;
    $scope.file.name = file.name;
  };
  
  $scope.addMISP =function(){
    Restangular.oneUrl('file','/MISP/0.1').post('upload_xml',$scope.file, {'complete':true, 'infated':true}).then(function (data) {
      if (data) {
        $location.path("/events/event/"+ data.identifier);
      } else {
        $location.path("/events/all");
      }
      messages.setMessage({'type':'success','message':'Event sucessfully added'});
    }, function (response) {
      handleError(response, messages);
    });
  };
  $scope.addSTIX =function(){
    Restangular.oneUrl('file','/STIX/0.1').post('upload_xml',$scope.file, {'complete':true, 'infated':true}).then(function (data) {
      if (data) {
        $location.path("/events/event/"+ data.identifier);
      } else {
        $location.path("/events/all");
      }
      messages.setMessage({'type':'success','message':'Event sucessfully added'});
    }, function (response) {
      handleError(response, messages);
    });
  };
  $scope.addOpenIOC =function(){
    Restangular.oneUrl('file','/OpenIOC/0.1').post('upload_xml',$scope.file, {'complete':true, 'infated':true}).then(function (data) {
      if (data) {
        $location.path("/events/event/"+ data.identifier);
      } else {
        $location.path("/events/all");
      }
      messages.setMessage({'type':'success','message':'Event sucessfully added'});
    }, function (response) {
      handleError(response, messages);
    });
  };
  
});
