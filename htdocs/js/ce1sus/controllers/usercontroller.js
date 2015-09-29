app.controller("userProfileController", function($scope, Restangular, messages, $log, $routeSegment, $location, user) {
  $scope.user = user;
});

app.controller("userGroupController", function($scope, Restangular, messages,$log, $routeSegment, $location, group) {
  $scope.group = group;
});

app.controller("userProfileEditController", function($scope, Restangular, messages,$log, $routeSegment, $location) {
  var original_user = {};
  
  $scope.closeModal = function(){
    $scope.user = angular.copy(original_user);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetUser = function ()
  {
    $scope.user = angular.copy(original_user);
    $scope.addUserForm.$setPristine();
  };
  
  $scope.userChanged = function ()
  {
    return !angular.equals($scope.user, original_user);
  };
  
  $scope.submitUser = function(){
    restangularizedUser = Restangular.restangularizeElement(null, $scope.user, "user/profile");
    
    restangularizedUser.put({'complete': true, 'inflated': true}).then(function (data) {
      
      if (data) {
        messages.setMessage({'type':'success','message':'User sucessfully added'});
      }

    }, function (response) {
      $scope.user = angular.copy(original_user);
      handleError(response, messages);
    });
    $scope.$hide();
  };
  
});

