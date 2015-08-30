/**
 * 
 */


app.directive("plainText", function() {
  
  return {
    restrict: "E",
    scope: {
      celsusText: "=text",
      ignoreEmptyLines: "=ignoreEmptyLines"
    },
    templateUrl: "pages/common/text.html",
    controller: function($scope, $log){
      var tempArray = $scope.celsusText.split('\n');
      var textArray = [];
      for (var i = 0; i < tempArray.length; i++) {
        textArray.push({"line": tempArray[i]});
      }
      $scope.preparedCelsusText = textArray;
    }
  };
});

app.directive("userForm", function() {
  
  return {
    restrict: "E",
    scope: {
      user: "=user",
      type: "=type",
      groups: "=groups"
    },
    templateUrl: "pages/common/directives/userform.html",
    controller: function($scope){
      $scope.generateAPIKey = function() {
        $scope.user.api_key = generateAPIKey();
      };

      $scope.setModified = setModified;
    }
  };
});

app.directive("groupForm", function() {
  
  return {
    restrict: "E",
    scope: {
      group: "=group",
      editMode: "=edit",
      tlps: "=tlps"
    },
    controller: function($scope, $log){
      $scope.setModified = setModified;
    },
    templateUrl: "pages/common/directives/groupform.html"
  };
});

