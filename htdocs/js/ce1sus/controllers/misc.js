/**
 * 
 */

app.controller('ladingController', function($scope, $routeSegment, version, menus, changelog) {
  
});

app.controller('errorController', function($scope, error) {
  $scope.error = error;
});

app.controller('loadingController', function($scope, cfpLoadingBar) {
  $scope.$watch(function() {
    return cfpLoadingBar.status();
  }, function(newValue, oldValue) {
    $scope.status = Math.floor(newValue * 100);
  });
  
});