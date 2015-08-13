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
  
  $scope.setMail = function(mail){
    $scope.mail = mail;
  };
});

app.controller("mailEditController", function($scope, Restangular, messages, $routeSegment,$location, $log) {
  var original_mail = angular.copy($scope.mail);


  $scope.closeModal = function(){

    var mail = angular.copy(original_mail);
    $scope.$parent.setMail(mail);
    $scope.$hide();
    
  };
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
    $scope.mail.modified_on = new Date().getTime();
    $scope.mail.put().then(function (maildata) {
      if (maildata) {
        $scope.mail = maildata;
      }
      messages.setMessage({'type':'success','message':'Mail sucessfully edited'});
    }, function (response) {
      var mail = angular.copy(original_mail);
      $scope.$parent.setMail(mail);
      handleError(response, messages);
    });
    $scope.$hide();
  };

});