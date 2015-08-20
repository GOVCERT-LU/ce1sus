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
    for (var i = 0; i < submenus.length; i++) {
      if (submenus[i].divider) {
        subMenuArray.push({
          "divider" : true
        });
      } else {
        subMenuArray.push({
          "text" : submenus[i].title,
          "href" : "#" + submenus[i].section
        });
      }
    }
    return subMenuArray;
  };
  

  
  
  
});

app.controller('homeController', function($scope, $routeSegment, changelog, $log) {
  $scope.changelog = changelog;
});