

app.controller("MainJobscontroller", function($scope, Restangular, messages, $log, $routeSegment, $location, ngTableParams, $filter, jobs) {
  $scope.jobs = jobs;
  $scope.jobsTable = new ngTableParams({
    page: 1,            // show first page
    count: 10,           // count per page
    sorting: {
      created_at: 'desc'     // initial sorting
    } 
  }, {
    total: $scope.jobs.length, // length of syncservers
    getData: function($defer, params) {

      // use build-in angular filter

      var filteredData = params.filter() ?

              $filter('filter')($scope.jobs, params.filter()) :

              $scope.jobs;

      var orderedData = params.sorting() ?

              $filter('orderBy')(filteredData, params.orderBy()) :

              $scope.jobs;

      params.total(orderedData.length); // set total for recalc pagination

      $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));

    }
  }); 
});

app.controller("Jobscontroller", function($scope, Restangular, messages, $log, $routeSegment, $location,$modal) {
  function findAndReplace(item){
    var index=0;
    angular.forEach($scope.jobs, function(entry) {
      if (entry.identifier === item.identifier){
        $scope.jobs[index] = data;
      }
      index++;
    }, $log);
    $scope.jobsTable.reload();
  }
  
  $scope.restart = function(item){
    message = {"type":"info","message":"Starting restarting of job "+item.identifier};
    messages.setMessage(message);
    Restangular.one('processes/reschedule/',item.identifier).get().then(function(data) {
      message = {"type":"success","message":"Job rescheduled "+item.identifier};
      messages.setMessage(message);
      //find and reset item in jobs list
      findAndReplace(data);
    }, function (response) {
      handleError(response, messages);
    });
  };
  
  $scope.cancel = function(item){
    message = {"type":"info","message":"Starting cancelation of job "+item.identifier};
    messages.setMessage(message);
    Restangular.one('processes/cancel/',item.identifier).get().then(function(data) {
      message = {"type":"success","message":"Job cancelled "+item.identifier};
      messages.setMessage(message);
      //find and reset item in jobs list
      findAndReplace(data);
    }, function (response) {
      handleError(response, messages);
    });
  };

  
  $scope.remove = function(item){
    message = {"type":"info","message":"Starting removal of job "+item.identifier};
    messages.setMessage(message);
    Restangular.one('processes/remove/',item.identifier).get().then(function(data) {
      message = {"type":"success","message":"Job removed "+item.identifier};
      messages.setMessage(message);
      // find and reset item in jobs list
      var index=0;
      var r_index=-1;
      angular.forEach($scope.jobs, function(entry) {
        if (entry.identifier === item.identifier){
          r_index = index;
        }
        index++;
      }, $log);
      $scope.jobs.splice(r_index, 1);
      $scope.jobsTable.reload();
    }, function (response) {
      handleError(response, messages);
    });
  };
});