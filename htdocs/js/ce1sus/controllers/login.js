/**
 * @author Weber Jean-Paul (jean-paul.weber@govcert.etat.lu)
 * @link https://github.com/GOVCERT-LU/ce1sus
 * @copyright Copyright 2013-2014, GOVCERT Luxembourg
 * @license GPL v3+
 * 
 * Created on Oct 29, 2014
 */
app.controller("loginController", function($scope, Restangular, messages,
    $log, $routeSegment, $location) {

  $scope.user = {};
  $scope.login = function() {
    Restangular.all("login").post($scope.user).then(function(data) {
      if (data) {
        $log.info(data);
        // reload the whole window with the loggedin informations
        window.location.href="/";
      }
    });
  };
  $scope.$routeSegment = $routeSegment;
  
});

app.controller("logoutController", function($scope, Restangular,
    messages, $log, $routeSegment) {
  Restangular.one("logout").get().then(function(data) {
    $scope.logoutText = "You are still logged in";
    if (data) {
      $log.info(data);
      // reload the whole window with the loggedin informations
      window.location = "/";
      $scope.logoutText = "You have logged out";
    }
  });
  $scope.$routeSegment = $routeSegment;
  
});