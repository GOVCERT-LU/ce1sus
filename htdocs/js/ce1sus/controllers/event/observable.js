/**
 * 
 */

app.controller("observableAddController", function($scope, Restangular, messages, $routeSegment,$location) {
  var original_observable = {'properties' : {'shared': true}
                            };
  $scope.observable=angular.copy(original_observable);
  
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
    //return !angular.equals($scope.observable, original_observable);
    //can also be empty
    return true;
  };
  
  $scope.submitObservable = function(){
    Restangular.one('event', $scope.event.identifier).post('observable', $scope.observable, {'complete':true, 'infated':true}).then(function (data) {
      if ($scope.$parent.$parent.appendObservable){
        $scope.$parent.$parent.appendObservable(data);
      } else {
        // apped root level
        $scope.observables.push(data);
      }
    }, function (response) {
      $scope.observable = angular.copy(original_observable);
      handleError(response, messages);
    });
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
    var eventID = $routeSegment.$routeParams.id;
    //Lost the connection to the event
    restangularObservable = Restangular.restangularizeElement(null, $scope.working_copy, 'event/'+eventID+'/observable');
    restangularObservable.put({'complete':true, 'inflated':true}).then(function (data) {
      $scope.$parent.$parent.setObservable(restangularObservable);
    }, function (response) {
      $scope.observable = angular.copy(original_observable);
      handleError(response, messages);
    });
    
    $scope.$hide();
  };


});

