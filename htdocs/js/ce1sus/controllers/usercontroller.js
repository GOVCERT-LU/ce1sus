app.controller("userProfileController", function($scope, Restangular, messages, $log, $routeSegment, $location, user) {
  $scope.user = user;
});

app.controller("userGroupController", function($scope, Restangular, messages,$log, $routeSegment, $location, group) {
  $scope.group = group;
});