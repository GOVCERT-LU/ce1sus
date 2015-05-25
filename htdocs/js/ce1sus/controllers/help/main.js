app.controller('swaggerController', function($scope, $routeSegment, $window, $timeout) {
          var timer = $timeout(
              function() {
                $window.open('/swagger', '_blank');
              }, 1000);
          timer.then(function() {
            console.log("Timer resolved!", Date.now());
          }, function() {
            console.log("Timer rejected!", Date.now());
          });
          $scope.$on("$destroy", function(event) {
            $timeout.cancel(timer);
          });
        });