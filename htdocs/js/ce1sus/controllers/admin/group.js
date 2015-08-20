/**
 * @author Weber Jean-Paul (jean-paul.weber@govcert.etat.lu)
 * @link https://github.com/GOVCERT-LU/ce1sus
 * @copyright Copyright 2013-2014, GOVCERT Luxembourg
 * @license GPL v3+
 * 
 * Created on Oct 29, 2014
 */

app.controller("groupController", function($scope, Restangular, messages, $routeSegment, $location, groups, tlps) {

  $scope.groups = groups;
  /*
  if (($scope.groups.length > 0) && (!$routeSegment.$routeParams.id)){
    $location.path("/admin/group/"+ $scope.groups[0].identifier);
  }
  */
  $scope.$routeSegment = $routeSegment;
  $scope.tlps = tlps;
});

app.controller("groupAddController", function($scope, Restangular, messages, $routeSegment,$location) {
  
  $scope.group={};
  var original_group = {};
  $scope.closeModal = function(){
    $scope.$parent.group = angular.copy(original_group);
    $scope.$hide();
  };
  //Scope functions
  $scope.submitGroup = function(){
    Restangular.all("group").post($scope.group).then(function (data) {
      if (data) {
        // add to the list of options in this scope
        $scope.groups.push(data);
        $location.path("/admin/group/"+ data.identifier);
        
      }
      messages.setMessage({'type':'success','message':'Group sucessfully added'});
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };
  
  $scope.resetGroup = function ()
  {
    $scope.$hide();
    $scope.group = angular.copy(original_group);
    $scope.addGroupForm.$setPristine();
  };
  
  $scope.groupChanged = function ()
  {
    return !angular.equals($scope.group, original_group);
  };


});


app.controller("groupDetailController", function($scope, Restangular, messages, $routeSegment,$location, $log, $group) {

  original_group = angular.copy($group);
  $scope.group = $group;

  if (!$scope.group.children){
    $scope.group.children = [];
  }
  
  $scope.group.getList("children").then(function (group_response) {
    $scope.group.children = group_response;
  });
  
  //Scope functions
  $scope.removeGroup = function(){
    //remove group from group list
    $scope.group.remove().then(function (data) {
      if (data) {
        
        for (var i = 0; i < $scope.groups.length; i++) {
          if ($scope.groups[i].identifier == $scope.group.identifier) {
            $scope.groups.splice(i, 1);
            if ($scope.groups.length > 0) {
              $location.path("/admin/group/"+ $scope.groups[0].identifier);
            } else {
              $location.path("/admin/group");
            }
            break;
          }
        }
        messages.setMessage({'type':'success','message':'Group sucessfully removed'});
      }
    }, function (response) {
      handleError(response, messages);
    });
  };
  
  $scope.$routeSegment = $routeSegment;

  $scope.setGroup = function(group){
    $scope.group = group;
  };
});



app.controller("groupEditController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_group = angular.copy($scope.group);
  
  $scope.closeModal = function(){
    var group = angular.copy(original_group);
    $scope.$parent.setGroup(group);
    $scope.$hide();

  };
  //Scope functions
  $scope.resetGroup = function ()
  {
    $scope.group = angular.copy(original_group);
    $scope.addGroupForm.$setPristine();
  };
  
  $scope.groupChanged = function ()
  {
    return !angular.equals($scope.group, original_group);
  };
  
  $scope.submitGroup = function(){
    $scope.group.put().then(function (data) {
      if (data) {
        $scope.group = data;
        //update name in menu
        for (var i = 0; i < $scope.groups.length; i++) {
          if ($scope.groups[i].identifier == data.identifier) {
            $scope.groups[i].name = data.name;
            break;
          }
        }
        messages.setMessage({'type':'success','message':'Group sucessfully edited'});
      }
    }, function (response) {
      var group = angular.copy(original_group);
      $scope.$parent.setGroup(group);
      handleError(response, messages);
    });
    $scope.$hide();
  };
  

});
