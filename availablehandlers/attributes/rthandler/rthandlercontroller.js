/**
 * 
 */

app.controller("rtController", function($scope, ngTableParams, $filter) {
  var data = $scope.handlerdata;
  $scope.tableParams = new ngTableParams({
    page: 1,            // show first page
    count: 10,          // count per page
    sorting: {
        name: 'asc'     // initial sorting
    }
  }, {
      total: data.length, // length of data
      getData: function($defer, params) {
          // use build-in angular filter
          var orderedData = params.filter() ? $filter('filter')(data, params.filter()) : data; 
          orderedData = params.sorting() ? $filter('orderBy')(orderedData, params.orderBy()) : orderedData;
          
          
          params.total(orderedData.length);
          $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
          
      }
  }); 
});