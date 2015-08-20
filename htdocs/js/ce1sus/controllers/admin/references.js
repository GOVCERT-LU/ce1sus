/**
 * 
 */

app.controller("referenceController", function($scope, Restangular, messages,
    $log, $routeSegment, references, handlers) {
  $scope.references = references;
  $scope.handlers = handlers;
  
  $scope.$routeSegment = $routeSegment;


});

app.controller('referenceDetailController', function($scope, $routeSegment,$reference, $log, messages, $location) {
  
  
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
        for (var i = 0; i < $scope.handlers.length; i++) {
          if ($scope.handlers[i].identifier === $scope.reference.referencehandler_id){
            $scope.reference.referencehandler_name = $scope.handlers[i].name;
            break;
          }
        }
      }
    });
  
  $scope.removeReference = function(){
    //remove user from user list
    $scope.reference.remove().then(function (data) {
      if (data) {
        //remove the selected user and then go to the first one in case it exists
        for (var i = 0; i < $scope.references.length; i++) {
          if ($scope.references[i].identifier === $scope.reference.identifier){
            $scope.references.splice(i, 1);
            if ($scope.references.length > 0) {
              $location.path("/admin/reference/"+ $scope.references[0].identifier);
            } else {
              $location.path("/admin/reference");
            }
            break;
          }
        }
        messages.setMessage({'type':'success','message':'Reference sucessfully removed'});
      }
    }, function (response) {
      handleError(response, messages);
    });
  };
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
      
      if (reference) {
        $scope.references.push(reference);
        $location.path("/admin/reference/"+ reference.identifier);
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
    $scope.reference.modified_on = new Date().getTime();
    $scope.reference.put().then(function (reference) {
      
      if (reference) {
        for (var i = 0; i < $scope.references.length; i++) {
          if ($scope.references[i].identifier == reference.identifier) {
            $scope.references[i].name = reference.name;
            break;
          }
        }
        $scope.reference = reference;
      }
      messages.setMessage({'type':'success','message':'Reference sucessfully added'});
      
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };
});