app.directive("addRemTable", function() {
  
  return {
    restrict: "E",
    scope: {
      title: "@title",
      allItems: "=all", //groups
      route: "@route",
      owner: "=owner",
      associated: "=associated"
    },
    templateUrl: "pages/common/directives/addremtables.html",
    controller: function($scope, $log, $timeout, Restangular, messages){
      //Split the associdated ones and available ones (definition of remaining)
      $scope.remaining = angular.copy($scope.allItems);
      
      if (!$scope.associated){
        $scope.associated =[];
      }

      $scope.$watch(function() {
        return $scope.associated;
      }, function(newVal, oldVal) {
        setRemaining();
      });
      
      function setRemaining() {
        var items_to_remove = [];
        for (var i = 0; i < $scope.remaining.length; i++) {
          // remove selected from the group
          if ($scope.remaining[i].identifier === $scope.owner.identifier) {
            items_to_remove.push(i);
          } else {
            if ($scope.associated) {
              for (var j = 0; j < $scope.associated.length; j++) {
                if ($scope.associated[j].identifier === $scope.remaining[i].identifier){
                  items_to_remove.push(i);
                  break;
                }
              }
            } else {
              //restangularize object
              $scope.associated =  [];
            }
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
      //make diff of the group and the children
      
      function remove_item(selected_associated){
        Restangular.one($scope.owner.route, $scope.owner.identifier).one($scope.route, selected_associated).remove().then(function (item) {
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
          
          handleError(response, messages);
        });
      }
      
      
      $scope.addRemTableRemove = function() {
        for (var i = 0; i < $scope.selected_accociated.length; i++) {
          // remove selected from the group
          for (var j = 0; j < $scope.associated.length; j++) {
            if ($scope.selected_accociated[i] == $scope.associated[j].identifier){
              $scope.associated.splice(j, 1);
              remove_item($scope.selected_accociated[i]);
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
      
      $scope.disableBtn = function() {
        return disableButton($scope.owner);
      };

      function add_item(added_group) {
        Restangular.one($scope.owner.route, $scope.owner.identifier).all($scope.route).post({'identifier':added_group.identifier,'name':added_group.name}).then(function (item) {
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
          
          handleError(response, messages);
        });
      }
      
      $scope.addRemTableAdd = function() {
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
              
              $scope.associated.push($scope.allItems[k]);
              //derestangularize the element
              add_item($scope.allItems[k]);
            }
          }
          
        }
        
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
    templateUrl: "pages/common/directives/objectdefinitionform.html",
    controller: function($scope, $log){
      $scope.setModified = setModified;
    }
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
      reset: "=doreset",
      conditions: "=conditions"
    },
    templateUrl: "pages/common/directives/attributedefinitionform.html",
    controller: function($scope, $log){
      $scope.available_tables = angular.copy($scope.tables);
      $scope.available_types = angular.copy($scope.types);
      $scope.available_handlers = angular.copy($scope.handlers);
      
      $scope.handlerChange = function (){

        var handler_id = $scope.attribute.attributehandler_id;
        //keep only the ones usable in the table list
        for (var i = 0; i < $scope.handlers.length; i++) {
          if ($scope.handlers[i].identifier == handler_id) {
            $scope.available_tables = $scope.handlers[i].allowed_tables;
            break;
          }
        }
        // Check if the there was previously an item selected and when check if it sill matches
        if ($scope.attribute.table_id) {
          var found = false;
          for (var j = 0; j < $scope.available_tables.length; j++) {
            if ($scope.available_tables[j].identifier == $scope.attribute.table_id) {
              found = true;
              break;
            }
          }
          if (!found) {
            delete $scope.attribute.table_id;
          }
        }
        $scope.setModified($scope.attribute);
      };
      $scope.tableChange = function (){
        var table_id = $scope.attribute.table_id;
        newAvailableHandlers = [];
        //keep only the ones usable in the types list
        for (var i = 0; i < $scope.handlers.length; i++) {
          for (var j = 0; j < $scope.handlers[j].allowed_tables.length; j++) {
            if ($scope.handlers[i].allowed_tables[j].identifier == table_id) {
              newAvailableHandlers.push($scope.handlers[i]);
            }
          }
        }
        $scope.setModified($scope.attribute);
        $scope.available_handlers = newAvailableHandlers;
        
        //remove the items which do not match
        var found = false;
        if ($scope.attribute.attributehandler_id) {
          found = false;
          for (var k = 0; k < $scope.available_handlers.length; k++) {
            if ($scope.available_handlers[k].identifier == $scope.attribute.attributehandler_id) {
              found = true;
              break;
            }
          }
          if (!found) {
            delete $scope.attribute.attributehandler_id;
          }
        }
        
        newTypes = [];
        //keep only the ones usable in handlers list
        for (var l = 0; l < $scope.types.length;l++) {
          if ($scope.types[i].allowed_table.identifier == table_id) {
            newTypes.push($scope.types[l]);
          } else {
            if (itemEntry.allowed_table.name == 'Any') {
              newTypes.push($scope.types[l]);
            }
          }
        }
        $scope.available_types = newTypes;
        
        //remove the items which do not match
        if ($scope.attribute.type_id) {
          found = false;
          for (var m = 0; m < $scope.available_types.length; m++) {
            if ($scope.available_types[m].identifier == $scope.attribute.type_id) {
              found = true;
              break;
            }
          }
          if (!found) {
            delete $scope.attribute.type_id;
          }
        }
        
      };
      
      $scope.typeChange = function (){
        $scope.setModified($scope.attribute);

        
      };
      

      

      $scope.$watch('reset', function(newValue, oldValue) {
        //would have preferred to call a function but this also works
        if (newValue) {
          $scope.available_tables = angular.copy($scope.tables);
          $scope.available_types = angular.copy($scope.types);
          $scope.available_handlers = angular.copy($scope.handlers);

          delete $scope.attribute.table_id;
          delete $scope.attribute.type_id;
          delete $scope.attribute.attributehandler_id;
          $scope.reset=false;
        }
      });
      
      $scope.setModified = setModified;
      
    }
  };
});

app.directive("referenceDefinitionForm", function() {
  
  return {
    restrict: "E",
    scope: {
      reference: "=reference",
      type: "=type",
      handlers: "=handlers"
    },
    templateUrl: "pages/common/directives/referencedefinitionform.html",
    controller: function($scope, $log){
      $scope.setModified = setModified;
    }
  };
});

app.directive("typeForm", function() {
  
  return {
    restrict: "E",
    scope: {
      type: "=type",
      datatypes: "=datatypes",
      editMode: "=edit"
    },
    templateUrl: "pages/common/directives/typeform.html",
    controller: function($scope, $log){
      $scope.setModified = setModified;
    }
  };
});


app.directive("conditionForm", function() {
  
  return {
    restrict: "E",
    scope: {
      condition: "=condition",
      type: "=type"
    },
    templateUrl: "pages/common/directives/conditionform.html",
    controller: function($scope, $log){
      $scope.setModified = setModified;
    }
  };
});

app.directive("composedobservable", function($compile) {
  
  return {
    restrict: "E",
    replace: true,
    transclude: true,
    scope: {
      composedobservable: "=composedobservable",
      indent: "=indent",
      permissions: "=permissions"
    },
    controller: function($scope, Pagination, $modal, $routeSegment, Restangular, messages){
      $scope.pagination = Pagination.getNew(5,'composedobservable.observable_composition');
      $scope.pagination.numPages = Math.ceil($scope.composedobservable.observable_composition.observables.length/$scope.pagination.perPage);
      $scope.pagination.setPages();
      
      
      
      $scope.removeComposedObservable = function() {
        var remove = false;
        if (confirm('Are you sure you want to delete this composed observable?')) {
          if ($scope.composedobservable.observable_composition.observables.length > 0) {
            remove = confirm('Are you sure you want also it\'s children?');
          } else {
            remove = true;
          }
        }
        if (remove) {
          var eventID = $routeSegment.$routeParams.id;
          

          restangularObservable = Restangular.restangularizeElement(null, $scope.composedobservable, 'event/'+eventID+'/observable');
          restangularObservable.remove().then(function (data) {
            //find a way to make this more neat see $parent
            var index = $scope.$parent.observables.indexOf($scope.composedobservable);
            $scope.$parent.observables.splice(index,1);
            messages.setMessage({'type':'success','message':'Observable sucessfully removed'});
          }, function (response) {
            handleError(response, messages);
          });
          
        }
      };
      
      $scope.addObservable = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/addChild.html', show: true});
      };
      
      $scope.getTitle = function(){
        if ($scope.composedobservable.title){
          return $scope.composedobservable.title;
        } else {
          return 'Composed observable';
        }
        
      };
      
      $scope.appendObservable =  function(observable){
        $scope.composedobservable.observable_composition.observables.push(observable);
      };
      
      $scope.showDetails = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/composeddetails.html', show: true});
      };
      $scope.editComposedObservable = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/composededit.html', show: true});
      };
      
      $scope.addChildObservable = function(){
        alert('Hello');
      };

      $scope.setModified = setModified;

    },
    templateUrl: "pages/common/directives/composendobservableview.html",
    compile: function (element) {
      var contents = element.contents().remove();
      var compiled;
      return function(scope,element){
        if(!compiled)
            compiled = $compile(contents);
        
        compiled(scope,function(clone){
          element.append(clone);
            
        });
      };
    },
  };
});

app.directive("indicator", function($compile) {
  return {
    restrict: "E",
    replace: true,
    transclude: true,
    scope: {
      indicator: "=indicator",
      indent: "=indent",
      permissions: "=permissions"
    },
    controller: function($scope, $modal, $log, messages, Restangular, $routeSegment){

      $scope.getTitle = function(indicator){
        if (indicator.title){
          return indicator.title;
        } else {
          return "Indicator";
        }
      };
      
      $scope.showDetails = function(){
        $modal({scope: $scope, template: 'pages/events/event/indicator/details.html', show: true});
      };

      $scope.setModified = setModified;

    },
    templateUrl: "pages/common/directives/indicatorview.html",
    compile: function(tElement, tAttr, transclude) {
      var contents = tElement.contents().remove();
      var compiledContents;
      return function(scope, iElement, iAttr) {

          if(!compiledContents) {
              compiledContents = $compile(contents, transclude);
          }
          compiledContents(scope, function(clone, scope) {
                   iElement.append(clone); 
          });
      };
    }
  };
});

app.directive("observable", function($compile) {
  
  return {
    restrict: "E",
    replace: true,
    transclude: true,
    scope: {
      observable: "=observable",
      indent: "=indent",
      permissions: "=permissions"
    },
    controller: function($scope, $modal, $log, messages, Restangular, $routeSegment){
      
      
      
      $scope.getTitle = function(observable){
        if (observable.title){
          return observable.title;
        } else {
          return "Observable";
        }
      };
      
      $scope.editObservable = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/edit.html', show: true});
      };
      
      $scope.setObservable = function(observable){
        var index = -1;
        if ($scope.$parent.$parent.$parent.composedobservable) {
          index = $scope.$parent.$parent.$parent.composedobservable.observable_composition.observables.indexOf($scope.observable);
          $scope.$parent.$parent.$parent.composedobservable.observable_composition.observables[index] = observable;
        } else {
          //belongs to root
          index = 0;
          for (var i = 0; i < $scope.$parent.$parent.$parent.$parent.observables.length; i++) {
            if ($scope.$parent.$parent.$parent.$parent.observables[i].identifier == observable.identifier) {
              $scope.$parent.$parent.$parent.$parent.observables[i] = observable;
              break;
            }
          }
        }
      };
      
      $scope.removeObservable = function(){
        if (confirm('Are you sure you want to delete?')) {
          var index = -1;
          eventID = $routeSegment.$routeParams.id;
          restangularObservable = Restangular.restangularizeElement(null, $scope.observable, 'event/'+eventID+'/observable');
          restangularObservable.remove().then(function (data) {
            
            if ($scope.$parent.$parent.$parent.composedobservable) {
              //TODO: find a way to do this more neatly see $parent.$parent.$parent, perhaps this changes!?
              index = $scope.$parent.$parent.$parent.composedobservable.observable_composition.observables.indexOf($scope.observable);
              $scope.$parent.$parent.$parent.composedobservable.observable_composition.observables.splice(index,1);
              //Serves currently only for composed observables
              //foo to get the paginaton right in case it changes
              var oldnumPages = $scope.$parent.$parent.$parent.pagination.numPages;
              $scope.$parent.$parent.$parent.pagination.numPages = Math.ceil($scope.$parent.$parent.$parent.composedobservable.observable_composition.observables.length/$scope.$parent.$parent.$parent.pagination.perPage);
              if (oldnumPages != $scope.$parent.$parent.$parent.pagination.numPages) {
                $scope.$parent.$parent.$parent.pagination.setPages();
                if (oldnumPages < $scope.$parent.$parent.$parent.pagination.numPages) {
                  $scope.$parent.$parent.$parent.pagination.nextPage();
                } else {
                  $scope.$parent.$parent.$parent.pagination.prevPage();
                }
                
              }
              
            } else {
              index = $scope.$parent.$parent.$parent.$parent.observables.indexOf($scope.observable);
              $scope.$parent.$parent.$parent.$parent.observables.splice(index,1);
              
            }
            
            
        }, function (response) {
          $scope.observable = angular.copy(original_observable);
          handleError(response, messages);
        });
       }
      };
      
      $scope.addObject = function(){
        var showModal = true;
        if ($scope.observable.object) {
          var r = confirm("Adding a second object to this observable will transform it into a composed one. Do you wish to continue?");
          showModal = r;
        }
        if (showModal){
          $modal({scope: $scope, template: 'pages/events/event/observable/object/add.html', show: true});
        }
      };
      
      $scope.showDetails = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/details.html', show: true});
      };
      
      $scope.showAddObjectBtn = function(){
        var index = -1;
        var obs = $scope.$parent.$parent.$parent.$parent.observables;
        if (obs){
          index = $scope.$parent.$parent.$parent.$parent.observables.indexOf($scope.observable);
        } else {
          index = $scope.$parent.$parent.$parent.$parent.indicator.observables.indexOf($scope.observable);
        }
        if (index >= 0) {
          return true;
        }
        else {
          if ($scope.observable){
            if ($scope.observable.object){
              return false;
            } else {
              return true;
            }
          }
            
          
        }
      };
      
      $scope.appendObservableObject = function(observableObject){
        if ($scope.observable.object) {
          //observableObject is actually an observable 
          index = $scope.$parent.$parent.$parent.$parent.observables.indexOf($scope.observable);
          $scope.$parent.$parent.$parent.$parent.observables[index] = observableObject;
          
          
        } else {
          $scope.observable.object = observableObject;
        }
      };
      

      $scope.setModified = setModified;

    },
    templateUrl: "pages/common/directives/observableview.html",
    compile: function(tElement, tAttr, transclude) {
      var contents = tElement.contents().remove();
      var compiledContents;
      return function(scope, iElement, iAttr) {

          if(!compiledContents) {
              compiledContents = $compile(contents, transclude);
          }
          compiledContents(scope, function(clone, scope) {
                   iElement.append(clone); 
          });
      };
    }
  };
});

