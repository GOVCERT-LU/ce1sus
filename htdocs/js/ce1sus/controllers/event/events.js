/**
 * 
 */

app.controller("eventsController", function($scope, Restangular, messages,
    $log, $routeSegment, $location, ngTableParams) {

  
  $scope.getTlpColor = function(tlpText){
    return getTlpColor(tlpText);
  };
  $scope.eventTable = new ngTableParams({
      page: 1,            // show first page
      count: 10,           // count per page
      sorting: {
        created_at: 'desc'     // initial sorting
      } 
  }, {
      total: 0, // length of data
      getData: function($defer, params) {
        // Make restangular call
        Restangular.one("events").get(params.url(), {"Complete": false}).then(function(data) {
          if (data) {
            //Set total 
            params.total(data.total);
            //set data
            $defer.resolve(data.data);
          } else {
            //show error
          }
        }, function (response) {
          handleError(response, messages);
        });

      }
  }); 

});
