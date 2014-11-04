/**
 * @author Weber Jean-Paul (jean-paul.weber@govcert.etat.lu)
 * @link https://github.com/GOVCERT-LU/ce1sus
 * @copyright Copyright 2013-2014, GOVCERT Luxembourg
 * @license GPL v3+
 * 
 * Created on Oct 29, 2014
 */
ce1susApp.controller("loginController", function($scope, Restangular, messages,
    $log, $routeSegment) {

  $scope.user = {};
  $scope.login = function() {
    Restangular.all("login").post($scope.user).then(function(data) {
      if (data) {
        $log.info(data);
        // reload the whole window with the loggedin informations
        window.location = "/";
      }
    });
  };
  $scope.$routeSegment = $routeSegment;
  
  //Sdt Ending of functions
  Restangular.setErrorInterceptor(function(response, deferred, responseHandler) {
    return handleError(response, messages);
  });
  $scope.start = function() {
    cfpLoadingBar.start();
  };
  $scope.complete = function() {
    cfpLoadingBar.complete();
  };
});

ce1susApp.controller("logoutController", function($scope, Restangular,
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
  
  //Sdt Ending of functions
  Restangular.setErrorInterceptor(function(response, deferred, responseHandler) {
    return handleError(response, messages);
  });
  $scope.start = function() {
    cfpLoadingBar.start();
  };
  $scope.complete = function() {
    cfpLoadingBar.complete();
  };
});