app.directive("object", function($compile) {
  
  return {
    restrict: "E",
    replace: true,
    transclude: true,
    scope: {
      object: "=object",
      indent: "=indent",
      permissions: "=permissions",
      related: "=related"
    },
    controller: function($scope, $modal, Restangular, messages, $log, Pagination, $routeSegment){

      $scope.pagination = Pagination.getNew(5,'object.attributes');
      if ($scope.object.attributes){
        items = $scope.object.attributes;
      } else {
        items = [];
      }
      $scope.pagination.numPages = Math.ceil(items.length/$scope.pagination.perPage);
      $scope.pagination.setPages();
      
      $scope.showDetails = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/object/details.html', show: true});
      };
      $scope.showProperties = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/object/properties.html', show: true});
      };
      $scope.removeObject = function(){
        if (confirm('Are you sure you want to delete this object?')) {
          var remove = false;
          if ($scope.object.related_objects){
            items = $scope.object.related_objects;
          } else {
            items = [];
          }
          if (items.length > 0) {
            remove = confirm('Are you sure you want also it\'s children?');
          } else {
            remove = true;
          }
          if (remove){
            if ($scope.related){
              //TODO: create one a new view for related objects
              restangularObject = Restangular.restangularizeElement(null, $scope.object, 'object/'+$scope.object.identifier+'/related_object');
            } else {
              restangularObject = Restangular.restangularizeElement(null, $scope.object, 'object');
            }
            restangularObject.remove().then(function (data) {
              if ($scope.$parent.observable) {
                $scope.$parent.$parent.$parent.observable.object = null;
              } else {
                var index = -1;
                for (var i = 0; i < $scope.$parent.object.related_objects.length; i++) {
                  
                  if ($scope.$parent.object.related_objects[i].object.identifier == $scope.object.identifier) {
                    index = i;
                    break;
                  }
                }
                if (index >= 0) {
                  $scope.$parent.object.related_objects.splice(index, 1);
                } else {
                  index = $routeSegment.chain.length;
                  
                  $routeSegment.chain[index-1].reload();
                }
                
              }
              messages.setMessage({'type':'success','message':'Object sucessfully removed'});
            }, function (response) {
              handleError(response, messages);
            });
          }
        }
      };
      
      $scope.removeAttribute = function(attribute){
        if (confirm('Are you sure you want to delete this attribute?')) {
          restangularAttribute = Restangular.restangularizeElement(null, attribute, 'object/'+$scope.object.identifier+'/attribute');
          restangularAttribute.remove().then(function (data) {
            if (data) {
              var index = $scope.object.attributes.indexOf(attribute);
              $scope.object.attributes.splice(index, 1);
              
              messages.setMessage({'type':'success','message':'Attribute sucessfully removed'});
            }
          }, function (response) {
            handleError(response, messages);
          });

        }
      };
      $scope.showAttributeDetails = function(attribute){
        $scope.attributeDetails = attribute;
        $modal({scope: $scope, template: 'pages/events/event/observable/object/attributes/details.html', show: true});
      };

      $scope.addChildObject = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/object/addChild.html', show: true});
      };
      
      $scope.appendData = function(data){
        

        //check what kind of data it is
        if (typeof(data.id_) == 'undefined'){
          //this is an object
          $scope.object = data;
          
        } else {
          // observable
          
          var allObservables = $scope.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.observables;
          if (!allObservables){
            allObservables = $scope.$parent.$parent.$parent.$parent.$parent.$parent.observables;
          }
          counter = -1;
          index = -1;
          for (i= allObservables.length -1; i >= 0; i--) {
            if (allObservables[i].identifier == data.identifier) {
              index = i;
              break;
            }
          }
          allObservables[index] = data;
          
          //$scope.$parent.$parent.$parent.$parent.$parent.$parent.observables.push(data);
        }
        
        

      };
      
      $scope.addAttribute = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/object/attributes/add.html', show: true});
      };
      
      $scope.editAttribute = function(attribute){
        $scope.attributeDetails = attribute;
        $modal({scope: $scope, template: 'pages/events/event/observable/object/attributes/edit.html', show: true});
      };
      
      $scope.appendAttribute = function(attribute){
        if (!$scope.object.attributes){
          $scope.object.attributes  = [];
        }
        $scope.object.attributes.push(attribute);
      };
      
      $scope.updateAttribute = function(attribute){
        for (var i = 0; i < $scope.object.attributes.length; i++) {
          if ($scope.object.attributes[i].identifier == attribute.identifier){
            $scope.object.attributes[i] = attribute;
            break;
          }
        }
      };
      
      $scope.getStyle = function(properties) {
        if (properties.proposal && !properties.validated) {
          return 'background-color: yellow;';
        }
        if (!properties.validated) {
          return 'background-color: red;';
        }
        return '';
      };

      $scope.setModified = setModified;

      $scope.getColor = function(attribute){
        if (attribute.properties.proposal && !attribute.properties.validated){
          return 'background-color: yellow;';
        }else {
          if (!attribute.properties.proposal && !attribute.properties.validated){
            return 'background-color: red;';
          } else {
            
          }
        }
      };
    },
    templateUrl: "pages/common/directives/objectview.html",
    compile: function(tElement, tAttr, transclude) {
      var contents = tElement.contents().remove();
      var compiledContents;
      return function(scope, iElement, iAttr) {

          if(!compiledContents) {
              compiledContents = $compile(contents, transclude);
          }
          compiledContents(scope, function(clone, scope) {
                   iElement.append(clone); 
          });
      };
    }
  };
});

