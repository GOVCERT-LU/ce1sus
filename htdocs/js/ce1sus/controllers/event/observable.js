/**
 * 
 */

app.controller("observableAddController", function($scope, Restangular, messages, $routeSegment,$location) {
  var original_observable = {};
  $scope.observable={'fo':'test'};
  
  $scope.closeModal = function(){
    $scope.observable = angular.copy(original_observable);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetObservable = function ()
  {
    $scope.observable = angular.copy(original_observable);

  };
  

  
  $scope.observableChanged = function ()
  {
    return !angular.equals($scope.observable, original_observable);
  };
  
  $scope.submitObservable = function(){
    $scope.$parent.$parent.appendObservable($scope.observable);
    $scope.$hide();
  };


});

app.controller("observableEditController", function($scope, Restangular, messages, $routeSegment,$location) {
  var original_observable = angular.copy($scope.observable);
  $scope.working_copy = angular.copy($scope.observable);
  $scope.closeModal = function(){
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetObservable = function ()
  {
    $scope.working_copy = angular.copy(original_observable);

  };
  

  
  $scope.observableChanged = function ()
  {
    return !angular.equals($scope.working_copy, original_observable);
  };
  
  $scope.submitObservable = function(){
    $scope.$parent.$parent.setObservable($scope.working_copy);
    $scope.$hide();
  };


});

