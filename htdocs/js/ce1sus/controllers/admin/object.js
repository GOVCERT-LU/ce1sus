/**
 * 
 */

app.controller("objectController", function($scope, Restangular, messages,
    $log, $routeSegment, objects) {
  $scope.objects = objects;
  $scope.$routeSegment = $routeSegment;

});

app.controller("objectDetailController", function($scope, $injector, Restangular, messages,
    $log, $routeSegment, $object, attributes, $location) {
  $scope.object = $object;
  $scope.attributes = attributes;
  
  $scope.showBtn = function() {
    return !disableButton($scope.object);
  };
  
  //scope functions
  $scope.removeObject = function(){
    //remove user from user list
    $scope.object.remove().then(function (data) {
      if (data) {
        //remove the selected user and then go to the first one in case it exists
        for (var i = 0; i < $scope.objects.length; i++) {
          if ($scope.objects[i].identifier === $scope.object.identifier){
            $scope.objects.splice(i, 1);
            if ($scope.objects.length > 0) {
              $location.path("/admin/object/"+ $scope.objects[0].identifier);
            } else {
              $location.path("/admin/object");
            }
            break;
          }
        }
        messages.setMessage({"type":"success","message":"Object sucessfully removed"});
      }
    }, function (response) {
      handleError(response, messages);
    });
  };
  
  $scope.setObject = function(object){
    $scope.object = object;
  };
  
  $scope.multiple = false;
  
  $scope.allItems = $scope.objects;
  var original_values = {};
  
  $scope.associated = $scope.object.objects;
  
  $scope.options = {"list_type": false};
  
  $scope.remaining = angular.copy($scope.allItems);
  
  if (!$scope.associated){
    $scope.associated =[];
  }

  $scope.objectChanged = function ()
  {
    return !angular.equals($scope.object.objects, original_values);
  };
  
  $scope.$watch(function() {
    return $scope.associated;
  }, function(newVal, oldVal) {
    setRemaining();
  });

  function setRemaining() {
    var items_to_remove = [];
    for (var i = 0; i < $scope.remaining.length; i++) {
      // remove selected from the group
      if ($scope.associated) {
        for (var j = 0; j < $scope.associated.length; j++) {
          if ($scope.associated[j].definition.identifier === $scope.remaining[i].identifier){
            items_to_remove.push(i);
            break;
          }
        }
      } else {
        $scope.associated =  [];
      }
      //remove it's own definition
      if ($scope.remaining[i].identifier == $scope.object.identifier) {
        items_to_remove.push(i);
      }
    }
    //sort array that the values are from big to low as the $scope.remaining array is shrinking
    items_to_remove = items_to_remove.reverse();
    for (var k = 0; k < items_to_remove.length; k++) {
      var index = items_to_remove[k];
      $scope.remaining.splice(index, 1);
    }
  }
  
  $scope.selected_accociated = [];
  $scope.selected_remaining = [];
  var original_associated = angular.copy($scope.associated);
  
  function add_item(addedObject, options) {
    var child_obj = {"definition": {"identifier":addedObject.identifier,"name":addedObject.name}, "properties": options};
    Restangular.one("objectdefinition", $scope.object.identifier).all("object").post(child_obj).then(function (item) {
      if (item) {
        messages.setMessage({"type":"success","message":"Item sucessfully associated"});
      } else {
        
        messages.setMessage({"type":"danger","message":"Unkown error occured"});
      }
      $scope.associated.push(child_obj);
      
      $scope.selected_accociated = [];
      $scope.selected_remaining = [];
    }, function (response) {
      $scope.remaining = angular.copy($scope.allItems);
      $scope.associated = original_associated;
      
      handleError(response, messages);
    });
  }
  
  $scope.objectAdd = function() {
    var original_associated = angular.copy($scope.associated);
    for (var i = 0; i < $scope.selected_remaining.length; i++) {
      // remove selected from the group
      for (var j = 0; j < $scope.remaining.length; j++) {
        if ($scope.selected_remaining[i] == $scope.remaining[j].identifier){
          $scope.remaining.splice(j, 1);
        }
      }
      
      //append the selected to the remaining groups
      //check if there are children
      //search for the group details
      for (var k = 0; k < $scope.allItems.length; k++) {
        if ($scope.allItems[k].identifier == $scope.selected_remaining[i]){
          
          
          //derestangularize the element
          if ($scope.selected_remaining.length == 1) {
            options = $scope.options;
          } else {
            options = {"list_type": false};
          }
          add_item($scope.allItems[k], options);
        }
      }
    }
    $scope.permissions = {};
    $scope.selected_accociated = [];
    $scope.selected_remaining = [];
  };
  
  function remove_item(restangularOption){
    restangularOption.remove().then(function (item) {
      if (item) {
        messages.setMessage({"type":"success","message":"Item sucessfully removed"});
      } else {
        messages.setMessage({"type":"danger","message":"Unkown error occured"});
      }
      $scope.selected_accociated = [];
      $scope.selected_remaining = [];
    }, function (response) {
      $scope.remaining = angular.copy($scope.allItems);
      $scope.associated = original_associated;
      
      handleError(response, messages);
    });

  }
  
  
  $scope.objectRemove = function() {
    for (var i = 0; i < $scope.selected_accociated.length; i++) {
      // remove selected from the group
      for (var j = 0; j < $scope.associated.length; j++) {
        if ($scope.selected_accociated[i] == $scope.associated[j].identifier){
          restangularOption = Restangular.restangularizeElement($scope.object, $scope.associated[j], "object");
          $scope.associated.splice(j, 1);
          remove_item(restangularOption);
          break;
        }
      }
      
      //search for the group details
      for (var k = 0; k < $scope.allItems.length; k++) {
        if ($scope.allItems[k].identifier == $scope.selected_accociated[i]){
          $scope.remaining.push($scope.allItems[k]);
        }
      }
    }
  };
  
  $scope.setOptions = function(){
    $scope.selected_remaining = [];
    if ($scope.selected_accociated.length == 1){
      //Get Permissions from selected
      for (var i = 0; i < $scope.associated.length; i++) {
        $scope.multiple = false;
        if ($scope.associated[i].identifier == $scope.selected_accociated[0]) {
          $scope.options = angular.copy($scope.associated[i].options);
          break;
        }
      }
      
    } else {
      $scope.multiple = true;
    }
  };
  
  $scope.setRemOptions = function(){
    $scope.options.list_type = false;
    $scope.selected_accociated = [];
  };
  
  function sumbit_changes(child){
    var restangularChild = Restangular.restangularizeElement($scope.object, child, 'object');
    restangularChild.put().then(function (data) {
      if (data){
        messages.setMessage({'type':'success','message':'Child sucessfully edited'});
        //update group in browser
        for (var i = 0; i < $scope.associated.length; i++) {
          $scope.multiple = false;
          if ($scope.associated[i].group.identifier == $scope.selected_accociated[0]) {
            $scope.associated[i] = data;
            break;
          }
        }
      } else {
        messages.setMessage({'type':'danger','message':'An unexpected error occured'});
      }
      
    }, function (response) {
      $scope.comment = angular.copy(original_comment);
      handleError(response, messages);
    });
  }
  
  $scope.submitChanges = function(){
    for (var i = 0; i < $scope.associated.length; i++) {
      $scope.multiple = false;
      if ($scope.associated[i].identifier == $scope.selected_accociated[0]) {
        child = $scope.associated[i];
        child.properties = $scope.options;
        setModified(child);
        sumbit_changes(child);
        break;
      }
    }
  };
  
});