app.directive("report", function($compile) {
  
  return {
    restrict: "E",
    replace: true,
    transclude: true,
    scope: {
      report: "=report",
      indent: "=indent",
      permissions: "=permissions"
    },
    controller: function($scope, $modal, Restangular, messages, $log, Pagination){
      if (!$scope.report.references) {
        $scope.report.references = [];
      }
      $scope.pagination = Pagination.getNew(5,'report.references');
      $scope.pagination.numPages = Math.ceil($scope.report.references.length/$scope.pagination.perPage);
      $scope.pagination.setPages();
      
      $scope.showDetails = function(){
        $modal({scope: $scope, template: 'pages/events/event/report/details.html', show: true});
      };
      $scope.showProperties = function(){
        $modal({scope: $scope, template: 'pages/events/event/report/edit.html', show: true});
      };
      
      $scope.setModified = setModified;
      
      $scope.removeReport = function(){
        if (confirm('Are you sure you want to delete this report?')) {
          var remove = false;
          if ($scope.report.related_reports.length > 0) {
            remove = confirm('Are you sure you want also it\'s children?');
          } else {
            remove = true;
          }
          if (remove){
            restangularReport = Restangular.restangularizeElement(null, $scope.report, 'report');
            restangularReport.remove().then(function (data) {
              var index = -1;
              if ($scope.$parent.report.related_reports.length > 0){
                index = $scope.$parent.report.related_reports.indexOf($scope.report);
                $scope.$parent.report.related_reports.splice(index, 1);
              } else {
                index = $scope.$parent.$parent.reports.indexOf($scope.report);
                $scope.$parent.$parent.reports.splice(index, 1);
              }
              messages.setMessage({'type':'success','message':'Report sucessfully removed'});
            }, function (response) {
              handleError(response, messages);
            });
          }
        }
      };
      
      $scope.removeReference = function(reference){
        if (confirm('Are you sure you want to delete this reference?')) {
          restangularReference = Restangular.restangularizeElement(null, reference, 'report/'+$scope.report.identifier+'/reference');
          restangularReference.remove().then(function (data) {
            if (data) {
              var index = $scope.report.references.indexOf(reference);
              $scope.report.references.splice(index, 1);
              messages.setMessage({'type':'success','message':'Reference sucessfully removed'});
            }
          }, function (response) {
            handleError(response, messages);
          });

        }
      };
      $scope.showReferenceDetails = function(reference){
        $scope.referenceDetails = reference;
        $modal({scope: $scope, template: 'pages/events/event/report/reference/details.html', show: true});
      };
      
      //TODO: edit Reference
      
      $scope.addChildReport = function(){
        $modal({scope: $scope, template: 'pages/events/event/report/addChild.html', show: true});
      };
      
      $scope.appendChildren = function(data){
        $scope.report = data;
      };
      
      $scope.addReference = function(){
        $modal({scope: $scope, template: 'pages/events/event/report/reference/add.html', show: true});
      };
      
      $scope.editReference = function(reference){
        $scope.referenceDetails = reference;
        $modal({scope: $scope, template: 'pages/events/event/report/reference/edit.html', show: true});
      };
      
      $scope.appendReference = function(reference){
        if (!$scope.report.references){
          $scope.report.references  = [];
        }
        $scope.report.references.push(reference);
      };
      
      $scope.updateReference = function(reference){
        for (var i = 0; i < $scope.report.references.length; i++) {
          if ($scope.report.references[i].identifier == reference.identifier){
            $scope.report.references[i] = reference;
          }
        }
      };
      
      $scope.getReportTitle = function(report){
        if (report.title){
          return report.title + ' - ' + report.identifier; 
        } else {
          return 'Report - ' + report.identifier; 
        }
      };
    },
    templateUrl: "pages/common/directives/reportview.html",
    compile: function(tElement, tAttr, transclude) {
      var contents = tElement.contents().remove();
      var compiledContents;
      return function(scope, iElement, iAttr) {

          if(!compiledContents) {
              compiledContents = $compile(contents, transclude);
          }
          compiledContents(scope, function(clone, scope) {
                   iElement.append(clone); 
          });
      };
    }
  };
});



