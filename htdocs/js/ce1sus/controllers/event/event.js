

app.controller("eventController", function($scope, Restangular,$route, messages,
    $log, $routeSegment,eventmenus, $location) {
  
  $scope.eventMenus = eventmenus;
  $scope.openedEvents = [];

  $scope.pushItem = function(event, guiOpen) {
    found = false;
    angular.forEach($scope.openedEvents, function(value, index) {
      if (value.identifier == event.identifier){
        found = true;
      }
    }, $log);
    if (!found) {
      var url = '/events/event/'+event.identifier;
      $scope.openedEvents.push({
        icon: '',
        title: event.title,
        section: 'main.layout.events.event',
        reload: false,
        close: true,
        href: url,
        identifier: event.identifier
      });
      if (guiOpen){
        $location.path(url);
      }
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
  
  $scope.foo = function() {
    $scope.text = [{"title":"foo"}];
  };
  $scope.reloadPage = function() {
    $route.reload();
  };
  $scope.$routeSegment = $routeSegment;
});

app.controller("viewEventController", function($scope, Restangular, messages,
    $log, $routeSegment, $location, ngTableParams, $event) {
  $scope.event = $event;
  $scope.pushItem($scope.event);
});

app.controller("eventObservableController", function($scope, Restangular, messages,
    $log, $routeSegment, $location, ngTableParams, observables, $anchorScroll, Pagination) {
  $scope.getAttributes=function(){
    function processObservavle(attributes, observable, composed){
      if (observable.observable_composition){
        angular.forEach(observable.observable_composition.observables, function(compobservable, index) {
          processObservavle(attributes, compobservable, observable.observable_composition);
        },$log);
      } else {
        angular.forEach(observable.object.attributes, function(attribute, index) {
          var item = {};
          item.value = attribute.value;
          item.definition = attribute.definition;
          item.ioc = attribute.ioc;
          item.shared = attribute.shared;
          item.object = observable.object.definition.name;
          //TODO: add referenced Objects
          item.observable = observable.title;
          if (composed) {
            item.composed = composed.title;
            item.composedoperator = composed.operator;
            item.composedlength = composed.observables.length;
          }
          attributes.push(item);
        }, $log);
      }
    }
    var attributes = [];
    angular.forEach($scope.observables, function(observable, index) {
      processObservavle(attributes, observable, null);
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

app.controller("addEventController", function($scope, Restangular, messages,
    $log, $routeSegment, $location, statuses, risks, tlps, analyses) {
  $scope.statuses=statuses;
  $scope.risks=risks;
  $scope.tlps=tlps;
  $scope.anlysises=analyses;
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
      }
      messages.setMessage({'type':'success','message':'Event sucessfully added'});
      
    }, function (response) {
      $scope.event = angular.copy(original_event);
      handleError(response, messages);
    });
  };
});
