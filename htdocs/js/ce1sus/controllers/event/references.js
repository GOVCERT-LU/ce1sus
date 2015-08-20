/**
 * 
 */

app.controller("reportReferenceAddController", function($scope, Restangular, messages, $routeSegment,$log, $upload) {
  $scope.definitions =[];

  Restangular.one("referencedefinition").getList(null,{"complete": true}).then(function (referenceDefinitions) {
    $scope.definitions = referenceDefinitions;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  
  $scope.$watch(function() {
    return $scope.reference.definition_id;
    }, function(newVal, oldVal) {
      for (var i = 0; i < $scope.definitions.length; i++) {
        if ($scope.definitions[i].identifier === $scope.reference.definition_id){
          $scope.reference.properties.shared = $scope.definitions[i].default_share;
          break;
        }
      }
    });
  
  var original_reference = {'properties' : {'shared': false},
                            'definition_id': null};
  $scope.reference=angular.copy(original_reference);
  
  $scope.$watch(function() {
    return $scope.reference.definition_id;
    }, function(newVal, oldVal) {
      for (var i = 0; i < $scope.definitions.length; i++) {
        if ($scope.definitions[i].identifier === $scope.reference.definition_id){
          $scope.reference.properties.shared = $scope.definitions[i].share;
          break;
        }
      }
    });
  
  $scope.closeModal = function(){
    $scope.reference = angular.copy(original_reference);
    $scope.$hide();
  };
  
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
    for (var i = 0; i < $scope.definitions.length; i++) {
      if ($scope.definitions[i].identifier == $scope.reference.definition_id){
        $scope.reference.definition=$scope.definitions[i];
        break;
      }
    }
    var objectID = $scope.$parent.$parent.report.identifier;
    Restangular.one('report', objectID).post('reference', $scope.reference, {'complete':true, 'infated':true}).then(function (data) {
      $scope.$parent.appendChildren(data);
    }, function (response) {
      $scope.reference = angular.copy(original_reference);
      handleError(response, messages);
    });
    $scope.$hide();
  };


});

app.controller("reportReferenceEditController", function($scope, Restangular, messages, $routeSegment,$log, $upload) {
  $scope.definitions =[];

  Restangular.one("referencedefinition").getList(null,{"complete": true}).then(function (referenceDefinitions) {
    $scope.definitions = referenceDefinitions;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  
  var original_reference = angular.copy($scope.referenceDetails);
  $scope.reference=angular.copy(original_reference);
  
  $scope.$watch(function() {
    return $scope.reference.definition_id;
    }, function(newVal, oldVal) {
      for (var i = 0; i < $scope.definitions.length; i++) {
        if ($scope.definitions[i].identifier === $scope.reference.definition_id){
          $scope.reference.properties.shared = $scope.definitions[i].share;
          break;
        }
      }
    });
  
  $scope.closeModal = function(){
    $scope.reference = angular.copy(original_reference);
    $scope.$hide();
  };
  
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
    for (var i = 0; i < $scope.definitions.length; i++) {
      if ($scope.definitions[i].identifier == $scope.reference.definition_id){
        $scope.reference.definition=$scope.definitions[i];
        break;
      }
    }
    var reportID = $scope.$parent.$parent.report.identifier;
    var restangularReference = Restangular.restangularizeElement(null, $scope.reference, 'report/'+reportID+'/reference');
    restangularReference.put({'complete':true, 'infated':true}).then(function (data) {
      $scope.$parent.updateReference(data);
    }, function (response) {
      $scope.reference = angular.copy(original_reference);
      handleError(response, messages);
    });
    $scope.$hide();
  };
});

