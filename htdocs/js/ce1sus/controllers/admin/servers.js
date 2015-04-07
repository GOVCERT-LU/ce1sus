

app.controller("SyncMainServersController", function($scope, Restangular, messages, $log, $routeSegment, $location, servertypes, syncservers, ngTableParams, $filter, users) {
  $scope.servertypes = servertypes;
  $scope.syncservers = syncservers;
  $scope.users = users;
  $scope.serversTable = new ngTableParams({
    page: 1,            // show first page
    count: 10,           // count per page
    sorting: {
      created_at: 'desc'     // initial sorting
    } 
  }, {
    total: $scope.syncservers.length, // length of syncservers
    getData: function($defer, params) {

      // use build-in angular filter

      var filteredData = params.filter() ?

              $filter('filter')($scope.syncservers, params.filter()) :

              $scope.syncservers;

      var orderedData = params.sorting() ?

              $filter('orderBy')(filteredData, params.orderBy()) :

              $scope.syncservers;

      params.total(orderedData.length); // set total for recalc pagination

      $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));

    }
  }); 
});

app.controller("SyncServersController", function($scope, Restangular, messages, $log, $routeSegment, $location,$modal) {
  
  $scope.removeServer = function(server){
    if (confirm('Are you sure you want to delete this server?')) {
      restangularServer = Restangular.restangularizeElement(null, server, 'syncservers');
      restangularServer.remove().then(function (data) {
        if (data) {
          var index = $scope.syncservers.indexOf(server);
          $scope.syncservers.splice(index, 1);
          $scope.serversTable.reload();
          messages.setMessage({'type':'success','message':'Server sucessfully removed'});
        }
      }, function (response) {
        handleError(response, messages);
      });

    }
  };
  $scope.showDetails = function(server){
    $scope.server = server;
    $modal({scope: $scope, template: 'pages/admin/syncservers/modals/serverdetails.html', show: true});
  };
  $scope.editServer = function(server){
    $scope.serverDetails = server;
    $modal({scope: $scope, template: 'pages/admin/syncservers/modals/editserver.html', show: true});
  };
});

app.controller("serverAddController", function($scope, Restangular, messages, $log, $routeSegment, $location) {
  
  var original_server = {};

  $scope.server={};
  
  $scope.resetServer = function ()
  {
    $scope.server = angular.copy(original_server);
  };
  
  $scope.serverChanged = function ()
  {
    return !angular.equals($scope.server, original_server);
  };
  
  $scope.submitServer = function(){
    Restangular.all("syncservers").post($scope.server,{"complete": true}).then(function (server) {
      
      if (server) {
        //set type
        
        $scope.syncservers.push(server);
        $scope.serversTable.reload();
      }
      messages.setMessage({'type':'success','message':'Server sucessfully added'});
      
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };


});

app.controller("serverEditController", function($scope, Restangular, messages, $log, $routeSegment, $location) {
  var original_server = angular.copy($scope.serverDetails);

  $scope.server=$scope.serverDetails;
  
  $scope.closeModal = function(){
    var server = angular.copy(original_server);
    $scope.$parent.setServer(server);
    $scope.$hide();

  };
  

  
  $scope.resetServer = function ()
  {
    $scope.server = angular.copy(original_server);
  };
  
  $scope.serverChanged = function ()
  {
    return !angular.equals($scope.server, original_server);
  };
  
  $scope.submitServer = function(){
    
    var restangularServer = Restangular.restangularizeElement(null, $scope.server, 'syncservers');
    restangularServer.put({'complete':true, 'infated':false}).then(function (server) {
      
      if (server) {
        //set type
        
        $scope.$parent.setServer(server);
        $scope.serversTable.reload();
      }
      messages.setMessage({'type':'success','message':'Server sucessfully Edited'});
      
    }, function (response) {
      $scope.server = angular.copy(original_server);
      handleError(response, messages);
    });
    $scope.$hide();
  };
});