/**
 * 
 */

var app = angular.module('app', ['ngRoute', 
                                 'ngAnimate', 
                                 'route-segment', 
                                 'view-segment',
                                 "restangular", 
                                 'ngSanitize', 
                                 "mgcrea.ngStrap",
                                 'ngTable',
                                 'simplePagination',
                                 'angularFileUpload'
                                 ]);


app.provider('messageQueue', function () {
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
  };
});
