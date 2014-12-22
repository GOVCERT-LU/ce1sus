/**
 * 
 */

app.controller("observableObjectAddController", function($scope, Restangular, messages, $routeSegment,$log) {
  $scope.definitions =[];
  Restangular.one("objectdefinition").getList(null, null, {"Complete": false}).then(function (objects) {
    $scope.definitions = objects;
  }, function(response) {
      throw generateErrorMessage(response);
  });
  
  var original_observableObject = {};
  $scope.observableObject={};
  
  $scope.closeModal = function(){
    $scope.observableObject = angular.copy(original_observableObject);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetObservableObject = function ()
  {
    $scope.observableObject = angular.copy(original_observableObject);

  };
  

  
  $scope.observableObjectChanged = function ()
  {
    return !angular.equals($scope.observableObject, original_observableObject);
  };
  
  $scope.submitObservableObject = function(){
    angular.forEach($scope.definitions, function(entry) {
      if (entry.identifier == $scope.observableObject.definition_id){
        $scope.observableObject.definition=entry;
      }
    }, $log);
    $scope.$parent.appendObservableObject($scope.observableObject);
    $scope.$hide();
  };


});


app.controller("objectChildAddController", function($scope, Restangular, messages, $routeSegment,$log) {
  $scope.definitions =[];
  Restangular.one("objectdefinition").getList(null, null, {"Complete": false}).then(function (objects) {
    $scope.definitions = objects;
  }, function(response) {
      throw generateErrorMessage(response);
  });
  
  var original_childObject = {};
  $scope.childObject={};
  
  $scope.closeModal = function(){
    $scope.childObject = angular.copy(original_childObject);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetChildObject = function ()
  {
    $scope.childObject = angular.copy(original_childObject);

  };
  

  
  $scope.childObjectChanged = function ()
  {
    return !angular.equals($scope.childObject, original_childObject);
  };
  
  $scope.submitChildObject = function(){
    angular.forEach($scope.definitions, function(entry) {
      if (entry.identifier == $scope.childObject.definition_id){
        $scope.childObject.definition=entry;
      }
    }, $log);
    
    $scope.$parent.$parent.appendChildObject($scope.childObject);
    $scope.$hide();
  };

});