/**
 * 
 */

app.controller("mailController", function($scope, Restangular, messages,
    $log, $routeSegment, mails) {
  $scope.mails = mails;
  
  $scope.$routeSegment = $routeSegment;


});

app.controller('mailDetailController', function($scope, $routeSegment,$mail, $log) {
  
  
  $scope.mail = $mail;
  
  
  $scope.$routeSegment = $routeSegment;
  

});

app.controller("mailEditController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
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