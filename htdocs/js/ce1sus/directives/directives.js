/**
 * 
 */


app.directive("plainText", function() {
  
  return {
    restrict: "E",
    scope: {
      celsusText: "=text"
    },
    templateUrl: "pages/common/text.html",
    controller: function($scope){
      var tempArray = $scope.celsusText.split('\n');
      var textArray = [];
      angular.forEach(tempArray, function(item) {
        textArray.push({"line": item});
      });

      $scope.preparedCelsusText = textArray;
    }
  };
});

app.directive("userForm", function() {
  
  return {
    restrict: "E",
    scope: {
      user: "=user",
      editMode: "=edit",
      groups: "=groups"
    },
    templateUrl: "pages/common/directives/userform.html"
  };
});

app.directive("groupForm", function() {
  
  return {
    restrict: "E",
    scope: {
      group: "=group",
      editMode: "=edit"
    },
    templateUrl: "pages/common/directives/groupform.html"
  };
});

app.directive("addRemTable", function() {
  
  return {
    restrict: "E",
    scope: {
      title: "=title",
      accociated: "=accociated", //group.children
      allItems: "=all", //groups
      addAction: "=add",
      remAction: "=rem",
      maskedID: "=masked"
    },
    templateUrl: "pages/common/directives/addremtables.html",
    controller: function($scope, $log, $timeout){
      //Split the associdated ones and available ones (definition of remaining)
      $scope.remaining = angular.copy($scope.allItems);
      
      $scope.setRemaining = function() {
        var index = 0;
        angular.forEach($scope.remaining, function(item) {
          // remove selected from the group
          if (item.identifier == $scope.maskedID) {
            $scope.remaining.splice(index, 1);
          } else {
            angular.forEach($scope.accociated, function(associatedEntry) {
              if (item.identifier == associatedEntry.identifier){
                $scope.remaining.splice(index, 1);
              }
            }, $log);
          }
          index++;
        }, $log);
      };
      //wait till the object was rendered
      $timeout($scope.setRemaining);

      $scope.selected_accociated = [];
      $scope.selected_remaining = [];
      
      //make diff of the group and the children
      $scope.addRemTableRemove = function() {
        if (typeof $scope.addAction != "undefined") {
          $scope.addAction($scope.selected_accociated);
        }
        angular.forEach($scope.selected_accociated, function(removedItemId) {
          // remove selected from the group
          var index = 0;
          angular.forEach($scope.accociated, function(associatedEntry) {
            if (removedItemId == associatedEntry.identifier){
              $scope.accociated.splice(index, 1);
            }
            index++;
          }, $log);
          
          //search for the group details
          angular.forEach($scope.allItems, function(itemEntry) {
            if (itemEntry.identifier == removedItemId){
              $scope.remaining.push(itemEntry);
            }
          }, $log);
          
          
        }, $log);
        $scope.selected_accociated = [];
        
      };
        
      $scope.addRemTableAdd = function() {
        if (typeof $scope.remAction != "undefined") {
          $scope.remAction($scope.selected_remaining);
        }
        angular.forEach($scope.selected_remaining, function(addedItemID) {
          // remove selected from the group
          var index = 0;
          angular.forEach($scope.remaining, function(remEntry) {
            if (addedItemID == remEntry.identifier){
              $scope.remaining.splice(index, 1);
            }
            index++;
          }, $log);
          
          //append the selected to the remaining groups
          //check if there are children
          if (!($scope.accociated instanceof Array)) {
            $scope.accociated = [];
          }
          //search for the group details
          angular.forEach($scope.allItems, function(itemEntry) {
            if (itemEntry.identifier == addedItemID){
              $scope.accociated.push(itemEntry);
            }
          }, $log);
          
          
        }, $log);

      };
    }
  };
});

app.directive("objectDefinitionForm", function() {
  
  return {
    restrict: "E",
    scope: {
      object: "=object",
      editMode: "=edit"
    },
    templateUrl: "pages/common/directives/objectdefinitionform.html"
  };
});

app.directive("attributeDefinitionForm", function() {
  
  return {
    restrict: "E",
    scope: {
      attribute: "=attribute",
      editMode: "=edit",
      handlers: "=handlers",
      tables: "=tables"
    },
    templateUrl: "pages/common/directives/attributedefinitionform.html",
    controller: function($scope, $log){
      $scope.available_types = angular.copy($scope.tables);
      
      $scope.handlerChange = function (){

        var handler_id = $scope.attribute.attributehandler_id;
        var handler = null;
        //keep only the ones usable in the list
        angular.forEach($scope.handlers, function(itemEntry) {
          if (itemEntry.identifier == handler_id) {
            $scope.available_types = itemEntry.allowed_tables;
          }
        }, $log);
        
      };
    }
  };
});