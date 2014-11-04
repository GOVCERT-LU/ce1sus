/**
 * @author Weber Jean-Paul (jean-paul.weber@govcert.etat.lu)
 * @link https://github.com/GOVCERT-LU/ce1sus
 * @copyright Copyright 2013-2014, GOVCERT Luxembourg
 * @license GPL v3+
 * 
 * Created on Oct 29, 2014
 */



ce1susApp.controller("mainController", function($scope, Restangular, messages,
    $routeSegment, $log) {

  // Get the menu Items
  Restangular.allUrl("menus", "/menus/primary_menus").getList().then(function(menus){
    $scope.menus = menus;
  });
  
  Restangular.one("version").get().then(function(versions) {
    $scope.versionInformation = versions;
  });

  Restangular.oneUrl("text", "/welcome_message").get().then(function(welcome) {
    $scope.changelog = welcome;
  });

  $scope.$routeSegment = $routeSegment;

  
  //scope functions
  $scope.createSubmenus = function(submenus) {
    subMenuArray = [];
    angular.forEach(submenus, function(entry) {
      if (entry.divider) {
        subMenuArray.push({
          "divider" : true
        });
      } else {
        subMenuArray.push({
          "text" : entry.title,
          "href" : "#" + entry.section
        });
      }
    }, $log);
    return subMenuArray;
  };

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