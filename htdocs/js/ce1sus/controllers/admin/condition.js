/**
 * 
 */

app.controller("conditionController", function($scope, Restangular, messages,
    $log, $routeSegment, conditions) {
  $scope.conditions = conditions;
  
  $scope.$routeSegment = $routeSegment;

});

app.controller('conditionDetailController', function($scope, $routeSegment,$condition, $log, messages, $location) {
  
  $scope.condition = $condition;

  $scope.$routeSegment = $routeSegment;
  
  $scope.setCondition = function(condition){
    $scope.condition = condition;
  };

  
  //scope functions
  $scope.removeCondition = function(){
    //remove user from user list
    $scope.condition.remove().then(function (data) {
      if (data) {
        //remove the selected user and then go to the first one in case it exists
        var index = 0;
        angular.forEach($scope.conditions, function(entry) {
          if (entry.identifier === $scope.condition.identifier){
            $scope.conditions.splice(index, 1);
            if ($scope.conditions.length > 0) {
              $location.path("/admin/condition/"+ $scope.conditions[0].identifier);
            } else {
              $location.path("/admin/condition");
            }
          }
          messages.setMessage({'type':'success','message':'Condition sucessfully removed'});
          index++;
        }, $log);
        
      }
    }, function (response) {
      handleError(response, messages);
    });
  };
});

app.controller("conditionEditController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_condition = angular.copy($scope.condition);

  $scope.closeModal = function(){

    var condition = angular.copy(original_condition);
    $scope.$parent.setCondition(condition);
    $scope.$hide();
    
  };
  //Scope functions
  $scope.resetCondition = function ()
  {
    $scope.condition = angular.copy(original_condition);
    $scope.addConditionForm.$setPristine();
  };
  
  $scope.conditionChanged = function ()
  {
    var result = !angular.equals($scope.condition, original_condition);
    return result;
  };
  
  $scope.submitCondition = function(){
    $scope.condition.modified_on = new Date().getTime();
    $scope.condition.put().then(function (conditiondata) {
      if (conditiondata) {
        $scope.condition = conditiondata;
      }
      messages.setMessage({'type':'success','message':'Condition sucessfully edited'});
    }, function (response) {
      var condition = angular.copy(original_condition);
      $scope.$parent.setCondition(condition);
      handleError(response, messages);
    });
    $scope.$hide();
  };

});

app.controller("conditionAddController",function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_condition = {};
  $scope.condition={};
  
  
  $scope.closeModal = function(){
    $scope.$hide();
  };
  //Scope functions
  $scope.resetCondition = function ()
  {
    $scope.condition = angular.copy(original_condition);
  };
  
  $scope.conditionChanged = function ()
  {
    var result = !angular.equals($scope.condition, original_condition);
    return result;
  };
  
  $scope.submitCondition = function(){
    Restangular.all("condition").post($scope.condition).then(function (data) {
      if (data) {
        $scope.conditions.push(data);
        $location.path("/admin/condition/"+ data.identifier);
      }
      messages.setMessage({'type':'success','message':'Condition sucessfully edited'});
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();

  };
  
});
