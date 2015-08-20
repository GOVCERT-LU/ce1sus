/**
 * 
 */

app.controller("eventReportController", function($scope, Restangular, messages,
    $log, $routeSegment, $location,reports, $anchorScroll, Pagination) {
  $scope.permissions=$scope.event.userpermissions;
  $scope.reports = reports;
});

app.controller("reportAddController", function($scope, Restangular, messages,
    $log, $routeSegment, $location) {
  var original_report = {};
  $scope.report=angular.copy(original_report);
  
  $scope.closeModal = function(){
    $scope.report = angular.copy(original_report);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetReport = function ()
  {
    $scope.report = angular.copy(original_report);

  };
  

  
  $scope.reportChanged = function ()
  {
    //return !angular.equals($scope.report, original_report);
    //can also be empty
    return true;
  };
  
  $scope.submitReport = function(){
    Restangular.one('event', $scope.event.identifier).post('report', $scope.report, {'complete':true, 'infated':true}).then(function (data) {
      if ($scope.$parent.$parent.appendReport){
        $scope.$parent.$parent.appendReport(data);
      } else {
        // apped root level
        $scope.reports.push(data);
      }
    }, function (response) {
      $scope.report = angular.copy(original_report);
      handleError(response, messages);
    });
    $scope.$hide();
  };
});

app.controller("reportAddChildController", function($scope, Restangular, messages,
    $log, $routeSegment, $location) {
  var original_report = {};
  $scope.report=angular.copy(original_report);
  
  $scope.closeModal = function(){
    $scope.report = angular.copy(original_report);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetReport = function ()
  {
    $scope.report = angular.copy(original_report);

  };
  

  
  $scope.reportChanged = function ()
  {
    //return !angular.equals($scope.report, original_report);
    //can also be empty
    return true;
  };
  
  $scope.submitReport = function(){
    var report_id = $scope.$parent.report.identifier;
    Restangular.one('report', report_id).post('report', $scope.report, {'complete':true, 'infated':true}).then(function (data) {
      if ($scope.$parent.$parent.appendReport){
        $scope.$parent.$parent.appendReport(data);
      } else {
        // apped root level
        $scope.$parent.report.related_reports.push(data);
      }
    }, function (response) {
      $scope.report = angular.copy(original_report);
      handleError(response, messages);
    });
    $scope.$hide();
  };
});

app.controller("reportEditController", function($scope, Restangular, messages,
    $log, $routeSegment, $location) {
  var original_report = angular.copy($scope.report);
  
  $scope.closeModal = function(){
    $scope.report = angular.copy(original_report);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetReport = function ()
  {
    $scope.report = angular.copy(original_report);

  };
  

  
  $scope.reportChanged = function ()
  {
    //return !angular.equals($scope.report, original_report);
    //can also be empty
    return true;
  };
  
  $scope.submitReport = function(){
    //restangularize element as path changes
    restangularizedElement = Restangular.restangularizeElement(null, $scope.report, 'report');
    restangularizedElement.put({'complete':true, 'infated':true}).then(function (data) {

      $scope.report = data;
      for (var i = 0; i < $scope.reports.length; i++) {
        if ($scope.reports[i].identifier == data.identifier) {
          $scope.reports[i].title = data.title;
          break;
        }
      }
      
    }, function (response) {
      $scope.report = angular.copy(original_report);
      handleError(response, messages);
    });
    $scope.$hide();
  };
});