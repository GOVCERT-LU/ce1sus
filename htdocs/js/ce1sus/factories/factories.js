/**
 * 
 */

ce1susApp.factory("messages", function($rootScope, $alert, messageQueue) {
  var currentMessage = "";
  $rootScope.$watch("messageSet", function(newValue, oldValue) { 
    if (newValue) {
      currentMessage = messageQueue.shift() || "";
      if (currentMessage) {
        var type = currentMessage.type;
        if (!type){
          type = "info";
        }
        var message = currentMessage.message;
        var title = currentMessage.title;
        if (!title){
          title = type.charAt(0).toUpperCase() + type.slice(1);
        }
        if (title == "Danger"){
          title = "Error";
        }
        
        var myAlert = $alert({title: title+":", 
                              content: message, 
                              type: type, 
                              container: "#alerts-container",
                              animation: "am-fade-and-slide-top",
                              duration: 10,
                              show: true});
      }
      $rootScope.messageSet = false;
    }
    
  });
  return {
    setMessage: function(message) {
      $rootScope.messageSet = true;
      messageQueue.push(message);
    },
    showMessage: function(){
      $rootScope.messageSet = true;
    }
      
  };
});
/*
ce1susApp.factory('$exceptionHandler', function( $injector, messageQueue) {
  return function(exception, cause) {
    
    var $rootScope = $injector.get("$rootScope");
    //put the unmodified data back incase there is an error
    var $routeSegment = $injector.get("$routeSegment");

    var type = 'danger';
    var message = exception.message;
    if (cause) {
      message = message += ' (caused by "' + cause + '")';
    }
    if (exception.name){
      type = exception.type;
    }
    messageQueue.push({'type': type,'message': message});
    $rootScope.messageSet = true;
    
    //window.location.reload();
  };
});
*/