/**
 * 
 */

ce1susApp.controller("objectController", function($scope, Restangular, messages,
    $log, $routeSegment) {
  $scope.objects = [];
  
  Restangular.one("object").getList(null,{"Complete": false}).then(function (objects) {
    $scope.objects = objects;
  });
  
  $scope.$routeSegment = $routeSegment;

});

ce1susApp.controller("objectDetailController", function($scope, $injector, Restangular, messages,
    $log, $routeSegment) {
  $scope.object = {};
  $scope.data = getLocals($routeSegment).data;
  var identifier = $routeSegment.$routeParams.id;
  Restangular.one("object",identifier).get(null,{"Complete": true}).then(function(data){
    
    $scope.object = data;
  });
  
  //scope functions
  $scope.removeObject = function(){
    //remove user from user list
    $scope.object.remove().then(function (data) {
      if (data) {
        //remove the selected user and then go to the first one in case it exists
        var index = 0;
        angular.forEach($scope.objects, function(entry) {
          if (entry.identifier === $scope.objects.identifier){
            $scope.objects.splice(index, 1);
            if ($scope.users.length > 0) {
              $location.path("/admin/object/"+ $scope.objects[0].identifier);
            } else {
              $location.path("/admin/object");
            }
          }
          messages.setMessage({'type':'success','message':'Object sucessfully removed'});
          index++;
        }, $log);
        
      }
      $scope.$hide();
    });
  };

  $scope.$routeSegment = $routeSegment;
  

  $scope.start = function() {
    cfpLoadingBar.start();
  };
  $scope.complete = function() {
    cfpLoadingBar.complete();
  };
});

ce1susApp.controller("objectAddController", function($scope, Restangular, messages,
    $log, $routeSegment, $location) {
  var original_object = {};

  $scope.object={};
  
  //Scope functions
  $scope.resetObject = function ()
  {
    $scope.object = angular.copy(original_object);
    $scope.addObjectDefinitionForm.$setPristine();
  };
  
  $scope.generateAPIKey = function() {
    $scope.object.api_key = generateAPIKey();
  };
  
  $scope.objectChanged = function ()
  {
    return !angular.equals($scope.object, original_object);
  };
  
  $scope.submitObject = function(){
    Restangular.all("object").post($scope.object).then(function (object) {
      
      if (data) {
        $scope.objects.push(data);
        $location.path("/admin/object/"+ data.identifier);
      }
      messages.setMessage({'type':'success','message':'Object sucessfully added'});
      
    });
    $scope.$hide();
  };

});


