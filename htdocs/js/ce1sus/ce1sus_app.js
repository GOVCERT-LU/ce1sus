/**
 * 
 */


var ce1susApp = angular.module("ce1susApp", ["chieffancypants.loadingBar",
                                             "ngRoute",
                                             "ngAnimate", 
                                             "route-segment", 
                                             "view-segment",
                                             "restangular",
                                             "mgcrea.ngStrap",
                                             "ngTable"]);


ce1susApp.provider('messageQueue', function () {
  this.queue = [];
  return {
    setQueue: function (value) {
      this.queue = value;
    },
    pushToQueue: function (value) {
      this.queue.push(value);
    },
    $get: function () {
      return this.queue;
    }
  }
});
 
