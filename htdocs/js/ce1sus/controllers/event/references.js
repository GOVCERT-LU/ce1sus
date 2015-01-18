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
      angular.forEach($scope.definitions, function(entry) {
        if (entry.identifier === $scope.reference.definition_id){
          $scope.reference.properties.shared = entry.default_share;
        }
      }, $log);
    });
  
  var original_reference = {'properties' : {'shared': false},
                            'definition_id': null};
  $scope.reference=angular.copy(original_reference);
  
  $scope.$watch(function() {
    return $scope.reference.definition_id;
    }, function(newVal, oldVal) {
      angular.forEach($scope.definitions, function(entry) {
        if (entry.identifier === $scope.reference.definition_id){
          $scope.reference.properties.shared = entry.share;
        }
      }, $log);
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
    angular.forEach($scope.definitions, function(entry) {
      if (entry.identifier == $scope.reference.definition_id){
        $scope.reference.definition=entry;
      }
    }, $log);
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
      angular.forEach($scope.definitions, function(entry) {
        if (entry.identifier === $scope.reference.definition_id){
          $scope.reference.properties.shared = entry.share;
        }
      }, $log);
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
    angular.forEach($scope.definitions, function(entry) {
      if (entry.identifier == $scope.reference.definition_id){
        $scope.reference.definition=entry;
      }
    }, $log);
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

