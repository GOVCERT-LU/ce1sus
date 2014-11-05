

app.controller("eventController", function($scope, Restangular,$route, messages,
    $log, $routeSegment,eventmenus) {
  
  $scope.eventMenus = eventmenus;

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