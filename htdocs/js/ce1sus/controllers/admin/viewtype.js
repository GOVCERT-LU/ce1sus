/**
 * 
 */

app.controller("viewTypesController", function($scope, Restangular, messages,
    $log, $routeSegment, viewTypes) {
  $scope.viewTypes = viewTypes;
  
  $scope.$routeSegment = $routeSegment;


});

app.controller('viewTypeDetailController', function($scope, $routeSegment,$viewType, $log, messages, $location) {
  
  $scope.viewType = $viewType;
  $scope.$routeSegment = $routeSegment;
  
  $scope.setType = function(viewType){
    $scope.viewType = viewType;
  };
  
  //scope functions
  $scope.removeViewType = function(){
    //remove user from user list
    $scope.viewType.remove().then(function (data) {
      if (data) {
        //remove the selected user and then go to the first one in case it exists
        var index = 0;
        angular.forEach($scope.viewTypes, function(entry) {
          if (entry.identifier === $scope.viewType.identifier){
            $scope.viewTypes.splice(index, 1);
            if ($scope.viewType.length > 0) {
              $location.path("/admin/viewtype/"+ $scope.types[0].identifier);
            } else {
              $location.path("/admin/viewtype");
            }
          }
          messages.setMessage({'type':'success','message':'View Type sucessfully removed'});
          index++;
        }, $log);
        
      }
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };
});

app.controller("viewTypeEditController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_viewType = angular.copy($scope.viewType);

  $scope.closeModal = function(){

    var viewType = angular.copy(original_viewType);
    $scope.$parent.setType(viewType);
    $scope.$hide();
    
  };
  //Scope functions
  $scope.resetType = function ()
  {
    $scope.viewType = angular.copy(original_viewType);
    $scope.addTypeForm.$setPristine();
  };
  
  $scope.viewTypeChanged = function ()
  {
    var result = !angular.equals($scope.viewType, original_viewType);
    return result;
  };
  
  $scope.submitType = function(){
    $scope.viewType.put().then(function (viewTypedata) {
      if (viewTypedata) {
        $scope.viewType = viewTypedata;
      }
      messages.setMessage({'type':'success','message':'View Type sucessfully edited'});
    }, function (response) {
      var viewType = angular.copy(original_viewType);
      $scope.$parent.setType(viewType);
      handleError(response, messages);
    });
    $scope.$hide();
  };

});

app.controller("viewTypeAddController",function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_viewType = {};
  $scope.viewType={};
  
  
  $scope.closeModal = function(){
    $scope.$hide();
  };
  //Scope functions
  $scope.resetType = function ()
  {
    $scope.viewType = angular.copy(original_viewType);
  };
  
  $scope.viewTypeChanged = function ()
  {
    var result = !angular.equals($scope.viewType, original_viewType);
    return result;
  };
  
  $scope.submitType = function(){
    Restangular.all("attribtueviewtypes").post($scope.viewType).then(function (viewTypedata) {
      if (viewTypedata) {
        $scope.viewTypes.push(data);
        $location.path("/admin/viewtype/"+ data.identifier);
      }
      messages.setMessage({'type':'success','message':'View Type sucessfully edited'});
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();

  };
  
});
