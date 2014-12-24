/**
 * 
 */

app.controller("observableObjectAddController", function($scope, Restangular, messages, $routeSegment,$log) {
  $scope.definitions =[];
  Restangular.one("objectdefinition").getList(null, {"complete": true}).then(function (objects) {
    $scope.definitions = objects;
  }, function(response) {
    handleError(response, messages);
  });
  
  var original_observableObject = {'properties' : {'shared': false},
                                   'definition_id': null};
  $scope.observableObject=angular.copy(original_observableObject);
  
  $scope.$watch(function() {
    return $scope.observableObject.definition_id;
    }, function(newVal, oldVal) {
      angular.forEach($scope.definitions, function(entry) {
        if (entry.identifier === $scope.observableObject.definition_id){
          $scope.observableObject.properties.shared = entry.default_share;
        }
      }, $log);
    });
  
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
    var observableID = $scope.$parent.$parent.observable.identifier;
    Restangular.one('observable', observableID).post('object', $scope.observableObject, {'complete':true, 'infated':true}).then(function (data) {
      $scope.$parent.appendObservableObject(data);
    }, function (response) {
      $scope.observableObject = angular.copy(original_observableObject);
      handleError(response, messages);
    });
    $scope.$hide();
  };


});


app.controller("objectChildAddController", function($scope, Restangular, messages, $routeSegment,$log) {
  $scope.definitions =[];
  Restangular.one("objectdefinition").getList(null, {"complete": false}).then(function (objects) {
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
    var eventID = $routeSegment.$routeParams.id;
    if ($scope.$parent.$parent.object){
      //This is a child object
      $scope.childObject.parent_id=$scope.$parent.$parent.object.identifier;
    }
    var objectID = $scope.$parent.$parent.object.identifier;
    Restangular.one('object', objectID).post('object', $scope.childObject, {'complete':true, 'infated':true}).then(function (data) {
      $scope.$parent.$parent.object.related_objects.push(data);
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };

});

app.controller("observableObjectPropertiesController", function($scope, Restangular, messages, $routeSegment,$log) {
  
  //set the id of the parent
  if (!$scope.object.parent_object_id) {
    $scope.object.parent_object_id = null;
  }
  if ($scope.object.parent_object_id) {
    Restangular.one("observable", $scope.object.observable_id).one("object").getList(null, {"complete": false, "flat": true}).then(function (objects) {
      $scope.objects = objects;
      //remove the object it self
      var index = 0;
      angular.forEach($scope.objects, function(entry) {
        if (entry.identifier == $scope.object.identifier){
          $scope.objects.splice(index,1);
        }

        index++;
      }, $log);
      index = 0;
      /*
      //remove the parent object
      angular.forEach($scope.objects, function(entry) {
        if (entry.identifier == $scope.object.parent_object_id){
          $scope.objects.splice(index,1);
        }

        index++;
      }, $log);
      */
      Restangular.one('relations').getList().then(function(relations) {
        $scope.relations = relations;
      }, function(response) {
        throw generateErrorMessage(response);
      });
    }, function(response) {
        throw generateErrorMessage(response);
    });
  } else {
    $scope.objects = [];
  }
  
  $scope.get_name = function(object){
    if (object.identifier) {
      return object.definition.name + ' - '+object.identifier;
    } else {
      return object.definition.name;
    }
  };

  var original_object = angular.copy($scope.object);
  
  $scope.closeModal = function(){
    $scope.object = angular.copy(original_object);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetObject = function ()
  {
    $scope.object = angular.copy(original_object);

  };
  

  
  $scope.objectChanged = function ()
  {
    return !angular.equals($scope.object, original_object);
  };
  
  $scope.submitObject = function(){
    //restangularize object
    restangularObject = Restangular.restangularizeElement(null, $scope.object, 'object');
    restangularObject.put({'complete':false, 'infated':false}).then(function (data) {
      $scope.$hide();
      $routeSegment.chain[4].reload();
    }, function (response) {
      handleError(response, messages);
      $scope.$hide();
    });
    
  };
});
