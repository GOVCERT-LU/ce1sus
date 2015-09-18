

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
    var found = false;
    for (var i = 0; i < $scope.openedEvents.length; i++) {
      if ($scope.openedEvents[i].identifier == event.identifier){
        found = true;
        break;
      }
    }
    
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
    for (var i = 0; i < $scope.openedEvents.length; i++) {
      if ($scope.openedEvents[i].identifier) {
        if ($scope.openedEvents[i].identifier == element_id) {
          $scope.openedEvents.splice(i, 1);
          $location.path("/events/all");
          break;
        }
      }
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
    for (var i = 0; i < roles.length; i++) {
      rolesStr = rolesStr + roles[i].name + ', '; 
    }
    return rolesStr + ']';
  };
});

app.controller("eventObservableController", function($scope, Restangular, messages,
    $log, $routeSegment, $location,observables, $anchorScroll, $filter, ngTableParams) {
  $scope.permissions=$scope.event.userpermissions;
  
  function getAttributes(){
    var attributes = [];
    function generateItems(object, observable, composed){
      var item = {};
      if (object.attributes.length > 0) {
        for (var i = 0; i < object.attributes.length; i++) {
          item = {};
          item.value = object.attributes[i].value;
          item.definition = object.attributes[i].definition;
          item.ioc = object.attributes[i].ioc;
          item.shared = object.attributes[i].shared;
          item.object = object.definition.name;
          item.observable = observable.title;
          if (object.attributes[i]){
            item.properties = object.attributes[i].properties;
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
        }
      } else {
        item = {};
        item.observable = observable.title;
        item.object = object.definition.name;
        item.value = 'No attributes were definied';
        attributes.push(item);
      }
      // continue with the related objects
      for (var j = 0; j < object.related_objects.length; j++) {
        generateItems(object.related_objects[j].object, observable);
      }
    }
    
    function processObservavle(observable, composed){
      if (observable.observable_composition){
        for (var i = 0; i < observable.observable_composition.observables.length; i++) {
          processObservavle(observable.observable_composition.observables[i], observable.observable_composition);
        }
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
    for (var i = 0; i < $scope.observables.length; i++) {
      processObservavle($scope.observables[i], null);
    }
    return attributes;
  }
  
  $scope.observables = observables;
  $scope.flat=false;
  $scope.flatAttributes = [];

  $scope.attribuesTable = new ngTableParams({
    page: 1,            // show first page
    count: 10,           // count per page
  }, {
      total: $scope.flatAttributes.length, // length of data
      getData: function($defer, params) {
        var orderedData = params.filter() ? $filter('filter')($scope.flatAttributes, params.filter()) : $scope.flatAttributes;
        orderedData = params.sorting() ? $filter('orderBy')(orderedData, params.orderBy()) : orderedData;
        orderedData = orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count());
        $defer.resolve(orderedData);
      }
  }); 
  
  $scope.getColor = function(attribute){
    if (attribute.properties.proposal && !attribute.properties.validated){
      return 'background-color: yellow;';
    }else {
      if (!attribute.properties.proposal && !attribute.properties.validated){
        return 'background-color: red;';
      } else {
        
      }
    }
  };
  
  $scope.showFlat=function(){
    $scope.flat=true;
    $scope.flatAttributes = getAttributes();
    $scope.attribuesTable.reload();
  };

  $scope.showStructured=function(){
    $scope.flat=false;
    $scope.flatAttributes = [];
    $scope.attribuesTable.reload();
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
    $log, $routeSegment, $location,indicators, $anchorScroll, ngTableParams, $filter) {
  $scope.permissions=$scope.event.userpermissions;
  
  function getAttributes(){
    var attributes = [];
    function generateItems(object, observable, composed){
      var item = {};
      if (object.attributes.length > 0) {
        for (var i = 0; i < object.attributes.length; i++) {
          item = {};
          item.value = object.attributes[i].value;
          item.definition = object.attributes[i].definition;
          item.ioc = object.attributes[i].ioc;
          item.shared = object.attributes[i].shared;
          item.object = object.definition.name;
          item.observable = observable.title;
          if (object.attributes[i]){
            item.properties = object.attributes[i].properties;
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
        }
      } else {
        item = {};
        item.observable = observable.title;
        item.object = object.definition.name;
        item.value = 'No attributes were definied';
        attributes.push(item);
      }
      // continue with the related objects
      for (var j = 0; j < object.related_objects.length; j++) {
        generateItems(object.related_objects[j].object, observable);
      }
    }
    
    function processObservavle(observable, composed){
      if (observable.observable_composition){
        for (var i = 0; i < observable.observable_composition.observables.length; i++) {
          processObservavle(observable.observable_composition.observables[i], observable.observable_composition);
        }
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
    for (var i = 0; i < $scope.indicators.length; i++) {
      for (var j = 0; j < $scope.indicators[i].observables.length; j++) {
        processObservavle($scope.indicators[i].observables[j], null);
      }
    }
    return attributes;
  }
  

  
  $scope.indicators = indicators;
  $scope.flat=false;
  $scope.flatAttributes = [];
  
  $scope.attribuesTable = new ngTableParams({
    page: 1,            // show first page
    count: 10,           // count per page
  }, {
      total: $scope.flatAttributes.length, // length of data
      getData: function($defer, params) {
        var orderedData = params.filter() ? $filter('filter')($scope.flatAttributes, params.filter()) : $scope.flatAttributes;
        orderedData = params.sorting() ? $filter('orderBy')(orderedData, params.orderBy()) : orderedData;
        orderedData = orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count());
        $defer.resolve(orderedData);
      }
  }); 
  
  $scope.showFlat=function(){
    $scope.flat=true;
    $scope.flatAttributes = getAttributes();
    $scope.attribuesTable.reload();
  };
  $scope.showStructured=function(){
    $scope.flat=false;
    $scope.flatAttributes = [];
    $scope.attribuesTable.reload();
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

  $scope.getColor = function(attribute){
    if (attribute.properties.proposal && !attribute.properties.validated){
      return 'background-color: yellow;';
    }else {
      if (!attribute.properties.proposal && !attribute.properties.validated){
        return 'background-color: red;';
      } else {
        
      }
    }
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
        for (var i = 0; i < $scope.openedEvents.length; i++) {
          if ($scope.openedEvents[i].identifier === data.identifier){
            $scope.openedEvents[i].stix_header.title = data.stix_header.title;
          }
        }
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
    $log, $routeSegment, $location, useradmin, $modal, relations, ngTableParams, comments, $filter) {
  if (useradmin){
    $scope.isAdmin = true;
  } else {
    $scope.isAdmin = false;
  }
  
  if (relations.length > 0){
    $scope.showRelations = true;
  } else {
    $scope.showRelations = false;
  }
  
  
  $scope.tableRelations = new ngTableParams({
    page: 1,            // show first page
    count: 10           // count per page
  }, {
    total: relations.length, // length of data
    getData: function ($defer, params) {
      var orderedData = params.filter() ? $filter('filter')(relations, params.filter()) : relations;
      orderedData = params.sorting() ? $filter('orderBy')(orderedData, params.orderBy()) : orderedData;
      $scope.relations = orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count());
      params.total(orderedData.length); // set total for recalc pagination
      $defer.resolve($scope.relations);
    }
  });

  $scope.tableComments = new ngTableParams({
    page: 1,            // show first page
    count: 10,           // count per page
  }, {
    total: comments.length, // length of data
    getData: function ($defer, params) {
      
      var orderedData = params.filter() ? $filter('filter')(comments, params.filter()) : comments;
      orderedData = params.sorting() ? $filter('orderBy')(orderedData, params.orderBy()) : orderedData;
      $scope.comments = orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count());
      params.total(orderedData.length); // set total for recalc pagination
      $defer.resolve($scope.comments);

    }
  });
  
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
          for (var i = 0; i < $scope.openedEvents.length; i++) {
            if ($scope.openedEvents[i].identifier === $scope.event.identifier){
              $scope.openedEvents.splice(i, 1);
              $location.path("/events/all");
              break;
            }
          }
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
    for (var i = 0; i < $scope.groups.length; i++) {
      if ($scope.groups[i].identifier === $scope.ownergroup){
        group = $scope.groups[i];
        break;
      }
    }
    
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

app.controller("eventGroupController", function($scope, Restangular, messages, $log, $routeSegment, groups, eventpermissions) {
  $scope.multiple = false;
  
  $scope.allItems = groups;
  var original_values = {};
  
  $scope.associated = eventpermissions;
  
  $scope.remaining = angular.copy($scope.allItems);
  
  if (!$scope.associated){
    $scope.associated =[];
  }

  $scope.setPropeties = function(){
    $scope.showBtn = true;
    $scope.selected_remaining = [];
    if ($scope.selected_accociated.length == 1){
      //Get Permissions from selected
      for (var i = 0; i < $scope.associated.length; i++) {
        $scope.multiple = false;
        if ($scope.associated[i].group.identifier == $scope.selected_accociated[0]) {
          $scope.permissions = angular.copy($scope.associated[i].permissions);
          original_values = angular.copy($scope.associated[i].permissions);
          break;
        }
      }
      
    } else {
      $scope.multiple = true;
    }
  };
  
  $scope.setRemPropeties = function(){
    $scope.selected_accociated = [];
    $scope.showBtn = false;
    if ($scope.selected_remaining.length == 1){
      //Get Permissions from selected
      for (var i = 0; i < $scope.remaining.length; i++) {
        $scope.multiple = false;
        if ($scope.remaining[i].identifier == $scope.selected_remaining[0]) {
          $scope.permissions = angular.copy($scope.remaining[i].default_event_permissions);
          original_values = angular.copy($scope.remaining[i].default_event_permissions);
          break;
        }
      }
      
    } else {
      $scope.multiple = true;
    }
  };
  
  $scope.resetPermissions = function() {
    $scope.permissions = angular.copy(original_values);
  };
  
  $scope.permissionsChanged = function ()
  {
    return !angular.equals($scope.permissions, original_values);
  };
  
  $scope.$watch(function() {
    return $scope.associated;
  }, function(newVal, oldVal) {
    setRemaining();
  });

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
      for (var i = 0; i < $scope.groups.length; i++) {
        if ($scope.groups[i].identifier == uuid) {
          $scope.permissions = angular.copy($scope.groups[i].default_event_permissions);
        }
      }
    } else {
      $scope.permissions = {};
    }
  };
  
  function sumbit_changes(eventPermission){
    restangularPermission = Restangular.restangularizeElement($scope.event, eventPermission, 'group');
    restangularPermission.put().then(function (data) {
      if (data){
        messages.setMessage({'type':'success','message':'Group sucessfully edited'});
        //update group in browser
        for (var i = 0; i < $scope.associated.length; i++) {
          $scope.multiple = false;
          if ($scope.associated[i].group.identifier == $scope.selected_accociated[0]) {
            $scope.associated[i] = data;
            break;
          }
        }
      } else {
        messages.setMessage({'type':'danger','message':'An unexpected error occured'});
      }
      
    }, function (response) {
      $scope.comment = angular.copy(original_comment);
      handleError(response, messages);
    });
  }
  
  $scope.submitPermissionChanges = function(){
    var eventPermission = null;
    for (var i = 0; i < $scope.associated.length; i++) {
      $scope.multiple = false;
      if ($scope.associated[i].group.identifier == $scope.selected_accociated[0]) {
        eventPermission = $scope.associated[i];
        eventPermission.permissions = $scope.permissions;
        sumbit_changes(eventPermission);
        break;
      }
    }
  };

  
  function setRemaining() {
    var items_to_remove = [];
    for (var i = 0; i < $scope.remaining.length; i++) {
      // remove selected from the group
      if ($scope.associated) {
        for (var j = 0; j < $scope.associated.length; j++) {
          if ($scope.associated[j].group.identifier === $scope.remaining[i].identifier){
            items_to_remove.push(i);
            break;
          }
        }
      } else {
        //restangularize object
        $scope.associated =  [];
      }
    }
    //sort array that the values are from big to low as the $scope.remaining array is shrinking
    items_to_remove = items_to_remove.reverse();
    for (var k = 0; k < items_to_remove.length; k++) {
      var index = items_to_remove[k];
      $scope.remaining.splice(index, 1);
    }
  }
  
  $scope.selected_accociated = [];
  $scope.selected_remaining = [];
  var original_associated = angular.copy($scope.associated);
  
  function add_item(added_group, permissions) {
    Restangular.one('event', $scope.event.identifier).all('group').post({'group': {'identifier':added_group.identifier,'name':added_group.name}, 'permissions': permissions}).then(function (item) {
      if (item) {
        messages.setMessage({'type':'success','message':'Item sucessfully associated'});
      } else {
        
        messages.setMessage({'type':'danger','message':'Unkown error occured'});
      }
      $scope.associated.push(item);
      
      $scope.selected_accociated = [];
      $scope.selected_remaining = [];
    }, function (response) {
      $scope.remaining = angular.copy($scope.allItems);
      $scope.associated = original_associated;
      
      handleError(response, messages);
    });
  }
  
  $scope.groupAdd = function() {
    var original_associated = angular.copy($scope.associated);
    for (var i = 0; i < $scope.selected_remaining.length; i++) {
      // remove selected from the group
      for (var j = 0; j < $scope.remaining.length; j++) {
        if ($scope.selected_remaining[i] == $scope.remaining[j].identifier){
          $scope.remaining.splice(j, 1);
        }
      }
      
      //append the selected to the remaining groups
      //check if there are children
      //search for the group details
      for (var k = 0; k < $scope.allItems.length; k++) {
        if ($scope.allItems[k].identifier == $scope.selected_remaining[i]){
          
          
          //derestangularize the element
          var permissions = $scope.allItems[k].default_event_permissions;
          if ($scope.selected_remaining.length == 1) {
            permissions = $scope.permissions;
          }
          add_item($scope.allItems[k], permissions);
        }
      }
    }
    $scope.permissions = {};
    $scope.selected_accociated = [];
    $scope.selected_remaining = [];
  };
  
  function remove_item(restangularPermission){
    restangularPermission.remove().then(function (item) {
      if (item) {
        messages.setMessage({'type':'success','message':'Item sucessfully removed'});
      } else {
        messages.setMessage({'type':'danger','message':'Unkown error occured'});
      }
      $scope.selected_accociated = [];
      $scope.selected_remaining = [];
    }, function (response) {
      $scope.remaining = angular.copy($scope.allItems);
      $scope.associated = original_associated;
      
      handleError(response, messages);
    });
  }
  
  
  $scope.groupRemove = function() {
    for (var i = 0; i < $scope.selected_accociated.length; i++) {
      // remove selected from the group
      for (var j = 0; j < $scope.associated.length; j++) {
        if ($scope.selected_accociated[i] == $scope.associated[j].group.identifier){
          restangularPermission = Restangular.restangularizeElement($scope.event, $scope.associated[j], 'group');
          $scope.associated.splice(j, 1);
          remove_item(restangularPermission);
          break;
        }
      }
      
      //search for the group details
      for (var k = 0; k < $scope.allItems.length; k++) {
        if ($scope.allItems[k].identifier == $scope.selected_accociated[i]){
          $scope.remaining.push($scope.allItems[k]);
        }
      }
    }
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
