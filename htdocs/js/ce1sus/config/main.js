/**
 * 
 */

var queue = [];

app.config(function($routeSegmentProvider, $routeProvider, RestangularProvider, messageQueueProvider, $scrollspyProvider) {
    
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
        .when("/login", "main.layout.login")
        .when("/logout", "main.layout.logout")
        .when("/about", "main.layout.about")
        .when("/events", "main.layout.events")
        .when("/events/all", "main.layout.events.allEvents")
        .when("/events/unpublished", "main.layout.events.unpublished")
        .when("/events/unpublishedProposals", "main.layout.events.uproposals")
        .when("/events/search", "main.layout.events.serach")
        .when("/events/add", "main.layout.events.add")
        .when("/events/event/:id", "main.layout.events.event")
        .when("/events/event/:id/overview", "main.layout.events.event.overview")
        .when("/events/event/:id/observables", "main.layout.events.event.observables")
        .when("/events/event/:id/indicators", "main.layout.events.event.indicators")
        .when("/events/event/:id/relations", "main.layout.events.event.relations")
        .when("/events/event/:id/groups", "main.layout.events.event.groups")
        .when("/admin", "main.layout.admin")
        .when("/admin/validation", "main.layout.admin.validation")
        .when("/admin/objAttrMgt", "main.layout.admin.objAttrMgt")
        .when("/admin/user", "main.layout.admin.user")
        .when("/admin/user/:id", "main.layout.admin.user.userDetails")
        .when("/admin/group", "main.layout.admin.group")
        .when("/admin/group/:id", "main.layout.admin.group.groupDetails")
        .when("/admin/mailMgt", "main.layout.admin.mailMgt")
        .when("/admin/object", "main.layout.admin.object")
        .when("/admin/object/:id", "main.layout.admin.object.objectDetails")
        .when("/admin/type", "main.layout.admin.type")
        .when("/admin/type/:id", "main.layout.admin.type.typeDetails")
        .when("/admin/viewtype", "main.layout.admin.viewType")
        .when("/admin/viewtype/:id", "main.layout.admin.viewType.viewTypeDetails")
        .when("/admin/attribute", "main.layout.admin.attribute")
        .when("/admin/attribute/:id", "main.layout.admin.attribute.attributeDetails")
        .when("/admin/mail", "main.layout.admin.mail")
        .when("/admin/mail/:id", "main.layout.admin.mail.mailDetails")
    
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
                    templateUrl: 'pages/common/loading.html'
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
                       templateUrl: 'pages/common/loading.html'
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
                  .segment('about', {
                    templateUrl : "pages/about.html"
                  })
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
                        templateUrl: 'pages/common/loading.html'
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
                                   }
                                 },
                                 dependencies: ["id"],
                                 untilResolved: {
                                   templateUrl: 'pages/common/loading.html'
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
                              groups: function(Restangular) {
                                return Restangular.one("groups").getList(null, {"complete": false}).then(function (groups) {
                                  return groups;
                                }, function(response) {
                                  return [];
                                });
                              }
                            },
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html'
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
                              templateUrl: 'pages/common/loading.html'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("indicators", {
                            templateUrl: "pages/events/event/indicators.html",
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("relations", {
                            templateUrl: "pages/events/event/relations.html",
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html'
                            },
                            resolveFailed: {
                              templateUrl: 'pages/common/error.html',
                              controller: 'errorController'
                            }
                          })
                          .segment("groups", {
                            templateUrl: "pages/events/event/groups.html",
                            dependencies: ["id"],
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html'
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
                        .segment("uproposals", {
                                 templateUrl: "pages/events/unpublishedProposals.html"
                        })
                        .segment("serach", {
                                 templateUrl: "pages/events/serach.html"
                        })
                        .segment("add", {
                            templateUrl: "pages/events/add.html",
                            controller : "addEventController",
                            resolve: {
                              
                            },
                            untilResolved: {
                              templateUrl: 'pages/common/loading.html'
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
                                     templateUrl: 'pages/common/loading.html'
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
                                templateUrl: 'pages/common/loading.html'
                              },
                              resolveFailed: {
                                templateUrl: 'pages/common/error.html',
                                controller: 'errorController'
                              }
                              })
                              
                            .up()
                        .segment("validation", {
                               "default": true,
                               templateUrl: "pages/admin/validation.html"
                        })
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
                                 templateUrl: 'pages/common/loading.html'
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
                                       templateUrl: 'pages/common/loading.html'
                                     },
                                     resolveFailed: {
                                       templateUrl: 'pages/common/error.html',
                                       controller: 'errorController'
                                     }
                                 })
                          
                         .up()
                           .segment("viewType", {
                               templateUrl: "pages/admin/viewtypesmgt.html",
                               controller : "viewTypesController",
                               resolve: {
                                 viewTypes: function(Restangular) {
                                   return Restangular.one("attributeviewtypes").getList(null, {"complete": false}).then(function (objects) {
                                     return objects;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 }
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html'
                               },
                               resolveFailed: {
                                 templateUrl: 'pages/common/error.html',
                                 controller: 'errorController'
                               }
                        })
                          .within()
                             .segment("help", {
                                 "default": true,
                                 templateUrl: "pages/admin/viewtype/help.html"})
                          
                                 .segment("viewTypeDetails", {
                                     templateUrl: "pages/admin/viewtype/viewtypedetail.html",
                                     controller: "viewTypeDetailController",
                                     resolve: {
                                       $viewType: function(Restangular,$routeSegment) {
                                         return Restangular.one("attributeviewtypes",$routeSegment.$routeParams.id).get({"complete": true}).then(function (object) {
                                           return object;
                                         }, function(response) {
                                             throw generateErrorMessage(response);
                                         });
                                       },
                                     },
                                     dependencies: ["id"],
                                     untilResolved: {
                                       templateUrl: 'pages/common/loading.html'
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
                                 templateUrl: 'pages/common/loading.html'
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
                                         return Restangular.one("objectdefinition",$routeSegment.$routeParams.id).get({"complete": true}).then(function (object) {
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
                                       templateUrl: 'pages/common/loading.html'
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
                                 viewTypes: function(Restangular) {
                                   return Restangular.one("attributeviewtypes").getList(null, {"complete": false}).then(function (tables) {
                                     return tables;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html'
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
                                 return Restangular.one("attribute",$routeSegment.$routeParams.id).get({"complete": true}).then(function (attribute) {
                                   return attribute;
                                 }, function(response) {
                                     throw generateErrorMessage(response);
                                 });
                               },
                               $attributeObjects: function(Restangular,$routeSegment) {
                                 return Restangular.one("attributedefinition",$routeSegment.$routeParams.id).getList('object').then(function (attribute) {
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
                               templateUrl: 'pages/common/loading.html'
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
                                 templateUrl: 'pages/common/loading.html'
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
                            }
                          },
                          dependencies: ["id"],
                          untilResolved: {
                            templateUrl: 'pages/common/loading.html'
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
                                 }
                               },
                               untilResolved: {
                                 templateUrl: 'pages/common/loading.html'
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
                            templateUrl: 'pages/common/loading.html'
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