/**
 * 
 */

ce1susApp.controller("mailController", function($scope, Restangular, messages,
    $log, $routeSegment) {
  $scope.mails = [];
  
  Restangular.one("mail").getList(null,{"Complete": false}).then(function (mails) {
    $scope.mails = mails;
  });
  
  $scope.$routeSegment = $routeSegment;


});

ce1susApp.controller("mailDetailController", function($scope, Restangular, messages,
    $log, $routeSegment) {
  
  var identifier = $routeSegment.$routeParams.id;
  
  $scope.mail = {};
  Restangular.one("mail",identifier).get(null,{"Complete": true}).then(function (data) {
    $scope.mail = data;
  });

  $scope.$routeSegment = $routeSegment;
  

});

ce1susApp.controller("mailEditController", function($scope, Restangular, messages, $routeSegment,$location, cfpLoadingBar, $log) {
  var original_mail = angular.copy($scope.mail);

  
  //Scope functions
  $scope.resetMail = function ()
  {
    $scope.mail = angular.copy(original_mail);
    $scope.addMailForm.$setPristine();
  };
  
  $scope.mailChanged = function ()
  {
    var result = !angular.equals($scope.mail, original_mail);
    return result;
  };
  
  $scope.submitMail = function(){
    $scope.mail.put().then(function (maildata) {
      if (maildata) {
        $scope.mail = maildata;
      }
      messages.setMessage({'type':'success','message':'User sucessfully edited'});
    });
    $scope.$hide();
  };

});