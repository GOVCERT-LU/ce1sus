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
app.controller("composedObservableAddController", function($scope, Restangular, messages, $routeSegment,$location) {
  var original_observable = {'properties' : {'shared': true}};
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
    parentObservable = $scope.$parent.$parent.composedobservable;
    Restangular.one('observable', parentObservable.identifier).post('observable', $scope.observable, {'complete':true, 'infated':true}).then(function (data) {
      $scope.$parent.$parent.composedobservable.observable_composition.observables.push(data);
    }, function (response) {
      $scope.observable = angular.copy(original_observable);
      handleError(response, messages);
    });
    $scope.$hide();
  };


});
app.controller("composedObservableEditController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_observable = angular.copy($scope.composedobservable);
  $scope.working_copy = angular.copy($scope.composedobservable);
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
      //find the observable in context and replace it
      var index = -1;
      var counter = 0;
      if ($scope.$parent.$parent.$parent.$parent.$parent.observables) {
        angular.forEach($scope.$parent.$parent.$parent.$parent.$parent.observables, function(item) {
          if (item.identifier == restangularObservable.identifier){
            index = counter;
          }
          counter++;
        },$log);
      }
      $scope.$parent.$parent.$parent.$parent.$parent.observables[index] = restangularObservable;
      

      
      
    }, function (response) {
      $scope.composedobservable = angular.copy(original_observable);
      handleError(response, messages);
    });
    
    $scope.$hide();
  };


});
