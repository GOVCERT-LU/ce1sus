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
    $log, $routeSegment, $attribute, objects, $location) {
  
  var identifier = $routeSegment.$routeParams.id;
  
  $scope.attribute = $attribute;
  $scope.objects = objects;

  $scope.showBtn = function() {
    return !disableButton($scope.attribute);
  };
  
  $scope.$watch(function() {
    return $scope.attribute.default_condition_id;
    }, function(newVal, oldVal) {
      //keep the condition name shown instead the uuid, but only if there are conditions
      if ($scope.conditions.length > 0) {
        for (var i = 0; i < $scope.conditions.length; i++) {
          if ($scope.conditions[i].identifier === $scope.attribute.default_condition_id){
            $scope.attribute.condition_value = $scope.conditions[i].value;
            break;
          }
        }
      }
    });
  
  //scope functions
  $scope.removeAttribute = function(){
    //remove user from user list
    $scope.attribute.remove().then(function (data) {
      if (data) {
        //remove the selected user and then go to the first one in case it exists
        for (var i = 0; i < $scope.attributes.length; i++) {
          if ($scope.attributes[i].identifier === $scope.attribute.identifier){
            $scope.attributes.splice(i, 1);
            if ($scope.attributes.length > 0) {
              $location.path("/admin/attribute/"+ $scope.attributes[0].identifier);
            } else {
              $location.path("/admin/attribute");
            }
            break;
          }
        }
      }
      messages.setMessage({'type':'success','message':'Attribute sucessfully removed'});
    }, function (response) {
      handleError(response, messages);
    });
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
        for (var i = 0; i < $scope.tables.length; i++) {
          if ($scope.tables[i].identifier === $scope.attribute.table_id){
            $scope.attribute.table_name = $scope.tables[i].name;
            break;
          }
        }
      }
    });
  
  $scope.$watch(function() {
    return $scope.attribute.attributehandler_id;
    }, function(newVal, oldVal) {
      //keep the group name shown instead the uuid, but only if there are groups
      if ($scope.handlers.length > 0) {
        for (var i = 0; i < $scope.handlers.length; i++) {
          if ($scope.handlers[i].identifier === $scope.attribute.attributehandler_id){
            $scope.attribute.attributehandler_name = $scope.handlers[i].name;
            break;
          }
        }
      }
    });
  
  $scope.$watch(function() {
    return $scope.attribute.type_id;
    }, function(newVal, oldVal) {
      //keep the group name shown instead the uuid, but only if there are groups
      if ($scope.types.length > 0) {
        for (var i = 0; i < $scope.types.length; i++) {
          if ($scope.types[i].identifier === $scope.attribute.type_id){
            $scope.attribute.type_name = $scope.types[i].name;
            break;
          }
        }
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
    Restangular.all("attributedefinition").post($scope.attribute).then(function (data) {
      
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

  $scope.closeModal = function(){
    var attribute = angular.copy(original_attribute);
    $scope.$parent.setAttribute(attribute);
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
    $scope.attribute.modified_on = new Date().getTime();
    $scope.attribute.put({'complete':true, 'infated':true}).then(function (data) {
      if (data) {
        $scope.attribute = data;
        //update name in menu
        for (var i = 0; i < $scope.attributes.length; i++) {
          if ($scope.attributes[i].identifier == data.identifier) {
            $scope.attributes[i].name = data.name;
            break;
          }
        }
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



