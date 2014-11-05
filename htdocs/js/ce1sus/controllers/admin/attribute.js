/**
 * 
 */

app.controller("attributeController", function($scope, Restangular, messages,
    $log, $routeSegment) {
  $scope.attribute = {};
  
  $scope.attributes = [];
  
  Restangular.one("attribute").getList(null,{"Complete": false}).then(function (attributes) {
    $scope.attributes = attributes;
  });
  
  Restangular.one("handlers").get(null,{"Complete": false}).then(function (handlers) {
    $scope.handlers = handlers;
  });
  
  Restangular.one("tables").get(null,{"Complete": false}).then(function (tables) {
    $scope.tables = tables;
  });
  
  $scope.$routeSegment = $routeSegment;


});

app.controller("attributeDetailController", function($scope, Restangular, messages,
    $log, $routeSegment) {
  
  var identifier = $routeSegment.$routeParams.id;
  
  $scope.attribute = {};
  Restangular.one("attribute",identifier).get(null,{"Complete": true}).then(function (data) {
    $scope.attribute = data;
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
      $scope.$hide();
    });
  };

  $scope.$routeSegment = $routeSegment;
  

  
});

app.controller("attributeAddController", function($scope, Restangular, messages,
    $log, $routeSegment, $location) {
  var original_attribute = {};

  $scope.attribute={};
  
  //Scope functions
  $scope.resetAttribute = function ()
  {
    $scope.attribute = angular.copy(original_attribute);
  };
  
  $scope.generateAPIKey = function() {
    $scope.attribute.api_key = generateAPIKey();
  };
  
  $scope.attributeChanged = function ()
  {
    return !angular.equals($scope.attribute, original_attribute);
  };
  
  $scope.submitAttribute = function(){
    Restangular.all("attribute").post($scope.attribute).then(function (attribute) {
      
      if (data) {
        $scope.attributes.push(data);
        $location.path("/admin/attribute/"+ data.identifier);
      }
      messages.setMessage({'type':'success','message':'Attribute sucessfully added'});
      
    });
    $scope.$hide();
  };


  
});