app.directive("menu", function($compile, $timeout) {
  
  return {
    restrict: "E",
    transclude: true,
    replace: true,
    scope: {
      items: "=items",
      first: "=first",
      limit: "=limit"
    },
    controller: function($scope, $anchorScroll, $location){
      $scope.getTitle = function(observable){
        if (observable.observable_composition){
          return "Composed observable";
        } else {
            if (observable.title) {
              return observable.title;
            } else {
              if (observable.object) {
                return "Observable - "+ observable.object.definition.name;
              } else {
                if (observable.hasOwnProperty('short_description')) {
                  if (!observable.title) {
                    if (observable.observables) {
                      return "Indicator";
                    } else {
                      return "Report";
                    }
                    
                  }
                } else {
                  return "Observable";
                }
                
                
              }
              
            }
          
        }
      };
      
      $scope.scrollTo = function(id) {
        if ($location.hash() !== id) {
          var hash =  $location.hash(id);
        } else {
          $anchorScroll();
        }
      };
    },
    templateUrl: "pages/common/directives/menuitem.html",
    compile: function(tElement, tAttr, transclude) {
      var contents = tElement.contents().remove();
      var compiledContents;
      return function(scope, iElement, iAttr) {

          if(!compiledContents) {
              compiledContents = $compile(contents, transclude);
          }
          compiledContents(scope, function(clone, scope) {
                   iElement.append(clone); 
          });
      };
    }
  };
});

