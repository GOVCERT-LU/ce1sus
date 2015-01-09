/**
 * 
 */

app.controller("referenceController", function($scope, Restangular, messages,
    $log, $routeSegment, references, handlers) {
  $scope.references = references;
  $scope.handlers = handlers;
  
  $scope.$routeSegment = $routeSegment;


});

app.controller('referenceDetailController', function($scope, $routeSegment,$reference, $log) {
  
  
  $scope.reference = $reference;
  
  
  $scope.$routeSegment = $routeSegment;
  
  $scope.setReference = function(reference){
    $scope.reference = reference;
  };
  
  $scope.$watch(function() {
    return $scope.reference.referencehandler_id;
    }, function(newVal, oldVal) {
      //keep the group name shown instead the uuid, but only if there are groups
      if ($scope.handlers.length > 0) {
        angular.forEach($scope.handlers, function(entry) {
          if (entry.identifier === $scope.reference.referencehandler_id){
            $scope.reference.referencehandler_name = entry.name;
          }
        }, $log);
      }
    });
});

app.controller("referenceAddController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_reference = {};

  $scope.reference={};
  
  $scope.reset = false;
  //Scope functions
  $scope.resetReference = function ()
  {
    $scope.reference = angular.copy(original_reference);
  };
  
  $scope.referenceChanged = function ()
  {
    return !angular.equals($scope.reference, original_reference);
  };
  
  $scope.submitReference = function(){
    Restangular.all("referencedefinition").post($scope.reference).then(function (reference) {
      
      if (data) {
        $scope.references.push(data);
        $location.path("/admin/reference/"+ data.identifier);
      }
      messages.setMessage({'type':'success','message':'Reference sucessfully added'});
      
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };
  
  $scope.closeModal = function(){

    $scope.reference=angular.copy(original_reference);
    $scope.$hide();

  };
});

app.controller("referenceEditController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_reference = angular.copy($scope.reference);
  
  $scope.reset = false;
  //Scope functions
  $scope.resetReference = function ()
  {
    $scope.reference = angular.copy(original_reference);
  };
  
  $scope.closeModal = function(){
    var reference = angular.copy(original_reference);
    $scope.$parent.setReference(reference);
    $scope.$hide();

  };
  
  $scope.referenceChanged = function ()
  {
    return !angular.equals($scope.reference, original_reference);
  };
  
  $scope.submitReference = function(){
    $scope.reference.put($scope.reference).then(function (reference) {
      
      if (data) {
        
        
        $scope.reference = data;
        
        angular.forEach($scope.references, function(entry) {
          if (entry.identifier == data.identifier) {
            entry.name = data.name;
          }
        }, $log);
        $location.path("/admin/reference/"+ data.identifier);
      }
      messages.setMessage({'type':'success','message':'Reference sucessfully added'});
      
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };
});