app.controller("objectAddController", function($scope, Restangular, messages,
    $log, $routeSegment, $location) {
  var original_object = {};

  $scope.object={};
  
  //Scope functions
  $scope.resetObject = function ()
  {
    $scope.object = angular.copy(original_object);
    $scope.addObjectDefinitionForm.$setPristine();
  };
  
  $scope.objectChanged = function ()
  {
    return !angular.equals($scope.object, original_object);
  };
  
  $scope.submitObject = function(){
    Restangular.all("objectdefinition").post($scope.object).then(function (object) {
      
      if (object) {
        $scope.objects.push(object);
        $location.path("/admin/object/"+ object.identifier);
      }
      messages.setMessage({"type":"success","message":"Object sucessfully added"});
      
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };
  
  $scope.$routeSegment = $routeSegment;
  $scope.setObject = function(object){
    $scope.object = object;
  };
});

app.controller("objectEditController", function($scope, Restangular, messages, $routeSegment,$location,  $log) {
  var original_object = angular.copy($scope.object);

  
  //Scope functions
  $scope.resetUser = function ()
  {
    $scope.object = angular.copy(original_object);
  };
  
  $scope.closeModal = function(){
    var object = angular.copy(original_object);
    $scope.$parent.setObject(object);
    $scope.$hide();
  };
  
  $scope.objectChanged = function ()
  {
    var result = !angular.equals($scope.object, original_object);
    return result;
  };
  
  $scope.submitObject = function(){
    $scope.object.put({"complete":true, "infated":true}).then(function (data) {
      if (data) {
        for (var i = 0; i < $scope.objects.length; i++) {
          if ($scope.objects[i].identifier === data.identifier){
            $scope.objects[i].name = data.name;
            break;
          }
        }
        $scope.$parent.setObject(data);
      }
      messages.setMessage({"type":"success","message":"Object sucessfully edited"});
    }, function (response) {
      var object = angular.copy(original_object);
      $scope.$parent.setObject(object);
      handleError(response, messages);
    });
    $scope.$hide();
  };
});