app.directive("observableForm", function() {
  
  return {
    restrict: "E",
    scope: {
      observable: "=observable",
      type: "=type",
      permissions:"=permissions",
      showoperator: "=showoperator"
    },
    templateUrl: "pages/common/directives/observableform.html",
    controller: function($scope, $log){
      $scope.setModified = setModified;
    }
  };
});

app.directive("observableObjectForm", function() {
  
  return {
    restrict: "E",
    scope: {
      observableobject: "=observableobject",
      definitions: '=',
      permissions: "=permissions",
      type: "=type"
    },
    controller: function($scope, Restangular, messages){
      
      if ($scope.child) {
        //get the possible relations and add None
        Restangular.one('relations').getList().then(function(relations) {
          $scope.relations = relations;
        }, function(response) {
          handleError(response, messages);
        });
      } 

      $scope.setModified = setModified;
      $scope.showattribute = false;
      $scope.showattribtues = function(){
        if ($scope.type == 'add') {
          $scope.showattribute = true;
        }
        
      };
      
      $scope.$watch('observableobject.definition.identifier', function() {
        
        for (var i = 0; i < $scope.definitions.length; i++) {
          if ($scope.definitions[i].identifier === $scope.observableobject.definition.identifier){
            if (!$scope.observableobject.properties){
              $scope.observableobject.properties = {'shared': true};
            }
            $scope.observableobject.properties.shared = $scope.definitions[i].default_share;
            break;
          }
        }
      });

    },
    templateUrl: "pages/common/directives/observableobjectform.html"
  };
});

app.directive("relatedObjectForm", function() {
  
  return {
    restrict: "E",
    scope: {
      observableobject: "=observableobject",
      definitions: '=',
      permissions: "=permissions",
      type: "=type"
    },
    controller: function($scope, Restangular, messages){
      //get the possible relations and add None
      Restangular.one('relations').getList().then(function(relations) {
        $scope.relations = relations;
      }, function(response) {
        handleError(response, messages);
      });
      
      $scope.setModified = setModified;

    },
    templateUrl: "pages/common/directives/relatedobjectform.html"
  };
});

app.directive("serverForm", function() {
  
  return {
    restrict: "E",
    scope: {
      server: "=server",
      types: '=types',
      type: "=type",
      users: "=users"
    },
    controller: function($scope, $log){
      $scope.setModified = setModified;
    },
    templateUrl: "pages/common/directives/serverform.html"
  };
});

