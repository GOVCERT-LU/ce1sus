/**
 * 
 */

app.controller("typesController", function($scope, Restangular, messages,
    $log, $routeSegment, types,datatypes) {
  $scope.types = types;
  
  $scope.$routeSegment = $routeSegment;
  $scope.datatypes = datatypes;
  //Add any any
  $scope.datatypes.push({"identifier": null, "name": "Any"});


});

app.controller('typeDetailController', function($scope, $routeSegment,$type, $log, messages) {
  


  $scope.$routeSegment = $routeSegment;
  $scope.type = $type;
  $scope.setType = function(type){
    $scope.type = type;
  };
  
  //scope functions
  $scope.removeType = function(){
    //remove user from user list
    $scope.type.remove().then(function (data) {
      if (data) {
        //remove the selected user and then go to the first one in case it exists
        var index = 0;
        angular.forEach($scope.types, function(entry) {
          if (entry.identifier === $scope.type.identifier){
            $scope.types.splice(index, 1);
            if ($scope.type.length > 0) {
              $location.path("/admin/type/"+ $scope.types[0].identifier);
            } else {
              $location.path("/admin/type");
            }
          }
          messages.setMessage({'type':'success','message':'Type sucessfully removed'});
          index++;
        }, $log);
        
      }
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };
});

app.controller("typeEditController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_type = angular.copy($scope.type);

  $scope.closeModal = function(){

    var type = angular.copy(original_type);
    $scope.$parent.setType(type);
    $scope.$hide();
    
  };
  //Scope functions
  $scope.resetType = function ()
  {
    $scope.type = angular.copy(original_type);
    $scope.addTypeForm.$setPristine();
  };
  
  $scope.typeChanged = function ()
  {
    var result = !angular.equals($scope.type, original_type);
    return result;
  };
  
  $scope.submitType = function(){
    $scope.type.modified_on = new Date().getTime();
    $scope.type.put().then(function (typedata) {
      if (typedata) {
        $scope.type = typedata;
      }
      messages.setMessage({'type':'success','message':'Type sucessfully edited'});
    }, function (response) {
      var type = angular.copy(original_type);
      $scope.$parent.setType(type);
      handleError(response, messages);
    });
    $scope.$hide();
  };

});

app.controller("typeAddController",function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_type = {};
  $scope.type={};
  
  
  $scope.closeModal = function(){
    $scope.$hide();
  };
  //Scope functions
  $scope.resetType = function ()
  {
    $scope.type = angular.copy(original_type);
  };
  
  $scope.typeChanged = function ()
  {
    var result = !angular.equals($scope.type, original_type);
    return result;
  };
  
  $scope.submitType = function(){
    Restangular.all("attributetypes").post($scope.type).then(function (typedata) {
      if (typedata) {
        $scope.types.push(data);
        $location.path("/admin/type/"+ data.identifier);
      }
      messages.setMessage({'type':'success','message':'Type sucessfully edited'});
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();

  };
  
});
