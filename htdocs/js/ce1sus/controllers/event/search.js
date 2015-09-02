/**
 * 
 */

app.controller("serachController", function($scope, Restangular,messages, $log, $routeSegment, attributes, ngTableParams, $filter) {
  $scope.attributes = attributes;
  //default searc
});

app.controller("doSerachController", function($scope, Restangular,messages, $log, $routeSegment, ngTableParams, $filter) {
  var original_search =  {'operator': '==','field':null};
  $scope.search = angular.copy(original_search);
  
  $scope.results = -2;
  $scope.resultItems = [];
  
  $scope.searchChanged = function (){
    return !angular.equals($scope.search, original_search);
  };
  
  function find_value(item){
    var needle = $scope.search.value;
    item_list = _.values(item);
    return _.find(item_list, function(value){ 
         if ((value+'').indexOf(needle) >=0){
           return value;
         }
       });
  }
  
  function make_search_entry(entry) {
    var event = '';
    var item = '';
    var type = '';
    var value = '';
    var title = '';
    
    if (entry.event){
      event = entry.event;
      value = find_value(entry.event);
      if (entry.event.stix_header){
        title = event.stix_header.title;
      }
    }
    if (entry.observable){
      item = 'Observable';
      value = find_value(entry.observable);
    }
    if (entry.indicator){
      item = 'Indicator';
      value = find_value(entry.indicator);
    }
    if (entry.report){
      item = 'Report';
      value = find_value(entry.report);
    }
    if (entry.reference){
      item = 'Refernece';
      type = entry.reference.definition.name;
      value = find_value(entry.reference);
    }
    if (entry.attribute){
      item = 'Attribute';
      type = entry.attribute.definition.name;
      value = find_value(entry.attribute);
    }
    if (entry.object){
      item = 'Object';
      type = entry.object.definition.name;
      value = find_value(entry.object);
    }
    if (entry.composed_observable){
      item = 'Composed Observable';
      value = find_value(entry.composed_observable);
    }
    if (entry.stix_header){
      item = 'Stix Header';
      value = find_value(entry.stix_header);
    }

    return {'event': event,'eventTitle': title,'type':type,'item':item,'value':value};
    
  }

  $scope.submitSearch = function(){
    results = [];
    $scope.results = -1;
    $scope.resultTable.reload();
    
    Restangular.all("search").post($scope.search).then(function (data) {
      if (data) {
        for (var i = 0; i < data.length; i++) {
          results.push(make_search_entry(data[i]));
        }
        $scope.results = results.length;
        $scope.resultItems = results;
        $scope.resultTable.reload();
      } else {
        messages.setMessage({'type':'info','message':'The given search did not yield any results'});
        results = [];
        $scope.results = results.length;
        $scope.resultItems = results;
        $scope.resultTable.reload();
      }
    }, function (response) {
      handleError(response, messages);
    });

  };

  $scope.resultTable = new ngTableParams({
    page: 1,            // show first page
    count: 10           // count per page
  }, {
    total: $scope.resultItems.length, // length of data
    getData: function($defer, params) {
        // use build-in angular filter
      
      var orderedData = params.sorting() ?
              $filter('orderBy')($scope.resultItems, params.orderBy()) :
              data;
      orderedData = params.filter() ?
              $filter('filter')(orderedData, params.filter()) :
              orderedData;
      params.total(orderedData.length);
      $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
    }
  }); 
 
});


