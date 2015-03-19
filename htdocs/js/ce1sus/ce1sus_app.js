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
                                 'angularFileUpload',
                                 'angular-loading-bar',
                                 'angular-growl',
                                 'ui.select'
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
