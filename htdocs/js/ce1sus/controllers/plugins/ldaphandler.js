/**
 * @author Weber Jean-Paul (jean-paul.weber@govcert.etat.lu)
 * @link https://github.com/GOVCERT-LU/ce1sus
 * @copyright Copyright 2013-2014, GOVCERT Luxembourg
 * @license GPL v3+
 * 
 * Created on Oct 29, 2014
 */

app.controller('ldapController', function($scope, ngTableParams,Restangular, messages,$filter, $log) {
  var data = [];
  Restangular.oneUrl("ldapusers", "/plugins/ldap/user").get().then(function (ldapusers) {
    if (!ldapusers){
      $scope.$hide();
    }
    data = ldapusers;
  });
  
  
  $scope.tableParams = new ngTableParams({
      page: 1,            
      count: 10,          
      sorting: {
          name: 'asc'     
      },
      filter: {
        name: ''
      } 
  }, {
      total: data.length,           // length of data
      getData: function($defer, params) {
        var filteredData = params.filter() ?
            $filter('filter')(data, params.filter()) :
            data;
        var orderedData = params.sorting() ?
            $filter('orderBy')(filteredData, params.orderBy()) :
            data; 
            
            params.total(orderedData.length); // set total for recalc pagination
            $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count())); 
      }
  });
  
  $scope.user = {};
  
  //Scope functions
  $scope.addLdapUser = function() {
    Restangular.allUrl("ldapusers", "/plugins/ldap/user").post($scope.user).then(function (ldapusers) {
      if (ldapusers){
        $scope.users.push(ldapusers);
      }
      messages.setMessage({'type':'success','message':'User sucessfully added'});
    });
    $scope.$hide();
  };
  
  //Event listeners to display the loading animation
  $scope.$on('cfpLoadingBar:completed', function(event) {
    // assign the loaded track as the 'current' 
    $scope.tableloading = false;
    try {
     if (!$scope.$$phase) {
      $scope.$apply($scope.tableloading);
     }
    } catch (err) {
      $log.error(err);
    }
  });
  $scope.$on('cfpLoadingBar:started', function(event) {
    // assign the loaded track as the 'current' 
    $scope.tableloading = true;
    try {
     if (!$scope.$$phase) {
      $scope.$apply($scope.tableloading);
     }
    } catch (err) {
      $log.error(err);
    }
  });

});