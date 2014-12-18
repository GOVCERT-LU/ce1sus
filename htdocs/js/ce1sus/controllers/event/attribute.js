/**
 * 
 */
app.controller("objectAttributeAddController", function($scope, Restangular, messages, $routeSegment,$log) {
  $scope.definitions =[];
  Restangular.one("attributedefinition").getList(null,{"complete": true}).then(function (attributes) {
    $scope.definitions = attributes;
  }, function(response) {
      throw generateErrorMessage(response);
  });
  
  var original_attribute = {};
  $scope.attribute={};
  
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
    
    //$scope.$parent.$parChildObjectableObject($scope.attribute);
    $scope.$hide();
  };


});

