/**
 * @author Weber Jean-Paul (jean-paul.weber@govcert.etat.lu)
 * @link https://github.com/GOVCERT-LU/ce1sus
 * @copyright Copyright 2013-2014, GOVCERT Luxembourg
 * @license GPL v3+
 * 
 * Created on Oct 29, 2014
 */

ce1susApp.controller("userController", function($rootScope, $scope, Restangular, messages, $routeSegment, $location, cfpLoadingBar) {
  
  $scope.groups = [];
  
  Restangular.one("group").get(null,{"Complete": false}).then(function (groups) {
    $scope.groups = data;
  });
  
  Restangular.oneUrl("ldapusers", "/plugins/is_plugin_avaibable/ldap").get().then(function (ldapusers) {
    if (ldapusers) {
      $scope.showLdapBtn = true;
    } else {
      $scope.showLdapBtn = false;
    }
  });
  
  Restangular.one("user").get(null,{"Complete": false}).then(function (users) {
    
    $scope.users = users;
    if (($scope.users.length > 0) && (!$routeSegment.$routeParams.id)) {
      $location.path("/admin/user/"+ $scope.users[0].identifier);
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

ce1susApp.controller("userAddController", function($scope, Restangular, messages, $routeSegment,$location, cfpLoadingBar) {
  var original_user = {};

  $scope.user={};
  
  //Scope functions
  $scope.resetUser = function ()
  {
    $scope.user = angular.copy(original_user);
    $scope.addUserForm.$setPristine();
  };
  
  $scope.generateAPIKey = function() {
    $scope.user.api_key = generateAPIKey();
  };
  
  $scope.userChanged = function ()
  {
    return !angular.equals($scope.user, original_user);
  };
  
  $scope.submitUser = function(){
    Restangular.all("user").post($scope.user).then(function (user) {
      
      if (data) {
        $scope.users.push(data);
        $location.path("/admin/user/"+ data.identifier);
      }
      messages.setMessage({'type':'success','message':'User sucessfully added'});
      
    });
    $scope.$hide();
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

ce1susApp.controller("userDetailController", function($scope, Restangular, messages, $routeSegment,$location, cfpLoadingBar, $log) {

  var identifier = $routeSegment.$routeParams.id;
  
  $scope.user = {};
  Restangular.one("user",identifier).get(null,{"Complete": true}).then(function (data) {
    $scope.user = data;
  });

  $scope.$watch(function() {
    return $scope.user.group_id;
    }, function(newVal, oldVal) {
      //keep the group name shown instead the uuid
      angular.forEach($scope.groups, function(entry) {
        if (entry.identifier === $scope.user.group_id){
          $scope.user.group_name = entry.name;
        }
      }, $log);
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
          messages.setMessage({'type':'success','message':'User sucessfully removed'});
          index++;
        }, $log);
        
      }
      $scope.$hide();
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

ce1susApp.controller("userEditController", function($scope, Restangular, messages, $routeSegment,$location, cfpLoadingBar, $log) {
  var original_user = angular.copy($scope.user);

  
  //Scope functions
  $scope.resetUser = function ()
  {
    $scope.user = angular.copy(original_user);
    $scope.addUserForm.$setPristine();
  };
  
  $scope.userChanged = function ()
  {
    var result = !angular.equals($scope.user, original_user);
    return result;
  };
  
  $scope.submitUser = function(){
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
    });
    $scope.$hide();
  };
  
  $scope.generateAPIKey = function() {
    $scope.user.api_key = generateAPIKey();
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