app.directive("eventReportForm", function() {
  
  return {
    restrict: "E",
    scope: {
      report: "=report",
      child: "=child",
      permissions: "=permissions",
      type: "=type"
    },
    controller: function($scope, $log){
      $scope.setModified = setModified;
    },
    templateUrl: "pages/common/directives/eventreportform.html"
  };
});

app.directive("objectAttributeForm", function() {
  
  return {
    restrict: "E",
    scope: {
      objectattribute: "=objectattribute",
      type: "=type",
      permissions: "=permissions",
      object: "=object"
    },
    controller: function($scope, $log, Restangular){
      $scope.getDefinition = function(identifier){
        var result = {};
        if ($scope.type == 'edit'){
          return $scope.objectattribute.definition;
        } else {
          for (var i = 0; i < $scope.definitions.length; i++) {
            if ($scope.definitions[i].identifier == identifier){
              result = $scope.definitions[i];
              break;
            }
          }
          return result;
        }
        
      };
      $scope.definitions =[];

      Restangular.one("objectdefinition", $scope.object.definition.identifier).getList("attributes",{"complete": true}).then(function (definitions) {
        $scope.allDefinitions = definitions;
      }, function(response) {
        handleError(response, messages);
        $scope.$hide();
      });
      Restangular.one("condition").getList(null, {"complete": false}).then(function (conditions) {
        $scope.conditions = conditions;
      }, function(response) {
        handleError(response, messages);
        $scope.$hide();
      });
      
      $scope.setDefinitions = function(){
        for (var j = 0; j < $scope.allDefinitions.length; j++) {
          found = false;
          //remove the ones already present
          if ($scope.object.attributes) {
            for (var i = 0; i < $scope.object.attributes.length; i++) {
              if ($scope.allDefinitions[j].identifier == $scope.object.attributes[i].definition.identifier) {
                found = true;
                break;
              }
            }
          }
          if (!found){
            $scope.definitions.push($scope.allDefinitions[j]);
          }
        }
      };
      
      $scope.$watch('object.definition.identifier', function() {
        
        $scope.definitions =[];
        Restangular.one("objectdefinition", $scope.object.definition.identifier).getList("attributes",{"complete": true}).then(function (definitions) {
          $scope.allDefinitions = definitions;
          $scope.setDefinitions();
        }, function(response) {
          handleError(response, messages);
          $scope.$hide();
        });
      });
      
      $scope.$watch('objectattribute.definition_id', function() {
          for (var i = 0; i < $scope.definitions.length; i++) {
            if ($scope.definitions[i].identifier === $scope.objectattribute.definition_id){
              if (!$scope.objectattribute.properties){
                $scope.objectattribute.properties = {'shared': true};
              }
              
              
              $scope.objectattribute.properties.shared = $scope.definitions[i].share;
              $scope.objectattribute.condition_id = $scope.definitions[i].default_condition_id;
              break;
            }
          }
        });
      
      $scope.setModified = setModified;
    },
    templateUrl: "pages/common/directives/objectattributeform.html"
  };
});

app.directive("reportReferenceForm", function() {
  
  return {
    restrict: "E",
    scope: {
      reportreference: "=reportreference",
      type: "=type",
      definitions: "=definitions",
      permissions: "=permissions"
    },
    controller: function($scope, $log){
      
      $scope.setModified = setModified;
      
      $scope.getDefinition = function(identifier){
        var result = {};
        if ($scope.type == 'edit'){
          return $scope.reportreference.definition;
        } else {
          for (var i = 0; i < $scope.definitions.length; i++) {
            if ($scope.definitions[i].identifier == identifier){
              result = $scope.definitions[i];
              break;
            }
          }
          return result;
        }
      };

    },
    templateUrl: "pages/common/directives/reportreferenceform.html"
  };
});


app.directive("attributeHandler", function() {

  return {
    restrict: "E",
    scope: {
      attribute: "=attribute",
      definition: "=definition",
      permissions: "=permissions",
      type: "=type",
      form: "=form"
    },
    template : '<div ng-include="getTemplate()"></div>',
    link: function(scope, element, attrs, ctrl) {
      
      
      scope.getTemplate = function(){
        var contentType =  scope.type;
        var viewType = null;
        if (scope.type == 'edit') {
          viewType = scope.attribute.definition.attributehandler.view_type;
        } else {
          viewType = scope.definition.attributehandler.view_type;
        }
        
        
        var baseUrl = 'pages/handlers';
        
        var templateUrl = baseUrl + '/attribtues/'+ contentType + '/'+viewType+'.html';
        templateUrl = templateUrl.toLowerCase();
        return templateUrl;
      };

    },
    controller: function($scope, $log, $templateCache, Restangular, messages ){
      //Resolve additional data
      $scope.setModified = setModified;
      
      $scope.getData = function() {
        if (scope.type == 'edit') {
          Restangular.one('attributehandlers', $scope.attribute.definition.identifier).one('get').getList(null, {'type': $scope.type}).then(function(handlerdata) {
            $scope.handlerdata = handlerdata;
          }, function(response) {
            handleError(response, messages);
          });
        } else {
          Restangular.one('attributehandlers', $scope.definition.identifier).one('get').getList(null, {'type': $scope.type}).then(function(handlerdata) {
            $scope.handlerdata = handlerdata;
          }, function(response) {
            handleError(response, messages);
          });
        }
      };

      $scope.setModified = setModified;
      
      $scope.$watch('definition.regex', function() {
        $scope.patternexpression = (function() {
          if (($scope.type != 'view') ){
            var regexp = /^.*$/;
            var muliline = false;
            if ($scope.type == 'edit') {
              regexp = $scope.attribute.definition.regex ;
              muliline = $scope.attribute.definition.attributehandler.is_multi_line;
            } else {
              regexp = $scope.definition.regex;
              muliline = $scope.definition.attributehandler.is_multi_line;
            }
            regexp = new RegExp(regexp);
            
            return {
                test: function(value) {
                    if( $scope.requireVal === false ) {
                        return true;
                    }
                    if (muliline) {
                      //silly but works
                      var splitted = value.split("\n");
                      for (var i in splitted) {
                        var cleaned = splitted[i].replace(/(\r\n|\n|\r)/gm,"");
                        if (!regexp.test(cleaned)){
                          return false;
                        }
                      }
                      return true;
                      
                      
                      
                    } else {
                      return regexp.test(value);
                    }

                    
                }
            };
          } else {
            return /^.*$/;
          }
        })();
        
      });

      $scope.patternexpression = /^.*$/;
    },
  };
});

