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
        var index = 0;
        angular.forEach($scope.objects, function(entry) {
          if (entry.identifier === $scope.object.identifier){
            $scope.objects.splice(index, 1);
            if ($scope.objects.length > 0) {
              $location.path("/admin/object/"+ $scope.objects[0].identifier);
            } else {
              $location.path("/admin/object");
            }
          }
          
          index++;
        }, $log);
        messages.setMessage({'type':'success','message':'Object sucessfully removed'});
      }
    }, function (response) {
      handleError(response, messages);
    });
  };

  $scope.$routeSegment = $routeSegment;
  
  $scope.setObject = function(object){
    $scope.object = object;
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
      messages.setMessage({'type':'success','message':'Object sucessfully added'});
      
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
    $scope.object.modified_on = new Date().getTime();
    $scope.object.put({'complete':true, 'infated':true}).then(function (data) {
      if (data) {
        //update username in case
        angular.forEach($scope.objects, function(entry) {
          if (entry.identifier === data.identifier){
            entry.name = data.name;
          }
        }, $log);
        $scope.$parent.setObject(data);
      }
      messages.setMessage({'type':'success','message':'Object sucessfully edited'});
    }, function (response) {
      var object = angular.copy(original_object);
      $scope.$parent.setObject(object);
      handleError(response, messages);
    });
    $scope.$hide();
  };
});

