/**
 * 
 */

var queue = [];

app.config(function($routeSegmentProvider, $routeProvider, RestangularProvider, messageQueueProvider, $scrollspyProvider, cfpLoadingBarProvider) {
  
  RestangularProvider.setDefaultHeaders({frontend: true});
  
  cfpLoadingBarProvider.includeSpinner = false;
  
  angular.extend($scrollspyProvider.defaults, {
    animation: 'am-fade-and-slide-top',
    placement: 'top'
  });
  

  
    messageQueueProvider.setQueue(queue);
    // Configuring provider options
    RestangularProvider.setBaseUrl("/REST/0.3.0");
    RestangularProvider.setRestangularFields({
      id : "identifier"
    });
    $routeSegmentProvider.options.autoLoadTemplates = true;
    
    // Setting routes.

    $routeSegmentProvider
    
        .when('/', 'main.layout')
        .when("/home", "main.layout.home")
        .when("/activate/:id", "main.layout.activate")
        .when("/login", "main.layout.login")
        .when("/logout", "main.layout.logout")
        .when("/help/restapi", "main.layout.help.restapi")
        .when("/help/about", "main.layout.help.about")
        .when("/events", "main.layout.events")
        .when("/events/all", "main.layout.events.allEvents")
        .when("/events/unpublished", "main.layout.events.unpublished")
        .when("/events/unpublished/events", "main.layout.events.unpublished.uevents")
        .when("/events/unpublished/observables", "main.layout.events.unpublished.observables")
        .when("/events/unpublished/objects", "main.layout.events.unpublished.objects")
        .when("/events/unpublished/attributes", "main.layout.events.unpublished.attributes")
        .when("/events/search", "main.layout.events.serach")
        .when("/events/add", "main.layout.events.add")
        .when("/events/event/:id", "main.layout.events.event")
        .when("/events/event/:id/overview", "main.layout.events.event.overview")
        .when("/events/event/:id/observables", "main.layout.events.event.observables")
        .when("/events/event/:id/indicators", "main.layout.events.event.indicators")
        .when("/events/event/:id/indicators", "main.layout.events.event.indicators")
        .when("/events/event/:id/relations", "main.layout.events.event.relations")
        .when("/events/event/:id/reports", "main.layout.events.event.reports")
        .when("/events/event/:id/groups", "main.layout.events.event.groups")
        .when("/admin", "main.layout.admin")
        .when("/admin/validation", "main.layout.admin.validation")
        .when("/admin/validation/all", "main.layout.admin.validation.all")
        .when("/admin/validation/event/:id", "main.layout.admin.validation.event")
        .when("/admin/validation/event/:id/overview", "main.layout.admin.validation.event.overview")
        .when("/admin/validation/event/:id/observables", "main.layout.admin.validation.event.observables")
        .when("/admin/validation/event/:id/indicators", "main.layout.admin.validation.event.indicators")
        .when("/admin/validation/event/:id/reports", "main.layout.admin.validation.event.reports")
        .when("/admin/validation/event/:id/relations", "main.layout.admin.validation.event.relations")
        .when("/admin/validation/event/:id/groups", "main.layout.admin.validation.event.groups")
        
        
        .when("/admin/objAttrMgt", "main.layout.admin.objAttrMgt")
        .when("/admin/user", "main.layout.admin.user")
        .when("/admin/user/:id", "main.layout.admin.user.userDetails")
        .when("/admin/group", "main.layout.admin.group")
        .when("/admin/group/:id", "main.layout.admin.group.groupDetails")
        
        .when("/admin/condition", "main.layout.admin.condition")
        .when("/admin/condition/:id", "main.layout.admin.condition.conditionDetails")
        
        .when("/admin/syncservers", "main.layout.admin.syncservers")
        .when("/admin/syncservers/help", "main.layout.admin.syncservers.help")
        .when("/admin/syncservers/servers", "main.layout.admin.syncservers.servers")
        
        .when("/admin/jobs", "main.layout.admin.bgjobs")
        .when("/admin/jobs/help", "main.layout.admin.bgjobs.help")
        .when("/admin/jobs/jobs", "main.layout.admin.bgjobs.jobs")
        
        .when("/admin/object", "main.layout.admin.object")
        .when("/admin/object/:id", "main.layout.admin.object.objectDetails")
        .when("/admin/type", "main.layout.admin.type")
        .when("/admin/type/:id", "main.layout.admin.type.typeDetails")
        .when("/admin/attribute", "main.layout.admin.attribute")
        .when("/admin/attribute/:id", "main.layout.admin.attribute.attributeDetails")
        .when("/admin/mail", "main.layout.admin.mail")
        .when("/admin/mail/:id", "main.layout.admin.mail.mailDetails")
        .when("/admin/reference", "main.layout.admin.reference")
        .when("/admin/reference/:id", "main.layout.admin.reference.referenceDetails")
        
        .segment('main', {
            //Main consits only of a main template
            templateUrl: 'pages/main.html',
          })
        .within()
            .segment('layout', {
                'default': true,
                templateUrl: 'pages/layout.html',
                controller: 'layoutController',
                resolve: {
                  version: function(Restangular) {
                    return Restangular.one("version").get().then(function(version) {
                        return version;
                      }, function(response) {
                        throw generateErrorMessage(response);
                      });
                  },
                  menus: function(Restangular) {
                    return Restangular.allUrl("menus", "/menus/primary_menus").getList().then(function(menus) {
                        return menus;
                      }, function(response) {
                        throw generateErrorMessage(response);
                      });
                  }
                },
                untilResolved: {
                    templateUrl: 'pages/common/loading.html',
                    controller: 'loadingController'
                },
                resolveFailed: {
                  templateUrl: 'pages/common/error.html',
                  controller: 'errorController'
                }
            })
            .within()
                  .segment('home', {
                    'default': true,
                     templateUrl: 'pages/home.html',
                     controller: 'homeController',
                     resolve: {
                       changelog: function(Restangular) {
                         return Restangular.oneUrl("text", "/welcome_message").get().then(function(message) {
                             return message;
                           }, function(response) {
                             throw generateErrorMessage(response);
                           });
                       }
                     },
                     untilResolved: {
                       templateUrl: 'pages/common/loading.html',
                       controller: 'loadingController'
                     },
                     resolveFailed: {
                       templateUrl: 'pages/common/error.html',
                       controller: 'errorController'
                     }
                   })
                   .segment('activate', {
                     templateUrl: 'pages/activate.html',
                     controller: 'activationController',
                     resolve: {
                       activated: function(Restangular, $routeSegment) {
                         return Restangular.one("login/activation", $routeSegment.$routeParams.id).get().then(function(message) {
                             return message;
                           }, function(response) {
                             throw generateErrorMessage(response);
                           });
                       }
                     },
                     untilResolved: {
                       templateUrl: 'pages/common/loading.html',
                       controller: 'loadingController'
                     },
                     resolveFailed: {
                       templateUrl: 'pages/common/error.html',
                       controller: 'errorController'
                     }
                   })
                  .segment('login', {
                    templateUrl : "pages/login.html",
                    controller : "loginController"
                  })
                  .segment('logout', {
                    templateUrl : "pages/logout.html",
                    controller : "logoutController"
                  })
                  .segment('help', {
                    templateUrl : "pages/help/layout.html"
                      
                  }).within()
                    .segment("about", {
                                'default': true,
                                 templateUrl: "pages/help/about.html"
                     })
                    .segment("restapi", {
                                 templateUrl: "pages/help/api.html",
                                 controller: "swaggerController"
                     })
                  .up()
                  .segment('events', {
                    templateUrl : "pages/events.html",
                    controller: "eventController",
                    resolve: {
                      eventmenus: function(Restangular) {
                        return Restangular.oneUrl("eventmenus", "/menus/event_links").getList().then(function(eventmenus) {
                          return eventmenus;
                        }, function(response) {
                          throw generateErrorMessage(response);
                        });
                      },
                      statuses: function(Restangular) {
                        return Restangular.one("statuses").getList(null, {"complete": true}).then(function (items) {
                          return items;
                        }, function(response) {
                            throw generateErrorMessage(response);
                        });
                      },
                      risks: function(Restangular) {
                        return Restangular.one("risks").getList(null, {"complete": true}).then(function (items) {
                          return items;
                        }, function(response) {
                            throw generateErrorMessage(response);
                        });
                      },
                      tlps: function(Restangular) {
                        return Restangular.one("tlps").getList(null, {"complete": true}).then(function (items) {
                          return items;
                        }, function(response) {
                            throw generateErrorMessage(response);
                        });
                      },
                      analyses: function(Restangular) {
                        return Restangular.one("analyses").getList(null, {"complete": true}).then(function (items) {
                          return items;
                        }, function(response) {
                            throw generateErrorMessage(response);
                        });
                      }
                    },
                    untilResolved: {
                      templateUrl: 'pages/common/loading.html',
                      controller: 'loadingController'
                    },
                    resolveFailed: {
                      templateUrl: 'pages/common/error.html',
                      controller: 'errorController'
                    }
                      
                  })
                      .within()
                        .segment("allEvents", {
                                'default': true,
                                 templateUrl: "pages/events/all.html",
                                 controller: 'eventsController'
                        })
                        .segment("event", {
                                 templateUrl: "pages/events/event/layout.html",
                                 controller: 'viewEventController',
                                 resolve: {
                                   $event: function(Restangular,$routeSegment) {
                                     return Restangular.one("event",$routeSegment.$routeParams.id).get({"complete": true}).then(function (data) {
                                       return data;
                                     }, function(response) {
                                         throw generateErrorMessage(response);
                                     });
                                   },
                                  groups: function(Restangular) {
                                    return Restangular.one("groups").getList(null, {"complete": true}).then(function (groups) {
                                      return groups;
                                    }, function(response) {
                                      return [];
                                    });
                                  }
                                 },
                                 dependencies: ["id"],
                                 untilResolved: {
                                   templateUrl: 'pages/common/loading.html',
                                   controller: 'loadingController'
                                 },
                                 resolveFailed: {
                                   templateUrl: 'pages/common/error.html',
                                   controller: 'errorController'
                                 }
                        })
                        .within()
                          .segment("overview", {
                            'default': true,
                            templateUrl: "pages/events/event/overview.html",
                            controller: 'eventOverviewController',
                            resolve: {
                              useradmin: function(Restangular,$routeSegment) {
                                return Restangular.one("checks","isuseradmin").get().then(function (data) {
                                  return data;
                                }, function(response) {
                                  return false;
                                });
                              },
                              relations: function(Restangular,$routeSegment) {
                                return Restangular.one("event",$routeSegment.$routeParams.id).all("relations").getList({'complete':false}).then(function (data) {
                                  return data;
                                }, function(response) {
                                  return false;
                                });
                              },
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("observables", {
                            templateUrl: "pages/events/event/observables.html",
                            controller: 'eventObservableController',
                            resolve: {
                              observables: function(Restangular,$routeSegment) {
                                return Restangular.one("event",$routeSegment.$routeParams.id).all('observable').getList({"complete": true, "inflated": true}).then(function (data) {
                                  return data;
                                }, function(response) {
                                    throw generateErrorMessage(response);
                                });
                              }
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("indicators", {
                            templateUrl: "pages/events/event/indicators.html",
                            controller: 'eventIndicatorController',
                            resolve: {
                              indicators: function(Restangular,$routeSegment) {
                                return Restangular.one("event",$routeSegment.$routeParams.id).all('indicator').getList({"complete": true, "inflated": true}).then(function (data) {
                                  return data;
                                }, function(response) {
                                    throw generateErrorMessage(response);
                                });
                              }
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("reports", {
                            templateUrl: "pages/events/event/reports.html",
                            controller: 'eventReportController',
                            resolve: {
                              reports: function(Restangular,$routeSegment) {
                                return Restangular.one("event",$routeSegment.$routeParams.id).all('report').getList({"complete": true, 'inflated':true}).then(function (data) {
                                  return data;
                                }, function(response) {
                                    throw generateErrorMessage(response);
                                });
                              }
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("relations", {
                            templateUrl: "pages/events/event/relations.html",
                            controller: 'eventRelationsController',
                            resolve: {
                              relations: function(Restangular,$routeSegment) {
                                return Restangular.one("event",$routeSegment.$routeParams.id).all('relations').getList({"complete": true}).then(function (data) {
                                  return data;
                                }, function(response) {
                                    throw generateErrorMessage(response);
                                });
                              }
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("groups", {
                            templateUrl: "pages/events/event/groups.html",
                            dependencies: ["id"],
                            controller: 'eventGroupController',
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                        .up()
                        .segment("unpublished", {
                                 templateUrl: "pages/events/unpublished.html"
                        })
                        .within()
                          .segment("uevents", {
                              'default': true,
                               templateUrl: "pages/events/unpublished/uevents.html"
                          })
                          .segment("observables", {
                                   templateUrl: "pages/events/unpublished/observables.html"
                          })
                          .segment("objects", {
                                   templateUrl: "pages/events/unpublished/objects.html"
                          })
                          .segment("attributes", {
                                   templateUrl: "pages/events/unpublished/attributes.html"
                          })
                        .up()
                        .segment("serach", {
                          templateUrl: "pages/events/serach.html",
                          controller : "serachController",
                          resolve: {
                            attributes: function(Restangular,$routeSegment) {
                              return Restangular.one("search").all('attributes').getList({"complete": true}).then(function (data) {
                                return data;
                              }, function(response) {
                                  throw generateErrorMessage(response);
                              });
                            }
                              
                              
                              
                          },
                          untilResolved: {
                            templateUrl: 'pages/common/loading.html',
                            controller: 'loadingController'
                          },
                          resolveFailed: {
                            templateUrl: 'pages/common/error.html',
                            controller: 'errorController'
                          }
                        })
                        .segment("add", {
                            templateUrl: "pages/events/add.html",
                            controller : "addEventController",
                            resolve: {
                              
                            },
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                            
                        })
                 .up()
                  .segment("admin", {
                        templateUrl : "pages/admin.html",
                      })
                        .within()
                          .segment("mail", {
                                   templateUrl: "pages/admin/mailmgt.html",
                                   controller : "mailController",
                                   resolve: {
                                     mails: function(Restangular) {
                                       return Restangular.one("mail").getList(null, {"complete": false}).then(function (mails) {
                                         return mails;
                                       }, function(response) {
                                           throw generateErrorMessage(response);
                                       });
                                     }
                                   },
                                   untilResolved: {
                                     templateUrl: 'pages/common/loading.html',
                                     controller: 'loadingController'
                                   },
                                   resolveFailed: {
                                     templateUrl: 'pages/common/error.html',
                                     controller: 'errorController'
                                   }
                          })
                            .within()
                               .segment("help", {
                              "default": true,
                              templateUrl: "pages/admin/mail/help.html"})
                              
                              .segment("mailDetails", {
                              templateUrl: "pages/admin/mail/maildetail.html",
                              controller: 'mailDetailController',
                              resolve: {
                                $mail: function(Restangular,$routeSegment) {
                                  return Restangular.one("mail",$routeSegment.$routeParams.id).get({"complete": true}).then(function (mails) {
                                    return mails;
                                  }, function(response) {
                                      throw generateErrorMessage(response);
                                  });
                                }
                              },
                              dependencies: ["id"],
                              untilResolved: {
                                templateUrl: 'pages/common/loading.html',
                                controller: 'loadingController'
                              },
                              resolveFailed: {
                                templateUrl: 'pages/common/error.html',
                                controller: 'errorController'
                              }
                              })
                              
                            .up()
                              .segment("reference", {
                                   templateUrl: "pages/admin/referencemgt.html",
                                   controller : "referenceController",
                                   resolve: {
                                     references: function(Restangular) {
                                       return Restangular.one("referencedefinition").getList(null, {"complete": false}).then(function (mails) {
                                         return mails;
                                       }, function(response) {
                                           throw generateErrorMessage(response);
                                       });
                                     },
                                     handlers: function(Restangular) {
                                       return Restangular.one("referencehandlers").getList(null, {"complete": false}).then(function (handlers) {
                                         return handlers;
                                       }, function(response) {
                                           throw generateErrorMessage(response);
                                       });
                                     },
                                   },
                                   untilResolved: {
                                     templateUrl: 'pages/common/loading.html',
                                     controller: 'loadingController'
                                   },
                                   resolveFailed: {
                                     templateUrl: 'pages/common/error.html',
                                     controller: 'errorController'
                                   }
                          })
                            .within()
                               .segment("help", {
                              "default": true,
                              templateUrl: "pages/admin/references/help.html"})
                              
                              .segment("referenceDetails", {
                              templateUrl: "pages/admin/references/referencedetail.html",
                              controller: 'referenceDetailController',
                              resolve: {
                                $reference: function(Restangular,$routeSegment) {
                                  return Restangular.one("referencedefinition",$routeSegment.$routeParams.id).get({"complete": true}).then(function (references) {
                                    return references;
                                  }, function(response) {
                                      throw generateErrorMessage(response);
                                  });
                                }
                              },
                              dependencies: ["id"],
                              untilResolved: {
                                templateUrl: 'pages/common/loading.html',
                                controller: 'loadingController'
                              },
                              resolveFailed: {
                                templateUrl: 'pages/common/error.html',
                                controller: 'errorController'
                              }
                              })
                              
                            .up()
                        .segment("validation", {
                               templateUrl: "pages/admin/validation.html",
                               controller: "adminValidationController",
                               resolve: {
                                 eventmenus: function(Restangular) {
                                   return Restangular.oneUrl("eventmenus", "/menus/event_links").getList().then(function(eventmenus) {
                                     return eventmenus;
                                   }, function(response) {
                                     throw generateErrorMessage(response);
                                   });
                                 },
                                 statuses: function(Restangular) {
                                   return Restangular.one("statuses").getList(null, {"complete": true}).then(function (items) {
                                     return items;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 risks: function(Restangular) {
                                   return Restangular.one("risks").getList(null, {"complete": true}).then(function (items) {
                                     return items;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 tlps: function(Restangular) {
                                   return Restangular.one("tlps").getList(null, {"complete": true}).then(function (items) {
                                     return items;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 analyses: function(Restangular) {
                                   return Restangular.one("analyses").getList(null, {"complete": true}).then(function (items) {
                                     return items;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 }
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html',
                                 controller: 'loadingController'
                               },
                               resolveFailed: {
                                 templateUrl: 'pages/common/error.html',
                                 controller: 'errorController'
                               }
                        })
                          .within()
                            .segment("all", {
                              'default': true,
                               templateUrl: "pages/events/all.html",
                               controller: 'adminValidationsController'
                            })
                            .segment("event", {
                                 templateUrl: "pages/admin/validation/event/layout.html",
                                 controller: 'viewEventController',
                                 resolve: {
                                   $event: function(Restangular,$routeSegment) {
                                     return Restangular.one("event",$routeSegment.$routeParams.id).get({"complete": true}).then(function (data) {
                                       return data;
                                     }, function(response) {
                                         throw generateErrorMessage(response);
                                     });
                                   },
                                  groups: function(Restangular) {
                                    return Restangular.one("groups").getList(null, {"complete": true}).then(function (groups) {
                                      return groups;
                                    }, function(response) {
                                      return [];
                                    });
                                  }
                                 },
                                 dependencies: ["id"],
                                 untilResolved: {
                                   templateUrl: 'pages/common/loading.html',
                                   controller: 'loadingController'
                                 },
                                 resolveFailed: {
                                   templateUrl: 'pages/common/error.html',
                                   controller: 'errorController'
                                 }
                        })
                        .within()
                          .segment("overview", {
                            'default': true,
                            templateUrl: "pages/events/event/overview.html",
                            controller: 'eventOverviewController',
                            resolve: {
                              useradmin: function(Restangular,$routeSegment) {
                                return Restangular.one("checks","isuseradmin").get().then(function (data) {
                                  return data;
                                }, function(response) {
                                  return false;
                                });
                              },
                              relations: function(Restangular,$routeSegment) {
                                return Restangular.one("event",$routeSegment.$routeParams.id).all("relations").getList({'complete':false}).then(function (data) {
                                  return data;
                                }, function(response) {
                                  return false;
                                });
                              },
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("observables", {
                            templateUrl: "pages/events/event/observables.html",
                            controller: 'eventObservableController',
                            resolve: {
                              observables: function(Restangular,$routeSegment) {
                                return Restangular.one("event",$routeSegment.$routeParams.id).all('observable').getList({"complete": true, "inflated": true}).then(function (data) {
                                  return data;
                                }, function(response) {
                                    throw generateErrorMessage(response);
                                });
                              }
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("indicators", {
                            templateUrl: "pages/events/event/indicators.html",
                            controller: 'eventIndicatorController',
                            resolve: {
                              indicators: function(Restangular,$routeSegment) {
                                return Restangular.one("event",$routeSegment.$routeParams.id).all('indicator').getList({"complete": true, "inflated": true}).then(function (data) {
                                  return data;
                                }, function(response) {
                                    throw generateErrorMessage(response);
                                });
                              }
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("reports", {
                            templateUrl: "pages/events/event/reports.html",
                            controller: 'eventReportController',
                            resolve: {
                              reports: function(Restangular,$routeSegment) {
                                return Restangular.one("event",$routeSegment.$routeParams.id).all('report').getList({"complete": true}).then(function (data) {
                                  return data;
                                }, function(response) {
                                    throw generateErrorMessage(response);
                                });
                              }
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("relations", {
                            templateUrl: "pages/events/event/relations.html",
                            controller: 'eventRelationsController',
                            resolve: {
                              relations: function(Restangular,$routeSegment) {
                                return Restangular.one("event",$routeSegment.$routeParams.id).all('relations').getList({"complete": true}).then(function (data) {
                                  return data;
                                }, function(response) {
                                    throw generateErrorMessage(response);
                                });
                              }
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("groups", {
                            templateUrl: "pages/events/event/groups.html",
                            dependencies: ["id"],
                            controller: 'eventGroupController',
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                        .up()
                        .up()
                        .segment("type", {
                               templateUrl: "pages/admin/typesmgt.html",
                               controller : "typesController",
                               resolve: {
                                 types: function(Restangular) {
                                   return Restangular.one("attributetypes").getList(null, {"complete": false}).then(function (objects) {
                                     return objects;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                datatypes: function(Restangular) {
                                  return Restangular.one("attributetables").getList(null, {"complete": false}).then(function (tables) {
                                    return tables;
                                  }, function(response) {
                                      throw generateErrorMessage(response);
                                  });
                                }
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html',
                                 controller: 'loadingController'
                               },
                               resolveFailed: {
                                 templateUrl: 'pages/common/error.html',
                                 controller: 'errorController'
                               }
                        })
                          .within()
                             .segment("help", {
                                 "default": true,
                                 templateUrl: "pages/admin/type/help.html"})
                          
                                 .segment("typeDetails", {
                                     templateUrl: "pages/admin/type/typedetail.html",
                                     controller: "typeDetailController",
                                     resolve: {
                                       $type: function(Restangular,$routeSegment) {
                                         return Restangular.one("attributetypes",$routeSegment.$routeParams.id).get({"complete": true}).then(function (object) {
                                           return object;
                                         }, function(response) {
                                             throw generateErrorMessage(response);
                                         });
                                       },
                                     },
                                     dependencies: ["id"],
                                     untilResolved: {
                                       templateUrl: 'pages/common/loading.html',
                                       controller: 'loadingController'
                                     },
                                     resolveFailed: {
                                       templateUrl: 'pages/common/error.html',
                                       controller: 'errorController'
                                     }
                                 })
                          
                         .up()
                        .segment("object", {
                               templateUrl: "pages/admin/objmgt.html",
                               controller : "objectController",
                               resolve: {
                                 objects: function(Restangular) {
                                   return Restangular.one("objectdefinition").getList(null, {"complete": false}).then(function (objects) {
                                     return objects;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 }
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html',
                                 controller: 'loadingController'
                               },
                               resolveFailed: {
                                 templateUrl: 'pages/common/error.html',
                                 controller: 'errorController'
                               }
                        })
                          .within()
                             .segment("help", {
                                 "default": true,
                                 templateUrl: "pages/admin/object/help.html"})
                          
                                 .segment("objectDetails", {
                                     templateUrl: "pages/admin/object/objectdetail.html",
                                     controller: "objectDetailController",
                                     resolve: {
                                       $object: function(Restangular,$routeSegment) {
                                         return Restangular.one("objectdefinition",$routeSegment.$routeParams.id).get({"complete": true, "inflated": true}).then(function (object) {
                                           return object;
                                         }, function(response) {
                                             throw generateErrorMessage(response);
                                         });
                                       },
                                       attributes: function(Restangular) {
                                         return Restangular.one("attributedefinition").getList(null, {"complete": false}).then(function (attributes) {
                                           return attributes;
                                         }, function(response) {
                                             throw generateErrorMessage(response);
                                         });
                                       }
                                     },
                                     dependencies: ["id"],
                                     untilResolved: {
                                       templateUrl: 'pages/common/loading.html',
                                       controller: 'loadingController'
                                     },
                                     resolveFailed: {
                                       templateUrl: 'pages/common/error.html',
                                       controller: 'errorController'
                                     }
                                 })
                          
                         .up()
                      .segment("attribute", {
                               templateUrl: "pages/admin/attrmgt.html",
                               controller : "attributeController",
                               resolve: {
                                 attributes: function(Restangular) {
                                   return Restangular.one("attributedefinition").getList(null, {"complete": false}).then(function (attributes) {
                                     return attributes;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 conditions: function(Restangular) {
                                   return Restangular.one("condition").getList(null, {"complete": false}).then(function (condtitions) {
                                     return condtitions;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 handlers: function(Restangular) {
                                   return Restangular.one("attributehandlers").getList(null, {"complete": false}).then(function (handlers) {
                                     return handlers;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 tables: function(Restangular) {
                                   return Restangular.one("attributetables").getList(null, {"complete": false}).then(function (tables) {
                                     return tables;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 types: function(Restangular) {
                                   return Restangular.one("attributetypes").getList(null, {"complete": false}).then(function (tables) {
                                     return tables;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html',
                                 controller: 'loadingController'
                               },
                               resolveFailed: {
                                 templateUrl: 'pages/common/error.html',
                                 controller: 'errorController'
                               }
                      })
                        .within()
                           .segment("help", {
                               "default": true,
                               templateUrl: "pages/admin/attribute/help.html"})
                          
                           .segment("attributeDetails", {
                             templateUrl: "pages/admin/attribute/attributedetail.html",
                             controller: "attributeDetailController",
                             resolve: {
                               $attribute: function(Restangular,$routeSegment) {
                                 return Restangular.one("attributedefinition",$routeSegment.$routeParams.id).get({"complete": true, "inflated": true}).then(function (attribute) {
                                   return attribute;
                                 }, function(response) {
                                     throw generateErrorMessage(response);
                                 });
                               },
                               objects: function(Restangular) {
                                 return Restangular.all("objectdefinition").getList(null, {"complete": false}).then(function (objects) {
                                   return objects;
                                 }, function(response) {
                                     throw generateErrorMessage(response);
                                 });
                               }
                             },
                             dependencies: ["id"],
                             untilResolved: {
                               templateUrl: 'pages/common/loading.html',
                               controller: 'loadingController'
                             },
                             resolveFailed: {
                               templateUrl: 'pages/common/error.html',
                               controller: 'errorController'
                             }
                           })
                           .up()
                        
                      .segment("user", {
                               templateUrl: "pages/admin/usermgt.html",
                               controller : "userController",
                               resolve: {
                                 groups: function(Restangular) {
                                   return Restangular.one("group").getList(null, {"complete": false}).then(function (groups) {
                                     return groups;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 showLdapBtn: function(Restangular) {
                                   return Restangular.oneUrl("ldapusers", "/plugins/is_plugin_avaibable/ldap").get().then(function (ldapusers) {
                                     if (ldapusers) {
                                       return true;
                                     } else {
                                       return false;
                                     }
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 users: function(Restangular,$routeSegment) {
                                   return Restangular.one("user").getList(null, {"complete": false}).then(function (users) {
                                     return users;
                                   
                                   }, function(response) {
                                     throw generateErrorMessage(response);
                                   });
                                 }
                                 
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html',
                                 controller: 'loadingController'
                               },
                               resolveFailed: {
                                 templateUrl: 'pages/common/error.html',
                                 controller: 'errorController'
                               }
                              
                      })
                        .within()
                           .segment("help", {
                          "default": true,
                          templateUrl: "pages/admin/user/help.html"})
                          
                          .segment("userDetails", {
                          templateUrl: "pages/admin/user/userdetail.html",
                          controller: "userDetailController",
                          resolve: {
                            $user: function(Restangular,$routeSegment) {
                              return Restangular.one("user",$routeSegment.$routeParams.id).get({"complete": true}).then(function (user) {
                                return user;
                              }, function(response) {
                                  throw generateErrorMessage(response);
                              });
                            },
                            showMailBtn: function(Restangular) {
                              return Restangular.oneUrl("mailing", "/plugins/is_plugin_avaibable/mail").get().then(function (data) {
                                if (data) {
                                  return true;
                                } else {
                                  return false;
                                }
                              }, function(response) {
                                  throw generateErrorMessage(response);
                              });
                            },
                          },
                          dependencies: ["id"],
                          untilResolved: {
                            templateUrl: 'pages/common/loading.html',
                            controller: 'loadingController'
                          },
                          resolveFailed: {
                            templateUrl: 'pages/common/error.html',
                            controller: 'errorController'
                          }
                          })
                        .up()
                          .segment("condition", {
                               templateUrl: "pages/admin/conditionmgt.html",
                               controller : "conditionController",
                               resolve: {
                                 conditions: function(Restangular) {
                                   return Restangular.one("condition").getList(null, {"complete": false}).then(function (conditions) {
                                     return conditions;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 }
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html',
                                 controller: 'loadingController'
                               },
                               resolveFailed: {
                                 templateUrl: 'pages/common/error.html',
                                 controller: 'errorController'
                               }
                              
                        })
                          .within()
                             .segment("help", {
                            "default": true,
                            templateUrl: "pages/admin/condition/help.html"})
                            
                            .segment("conditionDetails", {
                            templateUrl: "pages/admin/condition/conditiondetail.html",
                            controller: "conditionDetailController",
                            resolve: {
                              $condition: function(Restangular,$routeSegment) {
                                return Restangular.one("condition",$routeSegment.$routeParams.id).get({"complete": true}).then(function (condition) {
                                  return condition;
                                }, function(response) {
                                    throw generateErrorMessage(response);
                                });
                              }
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html',
                              controller: 'loadingController'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                            })
                          .up()
         
                          .segment("syncservers", {
                               templateUrl: "pages/admin/syncservers.html",
                               controller: "SyncMainServersController",
                               resolve: {
                                 servertypes: function(Restangular) {
                                   return Restangular.one("servertypes").getList(null, {"complete": true}).then(function (servertypes) {
                                     return servertypes;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 syncservers: function(Restangular) {
                                   return Restangular.one("syncservers").getList(null, {"complete": true}).then(function (syncservers) {
                                     return syncservers;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 users: function(Restangular,$routeSegment) {
                                   return Restangular.one("user").getList(null, {"complete": false}).then(function (users) {
                                     return users;
                                   
                                   }, function(response) {
                                     throw generateErrorMessage(response);
                                   });
                                 }
                          
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html',
                                 controller: 'loadingController'
                               },
                               resolveFailed: {
                                 templateUrl: 'pages/common/error.html',
                                 controller: 'errorController'
                               }
                        })
                        .within()
                           .segment("help", {
                          "default": true,
                          templateUrl: "pages/admin/syncservers/help.html"})
                          
                          .segment("servers", {
                          templateUrl: "pages/admin/syncservers/servers.html",
                          controller: "SyncServersController",
                          resolve: {
                            
                          },
                          untilResolved: {
                            templateUrl: 'pages/common/loading.html',
                            controller: 'loadingController'
                          },
                          resolveFailed: {
                            templateUrl: 'pages/common/error.html',
                            controller: 'errorController'
                          }
                          })
                          
                        .up()
                        
                        .segment("bgjobs", {
                               templateUrl: "pages/admin/bgjobs.html",
                               controller: "MainJobscontroller",
                               resolve: {
                                 jobs: function(Restangular) {
                                   return Restangular.one("processes").getList(null, {"complete": true}).then(function (jobs) {
                                     return jobs;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 }
                          
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html',
                                 controller: 'loadingController'
                               },
                               resolveFailed: {
                                 templateUrl: 'pages/common/error.html',
                                 controller: 'errorController'
                               }
                        })
                        .within()
                           .segment("help", {
                          "default": true,
                          templateUrl: "pages/admin/bgjobs/help.html"})
                          
                          .segment("jobs", {
                          templateUrl: "pages/admin/bgjobs/jobs.html",
                          controller: "Jobscontroller",
                          resolve: {
                            
                          },
                          untilResolved: {
                            templateUrl: 'pages/common/loading.html',
                            controller: 'loadingController'
                          },
                          resolveFailed: {
                            templateUrl: 'pages/common/error.html',
                            controller: 'errorController'
                          }
                          })
                          
                        .up()
                        
                      .segment("group", {
                               templateUrl: "pages/admin/groupmgt.html",
                               controller : "groupController",
                               resolve: {
                                 groups: function(Restangular) {
                                   return Restangular.one("group").getList(null, {"complete": false}).then(function (groups) {
                                     return groups;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 tlps: function(Restangular) {
                                   return Restangular.one("tlps").getList(null, {"complete": false}).then(function (tlps) {
                                     return tlps;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 }
                      
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html',
                                 controller: 'loadingController'
                               },
                               resolveFailed: {
                                 templateUrl: 'pages/common/error.html',
                                 controller: 'errorController'
                               }
                      })
                        .within()
                           .segment("help", {
                          "default": true,
                          templateUrl: "pages/admin/group/help.html"})
                          
                          .segment("groupDetails", {
                          templateUrl: "pages/admin/group/groupdetail.html",
                          controller: "groupDetailController",
                          resolve: {
                            $group: function(Restangular,$routeSegment) {
                              return Restangular.one("group",$routeSegment.$routeParams.id).get({"complete": true}).then(function (user) {
                                return user;
                              }, function(response) {
                                  throw generateErrorMessage(response);
                              });
                            }
                          },
                          dependencies: ["id"],
                          untilResolved: {
                            templateUrl: 'pages/common/loading.html',
                            controller: 'loadingController'
                          },
                          resolveFailed: {
                            templateUrl: 'pages/common/error.html',
                            controller: 'errorController'
                          }
                          })
                          
                        .up()
                        
                     .up()
             .up()
        .up();
    $routeProvider.otherwise({redirectTo: '/'}); 
});

app.config(['growlProvider', function(growlProvider) {
  growlProvider.globalReversedOrder(true);
  growlProvider.globalTimeToLive({success: 2000, error: 10000, warning: 5000, info: 3000});
}]);