app.directive("referenceHandler", function() {
  

  
  
  return {
    restrict: "E",
    scope: {
      resource: "=reference",
      definition: "=definition",
      permissions: "=permissions",
      type: "=type",
      form: "=form"
    },
    template : '<div ng-include="getTemplate()"></div>',
    link: function(scope, element, attrs, ctrl) {
      
      
      scope.getTemplate = function(){
        var contentType =  scope.type;
        var viewType = null;
        if (scope.type == 'edit') {
          viewType = scope.resource.definition.reference_handler.view_type;
        } else {
          viewType = scope.definition.reference_handler.view_type;
        }
        var baseUrl = 'pages/handlers';
        
        var templateUrl = baseUrl + '/references/'+ contentType + '/'+viewType+'.html';
        templateUrl = templateUrl.toLowerCase();
        return templateUrl;
        
      };

    },
    controller: function($scope, $log, $templateCache, Restangular, messages ){
      //Resolve additional data
      $scope.loading = false;
      $scope.getData = function() {
        $scope.loading = true;
        if ($scope.type == 'edit') {
          Restangular.one('referencehandlers', $scope.resource.definition.identifier).one('get').getList(null, {'type': $scope.type}).then(function(handlerdata) {
            $scope.handlerdata = handlerdata;
          }, function(response) {
            handleError(response, messages);
          });
          $scope.loading = false;
        } else {
          Restangular.one('referencehandlers', $scope.definition.identifier).one('get').getList(null, {'type': $scope.type}).then(function(handlerdata) {
            $scope.handlerdata = handlerdata;
          }, function(response) {
            handleError(response, messages);
          });
          $scope.loading = false;
        }
      };
      
      $scope.$watch('definition.regex', function() {
        $scope.patternexpression = (function() {
          if (($scope.type != 'view') ){
            var regexp = /^.*$/;
            var muliline = false;
            if ($scope.type == 'edit') {
              regexp = $scope.resource.definition.regex ;
              muliline = $scope.resource.definition.reference_handler.is_multi_line;
            } else {
              regexp = $scope.definition.regex;
              muliline = $scope.definition.reference_handler.is_multi_line;
            }
            regexp = new RegExp(regexp);
            
            return {
                test: function(value) {
                    if( $scope.requireVal === false ) {
                        return true;
                    }
                    if (muliline) {
                      //silly but works
                      var splitted = value.split("\n");
                      for (var i in splitted) {
                        var cleaned = splitted[i].replace(/(\r\n|\n|\r)/gm,"");
                        if (!regexp.test(cleaned)){
                          return false;
                        }
                      }
                      return true;
                      
                      
                      
                    } else {
                      return regexp.test(value);
                    }

                    
                }
            };
          } else {
            return /^.*$/;
          }
        })();
        
      });
      

      $scope.setModified = setModified;

      $scope.patternexpression = /^.*$/;
    },
  };
});


app.directive("eventForm", function() {
  
  return {
    restrict: "E",
    scope: {
      event: "=event",
      type: "=type",
      statuses: '=statuses',
      anlysises: '=anlysises',
      risks:'=risks',
      tlps: '=tlps'
    },
    controller: function($scope, $log){
      if ($scope.type == 'add'){
        $scope.addEvent = true;
      } else {
        $scope.addEvent = false;
      }
      $scope.setModified = setModified;
    },
    templateUrl: "pages/common/directives/eventform.html"
  };
});

app.directive("objectPropertiesForm", function() {
  
  return {
    restrict: "E",
    scope: {
      item: "=object",
      type: "=type",
      permissions: "=permissions"
    },
    controller: function($scope, $log){
      $scope.setModified = setModified;
    },
    
    templateUrl: "pages/common/directives/objectproperties.html"
  };
});