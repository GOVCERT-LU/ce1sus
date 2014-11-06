/**
 * 
 */

var queue = [];

app.config(function($routeSegmentProvider, $routeProvider, RestangularProvider, messageQueueProvider) {
    
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
        .when("/events/recent", "main.layout.events.recent")
        .when("/events/all", "main.layout.events.allEvents")
        .when("/events/unpublished", "main.layout.events.unpublished")
        .when("/events/unpublishedProposals", "main.layout.events.uproposals")
        .when("/events/search", "main.layout.events.serach")
        .when("/events/add", "main.layout.events.add")
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
                          var test = eventmenus;
                          return eventmenus;
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
                        .segment("recentEvents", {
                                 'default': true,
                                 templateUrl: "pages/events/recent.html"
                        })
                        .segment("allEvents", {
                                 templateUrl: "pages/events/all.html"
                        })
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
                                 templateUrl: "pages/events/add.html"
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
                                       return Restangular.one("mail").getList(null, null, {"Complete": false}).then(function (mails) {
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
                                  return Restangular.one("mail",$routeSegment.$routeParams.id).get(null, null, {"Complete": true}).then(function (mails) {
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
                        .segment("object", {
                               templateUrl: "pages/admin/objmgt.html",
                               controller : "objectController",
                               resolve: {
                                 objects: function(Restangular) {
                                   return Restangular.one("object").getList(null, null, {"Complete": false}).then(function (objects) {
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
                                         return Restangular.one("object",$routeSegment.$routeParams.id).get(null, null, {"Complete": true}).then(function (object) {
                                           return object;
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
                                   return Restangular.one("attribute").getList(null, null, {"Complete": false}).then(function (attributes) {
                                     return attributes;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 handlers: function(Restangular) {
                                   return Restangular.one("handlers").getList(null, null, {"Complete": false}).then(function (handlers) {
                                     return handlers;
                                   }, function(response) {
                                       throw generateErrorMessage(response);
                                   });
                                 },
                                 tables: function(Restangular) {
                                   return Restangular.one("tables").getList(null, null, {"Complete": false}).then(function (tables) {
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
                                 return Restangular.one("attribute",$routeSegment.$routeParams.id).get(null, null, {"Complete": true}).then(function (attribute) {
                                   return attribute;
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
                                   return Restangular.one("group").getList(null, null, {"Complete": false}).then(function (groups) {
                                     return data;
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
                                   return Restangular.one("user").getList(null, null, {"Complete": false}).then(function (users) {
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
                              return Restangular.one("user",$routeSegment.$routeParams.id).get(null, null, {"Complete": true}).then(function (user) {
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
                                   return Restangular.one("group").getList(null, null, {"Complete": false}).then(function (groups) {
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
                              return Restangular.one("group",$routeSegment.$routeParams.id).get(null, null, {"Complete": true}).then(function (user) {
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