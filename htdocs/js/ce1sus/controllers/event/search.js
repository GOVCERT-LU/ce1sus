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
   
  
  var makeFlat = function(entry) {
    var observable = '';
    if (entry.observable){
      if (entry.observable.title) {
        observable = entry.observable.title;
      } else {
        observable = 'Observable';
      }
    } else {
      if (entry.report){
        observable = 'Report';
      }
    }
    var objType = '';
    if (entry.object){
      objType = entry.object.definition.name;
    } else {
      if (entry.report){
        if (entry.report.title) {
          objType = entry.report.title;
        } else {
          objType = entry.identifier;
        }
        
      }
    }
    var attribute =  entry.attribute;
    
    return {'event':entry.event,'eventTitle':entry.event.stix_header.title,'observable':observable,'objectType':objType,'attribute':attribute};
    
  };

  $scope.submitSearch = function(){
    results = [];
    $scope.results = -1;
    $scope.resultTable.reload();
    
    Restangular.all("search").post($scope.search).then(function (data) {
      if (data) {
        for (var i = 0; i < data.length; i++) {
          results.push(makeFlat(data[i]));
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
      results = [];
      $scope.results = results.length;
      $scope.resultItems = results;
      $scope.resultTable.reload();
      handleError(response, messages);
    });
    //$scope.search = angular.copy(original_search);
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


