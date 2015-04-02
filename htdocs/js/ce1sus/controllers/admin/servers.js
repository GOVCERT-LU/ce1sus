

app.controller("SyncMainServersController", function($scope, Restangular, messages, $log, $routeSegment, $location, servertypes) {
  $scope.servertypes = servertypes;
});

app.controller("SyncServersController", function($scope, Restangular, messages, $log, $routeSegment, $location, syncservers) {
  $scope.syncservers = syncservers;
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
    Restangular.all("syncservers").post($scope.server).then(function (server) {
      
      if (server) {
        $scope.servers.push(server);
      }
      messages.setMessage({'type':'success','message':'Server sucessfully added'});
      
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };


});

app.controller("serverEditController", function($scope, Restangular, messages, $log, $routeSegment, $location) {
  
  $scope.closeModal = function(){
    var attribute = angular.copy(original_attribute);
    $scope.$parent.setAttribute(attribute);
    $scope.$hide();

  };
});