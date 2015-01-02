/**
 * 
 */

app.controller("attributeController", function($scope, Restangular, messages,
    $log, $routeSegment, attributes, handlers, tables, types, conditions) {
  
  $scope.attributes = attributes;
  $scope.handlers = handlers;
  $scope.tables = tables;
  $scope.types = types;
  $scope.conditions = conditions;
  
  $scope.$routeSegment = $routeSegment;


});

app.controller("attributeDetailController", function($scope, Restangular, messages,
    $log, $routeSegment, $attribute, objects) {
  
  var identifier = $routeSegment.$routeParams.id;
  
  $scope.attribute = $attribute;
  $scope.objects = objects;

  $scope.$watch(function() {
    return $scope.attribute.default_condition_id;
    }, function(newVal, oldVal) {
      //keep the condition name shown instead the uuid, but only if there are conditions
      if ($scope.conditions.length > 0) {
        angular.forEach($scope.conditions, function(entry) {
          if (entry.identifier === $scope.attribute.default_condition_id){
            $scope.attribute.condition_value = entry.value;
          }
        }, $log);
      }
    });
  
  //scope functions
  $scope.removeAttribute = function(){
    //remove user from user list
    $scope.attribute.remove().then(function (data) {
      if (data) {
        //remove the selected user and then go to the first one in case it exists
        var index = 0;
        angular.forEach($scope.attributes, function(entry) {
          if (entry.identifier === $scope.attributes.identifier){
            $scope.attributes.splice(index, 1);
            if ($scope.users.length > 0) {
              $location.path("/admin/attribute/"+ $scope.attributes[0].identifier);
            } else {
              $location.path("/admin/attribute");
            }
          }
          messages.setMessage({'type':'success','message':'Attribute sucessfully removed'});
          index++;
        }, $log);
        
      }
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };

  $scope.$routeSegment = $routeSegment;
  
  $scope.setAttribute = function(attribute){
    $scope.attribute = attribute;
  };
  
  $scope.$watch(function() {
    return $scope.attribute.table_id;
    }, function(newVal, oldVal) {
      //keep the group name shown instead the uuid, but only if there are groups
      if ($scope.tables.length > 0) {
        angular.forEach($scope.tables, function(entry) {
          if (entry.identifier === $scope.attribute.table_id){
            $scope.attribute.table_name = entry.name;
          }
        }, $log);
      }
    });
  
  $scope.$watch(function() {
    return $scope.attribute.attributehandler_id;
    }, function(newVal, oldVal) {
      //keep the group name shown instead the uuid, but only if there are groups
      if ($scope.handlers.length > 0) {
        angular.forEach($scope.handlers, function(entry) {
          if (entry.identifier === $scope.attribute.attributehandler_id){
            $scope.attribute.attributehandler_name = entry.name;
          }
        }, $log);
      }
    });
  
  $scope.$watch(function() {
    return $scope.attribute.type_id;
    }, function(newVal, oldVal) {
      //keep the group name shown instead the uuid, but only if there are groups
      if ($scope.types.length > 0) {
        angular.forEach($scope.types, function(entry) {
          if (entry.identifier === $scope.attribute.type_id){
            $scope.attribute.type_name = entry.name;
          }
        }, $log);
      }
    });
  
  $scope.addObject = function(){
    $scope.attribute.objects.put();
  };
  $scope.remObject = function(selected){
    
  };
});

app.controller("attributeAddController", function($scope, Restangular, messages,
    $log, $routeSegment, $location) {
  var original_attribute = {};

  $scope.attribute={};
  
  $scope.reset = false;
  //Scope functions
  $scope.resetAttribute = function ()
  {
    $scope.attribute = angular.copy(original_attribute);
    $scope.reset = true;
  };
  
  $scope.resetAttributeCBs = function ()
  {
    $scope.reset = true;
  };
  
  $scope.attributeChanged = function ()
  {
    return !angular.equals($scope.attribute, original_attribute);
  };
  
  $scope.submitAttribute = function(){
    Restangular.all("attributedefinition").post($scope.attribute).then(function (attribute) {
      
      if (data) {
        $scope.attributes.push(data);
        $location.path("/admin/attribute/"+ data.identifier);
      }
      messages.setMessage({'type':'success','message':'Attribute sucessfully added'});
      
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };


  
});

app.controller("attributeEditController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_attribute = angular.copy($scope.attribute);
  
  $scope.closeModal = function(){
    var attribute = angular.copy(original_attribute);
    $scope.$parent.setAttribute(attribute);
    $scope.$hide();

  };
  //Scope functions
  $scope.resetAttribute = function ()
  {
    $scope.attribute = angular.copy(original_attribute);
    $scope.addAttributeForm.$setPristine();
  };
  
  $scope.attributeChanged = function ()
  {
    return !angular.equals($scope.attribute, original_attribute);
  };
  
  $scope.submitAttribute = function(){
    $scope.attribute.put().then(function (data) {
      if (data) {
        $scope.attribute = data;
        //update name in menu
        angular.forEach($scope.attributes, function(entry) {
          if (entry.identifier == data.identifier) {
            entry.name = data.name;
          }
        }, $log);
        messages.setMessage({'type':'success','message':'Attribute sucessfully edited'});
      }
      
    }, function (response) {
      var attribute = angular.copy(original_attribute);
      $scope.$parent.setAttribute(attribute);
      handleError(response, messages);
    });
    $scope.$hide();
  };
  


});



