/**
 * 
 */

app.controller("observableObjectAddController", function($scope, Restangular, messages, $routeSegment,$log) {
  $scope.definitions =[];
  Restangular.one("object").getList(null, null, {"Complete": false}).then(function (objects) {
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
    
    $scope.$parent.$parent.appendObservableObject($scope.observableObject);
    $scope.$hide();
  };


});

app.controller("observableObjectEditController", function($scope, Restangular, messages, $routeSegment,$location) {
  var original_observableObject = angular.copy($scope.observableObject);
  $scope.working_copy = angular.copy($scope.observableObject);
  $scope.closeModal = function(){
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetObservableObject = function ()
  {
    $scope.working_copy = angular.copy(original_observableObject);

  };
  

  
  $scope.observableObjectChanged = function ()
  {
    return !angular.equals($scope.working_copy, original_observableObject);
  };
  
  $scope.submitObservableObject = function(){
    $scope.$parent.$parent.setObservableObject($scope.working_copy);
    $scope.$hide();
  };


});
