

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
    $log, $routeSegment, $location, ngTableParams, observables, $anchorScroll) {
  $scope.observables = observables;

});
