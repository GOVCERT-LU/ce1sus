/**
 * @author Weber Jean-Paul (jean-paul.weber@govcert.etat.lu)
 * @link https://github.com/GOVCERT-LU/ce1sus
 * @copyright Copyright 2013-2014, GOVCERT Luxembourg
 * @license GPL v3+
 * 
 * Created on Oct 29, 2014
 */

app.controller("groupController", function($scope, Restangular, messages, $routeSegment, $location, groups) {

  $scope.groups = groups;
  /*
  if (($scope.groups.length > 0) && (!$routeSegment.$routeParams.id)){
    $location.path("/admin/group/"+ $scope.groups[0].identifier);
  }
  */
  $scope.$routeSegment = $routeSegment;

});

app.controller("groupAddController", function($scope, Restangular, messages, $routeSegment,$location) {
  
  $scope.group={};
  var original_group = {};
  
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
  
  $scope.modalTitle ="Edit Group " + data.groupname;
  $scope.group.getList("children").then(function (group_response) {
    $scope.group.children = group_response;
  });
  var remaining = [];
  var found = false;
  angular.forEach($scope.groups, function(available_group) {
    angular.forEach($scope.group.children, function(child_group) {
      if (available_group.identifier === child_group.identifier){
        found = true;
      }
    }, $log);
    if (!found){
      remaining.push(available_group);
    }
  }, $log);
  $scope.remaining = remaining;

  
  //Scope functions
  $scope.removeGroup = function(){
    //remove group from group list
    $scope.group.remove().then(function (data) {
      if (data) {
        var index = 0;
        angular.forEach($scope.groups, function(entry) {
          
          if (entry.identifier == $scope.group.identifier) {
            $scope.groups.splice(index, 1);
            if ($scope.groups.length > 0) {
              $location.path("/admin/group/"+ $scope.groups[0].identifier);
            } else {
              $location.path("/admin/group");
            }
          }
          index++;
        }, $log);
        messages.setMessage({'type':'success','message':'Group sucessfully removed'});
      }
      $scope.$hide();
    }, function (response) {
      handleError(response, messages);
    });
  };
  
  //TODO: Write actions for add and remove groups from group
  $scope.foo = function(input){
    console.log('aaaa');
  };
  
  $scope.$routeSegment = $routeSegment;


});



app.controller("groupEditController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_group = angular.copy($scope.group);
  
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
        angular.forEach($scope.groups, function(entry) {
          if (entry.identifier == data.identifier) {
            entry.name = data.name;
          }
        }, $log);
        messages.setMessage({'type':'success','message':'Group sucessfully edited'});
      }
      $scope.$hide();
    }, function (response) {
      handleError(response, messages);
    });
  };
  

});
