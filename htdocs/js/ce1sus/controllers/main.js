/**
 * @author Weber Jean-Paul (jean-paul.weber@govcert.etat.lu)
 * @link https://github.com/GOVCERT-LU/ce1sus
 * @copyright Copyright 2013-2014, GOVCERT Luxembourg
 * @license GPL v3+
 * 
 * Created on Oct 29, 2014
 */



ce1susApp.controller("mainController", function($scope) {
  var $log = null;
  //$scope.menus = menus;
  //$scope.versionInformation = versions;


  
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

});