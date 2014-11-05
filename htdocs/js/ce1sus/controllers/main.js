/**
 * @author Weber Jean-Paul (jean-paul.weber@govcert.etat.lu)
 * @link https://github.com/GOVCERT-LU/ce1sus
 * @copyright Copyright 2013-2014, GOVCERT Luxembourg
 * @license GPL v3+
 * 
 * Created on Oct 29, 2014
 */

app.controller('layoutController', function($scope, $routeSegment, version, menus, $log) {
  
  $scope.$routeSegment = $routeSegment;
  $scope.versionInformation = version;
  $scope.menus = menus;
  $scope.createSubmenus = function(submenus) {
    var subMenuArray = [];
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
});

app.controller('homeController', function($scope, $routeSegment, changelog, $log) {
  $scope.changelog = changelog;
});
/*
ce1susApp.controller("mainController", function($scope, Restangular, messages,
    $log, $routeSegment) {
  
  Restangular.setErrorInterceptor(function(response, deferred, responseHandler) {
    return handleError(response, messages);
});

  $scope.$routeSegment = $routeSegment;
  
  Restangular.one("version").get().then(function(version) {
    $scope.versionInformation = version;
  });
  Restangular.oneUrl("text", "/welcome_message").get().then(function(changelog) {
    $scope.changelog = changelog;
  });
  Restangular.allUrl("menus", "/menus/primary_menus").getList().then(function(menus) {
    $scope.menus = menus;
  });
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

});
*/