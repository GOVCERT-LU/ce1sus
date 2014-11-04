

ce1susApp.controller("eventController", function($scope, Restangular,$route, messages,
    $log, $routeSegment) {
  
  $scope.start = function() {
    cfpLoadingBar.start();
  };
  $scope.complete = function() {
    cfpLoadingBar.complete();
  };
  
  Restangular.oneUrl("menus", "/menus/event_links").get().then(function(eventMenus){
    $scope.eventMenus = eventMenus;
  }, function(response) {
    handleError(response, messages);
  });

  $scope.pushItem = function(title, identifer) {
    $scope.menus.push({
      eventID : identifer,
      title : identifer,
      section : "about",
      icon : "fa-lock"
    });
  };

  $scope.removeItem = function(element_id) {
    angular.forEach($scope.menus, function(value, index) {
      if (value.eventID) {
        if (value.eventID == element_id) {
          $scope.menus.splice(index, 1);
        }
      }
    });
  };
  
  $scope.foo = function() {
    $scope.text = [{"title":"foo"}];
  };
  $scope.reloadPage = function() {
    $route.reload();
  };
  $scope.$routeSegment = $routeSegment;
});