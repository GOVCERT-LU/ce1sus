/**
 * 
 */


app.directive("plainText", function() {
  
  return {
    restrict: "E",
    scope: {
      celsusText: "@text"
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
      editMode: "@edit",
      groups: "@groups"
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
      title: "@title",
      foo: "=foo", //group.children
      allItems: "=all", //groups
      route: "@route",
      owner: "=owner"
    },
    templateUrl: "pages/common/directives/addremtables.html",
    controller: function($scope, $log, $timeout, Restangular, messages){
      //Split the associdated ones and available ones (definition of remaining)
      $scope.remaining = angular.copy($scope.allItems);
      if ($scope.foo) {
        $scope.associated = $scope.foo;
      } else {
        $scope.associated = [];
      }
      $scope.setRemaining = function() {
        var index = 0;
        var items_to_remove = [];
        angular.forEach($scope.remaining, function(item) {
          // remove selected from the group
          if (item.identifier == $scope.owner.identifier) {
            items_to_remove.push(index);
          } else {
            if ($scope.associated.length > 0) {
              angular.forEach($scope.associated, function(associatedEntry) {
                var id1 = associatedEntry.identifier;
                var id2 = item.identifier;
                if (id1.toLowerCase() == id2.toLowerCase()){
                  items_to_remove.push(index);
                  
                }
                
              }, $log);
            } else {
              //restangularize object
              $scope.associated =  [];
            }
          }
          index++;
        }, $log);
        //sort array from big to log
        items_to_remove = items_to_remove.reverse();
        angular.forEach(items_to_remove, function(index){
          $scope.remaining.splice(index, 1);
        });
      };
      //wait till the object was rendered
      $timeout($scope.setRemaining);

      $scope.selected_accociated = [];
      $scope.selected_remaining = [];
      var original_associated = angular.copy($scope.associated);
      //make diff of the group and the children
      $scope.addRemTableRemove = function() {
        angular.forEach($scope.selected_accociated, function(removedItemId) {
          // remove selected from the group
          var index = 0;
          angular.forEach($scope.associated, function(associatedEntry) {
            if (removedItemId == associatedEntry.identifier){
              
              $scope.associated.splice(index, 1);
              Restangular.one($scope.owner.route, $scope.owner.identifier).one($scope.route, removedItemId).remove().then(function (item) {
                if (item) {
                  messages.setMessage({'type':'success','message':'Item sucessfully removed'});
                } else {
                  messages.setMessage({'type':'danger','message':'Unkown error occured'});
                }
                $scope.selected_accociated = [];
                $scope.selected_remaining = [];
              }, function (response) {
                $scope.remaining = angular.copy($scope.allItems);
                $scope.associated = original_associated;
                $scope.setRemaining();
                
                handleError(response, messages);
              });
              
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
      };
      
      $scope.addRemTableAdd = function() {
        var original_associated = angular.copy($scope.associated);
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
          //search for the group details
          
          angular.forEach($scope.allItems, function(itemEntry) {
            if (itemEntry.identifier == addedItemID){
              
              
              $scope.associated.push(itemEntry);
              //derestangularize the element
              //foo as the owner is modified 
              Restangular.one($scope.owner.route, $scope.owner.identifier).all($scope.route).post({'identifier':itemEntry.identifier,'name':itemEntry.name}).then(function (item) {
                if (item) {
                  messages.setMessage({'type':'success','message':'Item sucessfully associated'});
                } else {
                  
                  messages.setMessage({'type':'danger','message':'Unkown error occured'});
                }
                $scope.selected_accociated = [];
                $scope.selected_remaining = [];
              }, function (response) {
                $scope.remaining = angular.copy($scope.allItems);
                $scope.associated = original_associated;
                $scope.setRemaining();
                
                handleError(response, messages);
              });
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