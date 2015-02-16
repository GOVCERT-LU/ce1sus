/**
 * 
 */
app.controller("objectAttributeAddController", function($scope, Restangular, messages, $routeSegment,$log, $upload) {
  $scope.definitions =[];

  Restangular.one("objectdefinition", $scope.object.definition.identifier).getList("attributes",{"complete": true}).then(function (attributes) {
    $scope.definitions = attributes;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  Restangular.one("condition").getList(null, {"complete": false}).then(function (conditions) {
    $scope.conditions = conditions;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  
  $scope.$watch(function() {
    return $scope.attribute.definition_id;
    }, function(newVal, oldVal) {
      angular.forEach($scope.definitions, function(entry) {
        if (entry.identifier === $scope.attribute.definition_id){
          $scope.attribute.properties.shared = entry.default_share;
          $scope.attribute.condition_id = entry.default_condition_id;
        }
      }, $log);
    });
  
  var original_attribute = {'properties' : {'shared': false},
                            'definition_id': null};
  $scope.attribute=angular.copy(original_attribute);
  
  $scope.closeModal = function(){
    $scope.attribute = angular.copy(original_attribute);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetAttribute = function ()
  {
    $scope.attribute = angular.copy(original_attribute);

  };
  

  
  $scope.attributeChanged = function ()
  {
    return !angular.equals($scope.attribute, original_attribute);
  };
  
  $scope.submitAttribute = function(){
    angular.forEach($scope.definitions, function(entry) {
      if (entry.identifier == $scope.attribute.definition_id){
        $scope.attribute.definition=entry;
      }
    }, $log);
    var objectID = $scope.$parent.$parent.object.identifier;
    Restangular.one('object', objectID).post('attribute', $scope.attribute, {'complete':true, 'infated':true}).then(function (data) {
      $scope.$parent.appendChildren(data);
    }, function (response) {
      $scope.attribute = angular.copy(original_attribute);
      handleError(response, messages);
    });
    $scope.$hide();
  };


});

app.controller("objectAttributeEditController", function($scope, Restangular, messages, $routeSegment,$log, $upload) {
  $scope.definitions =[];
  
  var original_attribute = angular.copy($scope.attributeDetails);
  $scope.attribute=angular.copy(original_attribute);

  Restangular.one("objectdefinition", $scope.object.definition.identifier).getList("attributes",{"complete": true}).then(function (attributes) {
    $scope.definitions = attributes;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  Restangular.one("condition").getList(null, {"complete": false}).then(function (conditions) {
    $scope.conditions = conditions;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  $scope.closeModal = function(){
    $scope.attribute = angular.copy(original_attribute);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetAttribute = function ()
  {
    $scope.attribute = angular.copy(original_attribute);

  };

  $scope.attributeChanged = function ()
  {
    return !angular.equals($scope.attribute, original_attribute);
  };
  

  
  

  
  $scope.submitAttribute = function(){
    angular.forEach($scope.definitions, function(entry) {
      if (entry.identifier == $scope.attribute.definition_id){
        $scope.attribute.definition=entry;
      }
    }, $log);
    var objectID = $scope.$parent.$parent.object.identifier;
    var restangularAttribute = Restangular.restangularizeElement(null, $scope.attribute, 'object/'+objectID+'/attribute');
    restangularAttribute.put({'complete':true, 'infated':true}).then(function (data) {
      $scope.$parent.updateAttribute(data);
    }, function (response) {
      $scope.attribute = angular.copy(original_attribute);
      handleError(response, messages);
    });
    $scope.$hide();
  };

  
});