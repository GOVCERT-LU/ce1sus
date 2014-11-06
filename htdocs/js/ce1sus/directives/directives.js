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
      tables: "=tables",
      types: "=types",
      viewTypes: "=viewtypes",
      reset: "=doreset"
    },
    templateUrl: "pages/common/directives/attributedefinitionform.html",
    controller: function($scope, $log){
      $scope.available_tables = angular.copy($scope.tables);
      $scope.available_types = angular.copy($scope.types);
      $scope.available_viewTypes = angular.copy($scope.viewTypes);
      $scope.available_handlers = angular.copy($scope.handlers);
      
      $scope.handlerChange = function (){

        var handler_id = $scope.attribute.attributehandler_id;
        //keep only the ones usable in the table list
        angular.forEach($scope.handlers, function(itemEntry) {
          if (itemEntry.identifier == handler_id) {
            $scope.available_tables = itemEntry.allowed_tables;
          }
        }, $log);
        // Check if the there was previously an item selected and when check if it sill matches
        if ($scope.attribute.table_id) {
          var found = false;
          angular.forEach($scope.available_tables, function(itemEntry) {
            if (itemEntry.identifier == $scope.attribute.table_id) {
              found = true;
            }
          }, $log);
          if (!found) {
            delete $scope.attribute.table_id;
          }
        }
      };
      $scope.tableChange = function (){
        var table_id = $scope.attribute.table_id;
        newAvailableHandlers = [];
        //keep only the ones usable in the types list
        angular.forEach($scope.handlers, function(itemEntry) {
          angular.forEach(itemEntry.allowed_tables, function(allowed_table) {
            if (allowed_table.identifier == table_id) {
              newAvailableHandlers.push(itemEntry);
            }
          }, $log);
        }, $log);
        $scope.available_handlers = newAvailableHandlers;
        
        //remove the items which do not match
        var found = false;
        if ($scope.attribute.attributehandler_id) {
          found = false;
          angular.forEach($scope.available_handlers, function(itemEntry) {
            if (itemEntry.identifier == $scope.attribute.attributehandler_id) {
              found = true;
            }
          }, $log);
          if (!found) {
            delete $scope.attribute.attributehandler_id;
          }
        }
        
        newTypes = [];
        //keep only the ones usable in handlers list
        angular.forEach($scope.types, function(itemEntry) {
          if (itemEntry.allowed_table.identifier == table_id) {
            newTypes.push(itemEntry);
          }
        }, $log);
        $scope.available_types = newTypes;
        
        //remove the items which do not match
        if ($scope.attribute.type_id) {
          found = false;
          angular.forEach($scope.available_types, function(itemEntry) {
            if (itemEntry.identifier == $scope.attribute.type_id) {
              found = true;
            }
          }, $log);
          if (!found) {
            delete $scope.attribute.type_id;
          }
        }
        
      };
      
      $scope.typeChange = function (){
        

        
      };
      

      

      $scope.$watch('reset', function(newValue, oldValue) {
        //would have preferred to call a function but this also works
        if (newValue) {
          $scope.available_tables = angular.copy($scope.tables);
          $scope.available_types = angular.copy($scope.types);
          $scope.available_viewTypes = angular.copy($scope.viewTypes);
          $scope.available_handlers = angular.copy($scope.handlers);
          
          delete $scope.attribute.viewType_id;
          delete $scope.attribute.table_id;
          delete $scope.attribute.type_id;
          delete $scope.attribute.attributehandler_id;
          $scope.reset=false;
        }
      });
      
    }
  };
});