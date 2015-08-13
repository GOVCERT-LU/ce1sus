/**
 * @author Weber Jean-Paul (jean-paul.weber@govcert.etat.lu)
 * @link https://github.com/GOVCERT-LU/ce1sus
 * @copyright Copyright 2013-2014, GOVCERT Luxembourg
 * @license GPL v3+
 * 
 * Created on Oct 29, 2014
 */

app.controller("userController", function($rootScope, $scope, Restangular, messages, $routeSegment, $location,  groups, showLdapBtn, users) {
  
  $scope.groups = groups;
  $scope.showLdapBtn = showLdapBtn;
  
  $scope.users = users;
  /*
  if (($scope.users.length > 0) && (!$routeSegment.$routeParams.id)) {
    $location.path("/admin/user/"+ $scope.users[0].identifier);
  }
  */
  

  $scope.$routeSegment = $routeSegment;


});

app.controller("userAddController", function($scope, Restangular, messages, $routeSegment,$location) {
  var original_user = {};
  $scope.user={};
  
  $scope.closeModal = function(){
    $scope.$parent.user = angular.copy(original_user);
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
    Restangular.all("user").post($scope.user).then(function (data) {
      
      if (data) {
        $scope.users.push(data);
        $location.path("/admin/user/"+ data.identifier);
      }
      messages.setMessage({'type':'success','message':'User sucessfully added'});
      
    }, function (response) {
      $scope.$parent.user = angular.copy(original_user);
      handleError(response, messages);
    });
    $scope.$hide();
  };


});

app.controller("userDetailController", function($scope, $routeSegment,$user, $log, messages, Restangular, showMailBtn, $location) {

  $scope.user = $user;
  $scope.showMailBtn= showMailBtn;
  
  $scope.$watch(function() {
    return $scope.user.group_id;
    }, function(newVal, oldVal) {
      //keep the group name shown instead the uuid, but only if there are groups
      if ($scope.groups.length > 0) {
        angular.forEach($scope.groups, function(entry) {
          if (entry.identifier === $scope.user.group_id){
            $scope.user.group_name = entry.name;
          }
        }, $log);
      }
    });
  
  

  //scope functions
  $scope.removeUser = function(){
    //remove user from user list
    $scope.user.remove().then(function (data) {
      if (data) {
        //remove the selected user and then go to the first one in case it exists
        var index = 0;
        angular.forEach($scope.users, function(entry) {
          if (entry.identifier === $scope.user.identifier){
            $scope.users.splice(index, 1);
            if ($scope.users.length > 0) {
              $location.path("/admin/user/"+ $scope.users[0].identifier);
            } else {
              $location.path("/admin/user");
            }
          }
          
          index++;
        }, $log);
        messages.setMessage({'type':'success','message':'User sucessfully removed'});
      }
    }, function (response) {
      handleError(response, messages);
    });
  };

  $scope.$routeSegment = $routeSegment;
  $scope.setUser = function(user){
    $scope.user = user;
  };
  
  $scope.activate = function(){
    
    Restangular.one('user/activate',$scope.user.identifier).get({"complete": true, "inflated": true}).then(function(data) {
      message = {"type":"success","message":"User Activated"};
      messages.setMessage(message);
      $scope.user = data;
    }, function (response) {
      handleError(response, messages);
    });
    
  };
  
  $scope.resentmail = function(){
    
    Restangular.one('user/resentmail',$scope.user.identifier).get().then(function(data) {
      message = {"type":"success","message":"Mail successfully sent to user "+item.username};
      messages.setMessage(message);
      $scope.user = data;
    }, function (response) {
      handleError(response, messages);
    });
    
  };

});

app.controller("userEditController", function($scope, Restangular, messages, $routeSegment,$location,  $log) {
  var original_user = angular.copy($scope.user);

  
  //Scope functions
  $scope.resetUser = function ()
  {
    $scope.user = angular.copy(original_user);
  };
  
  $scope.closeModal = function(){
    var user = angular.copy(original_user);
    $scope.$parent.setUser(user);
    $scope.$hide();
  };
  
  $scope.userChanged = function ()
  {
    var result = !angular.equals($scope.user, original_user);
    return result;
  };
  
  $scope.submitUser = function(){
    $scope.user.modified_on = new Date().getTime();
    $scope.user.put().then(function (data) {
      if (data) {
        //update username in case
        angular.forEach($scope.users, function(entry) {
          if (entry.identifier === data.identifier){
            entry.username = data.username;
          }
        }, $log);
        $scope.user = data;
      }
      messages.setMessage({'type':'success','message':'User sucessfully edited'});
    }, function (response) {
      var user = angular.copy(original_user);
      $scope.$parent.setUser(user);
      handleError(response, messages);
    });
    $scope.$hide();
  };

});