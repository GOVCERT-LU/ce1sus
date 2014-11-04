/**
 * 
 */



var queue = [];
// configure our routes
ce1susApp.config(function($routeSegmentProvider, $routeProvider,
    RestangularProvider, messageQueueProvider) {
  
  messageQueueProvider.setQueue(queue);

  // Configuring provider options

  $routeSegmentProvider.options.autoLoadTemplates = true;

  // Setting routes. This consists of two parts:
  // 1. `when` is similar to vanilla $route `when` but takes segment name
  // instead of params hash
  // 2. traversing through segment tree to set it up
  RestangularProvider.setBaseUrl("/REST/0.3.0");
  // RestangularProvider.setDefaultRequestParams({ apiKey:
  // "4f847ad3e4b08a2eed5f3b54" })
  RestangularProvider.setRestangularFields({
    id : "identifier"
  });

  $routeSegmentProvider
    .when("/home", "home")
    .when("/login", "login")
    .when("/logout", "logout")
    .when("/about", "about")
    .when("/events", "events")
    .when("/events/all", "events.allEvents")
    .when("/events/unpublished", "events.unpublished")
    .when("/events/unpublishedProposals", "events.uproposals")
    .when("/events/search", "events.serach")
    .when("/events/add", "events.add")

    .segment("home", {
      templateUrl : "pages/home.html",
      controller : "mainController"
    })

    .segment("login", {
      templateUrl : "pages/login.html",
      controller : "loginController"

    })

    .segment("logout", {
      templateUrl : "pages/logout.html",
      controller : "logoutController"

    })

    .segment("about", {
      templateUrl : "pages/about.html"
    })

    .segment("events", {
      templateUrl : "pages/events.html",
      controller : "eventController"
    })
      .within()
        .segment("recentEvents", {
                 "default": true,
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

    .when("/admin", "admin")
    .when("/admin/validation", "admin.validation")
    .when("/admin/objAttrMgt", "admin.objAttrMgt")
    .when("/admin/user", "admin.user")
    .when("/admin/user/:id", "admin.user.userDetails")
    .when("/admin/group", "admin.group")
    .when("/admin/group/:id", "admin.group.groupDetails")
    .when("/admin/mailMgt", "admin.mailMgt")
    .when("/admin/object", "admin.object")
    .when("/admin/object/:id", "admin.object.objectDetails")
    .when("/admin/attribute", "admin.attribute")
    .when("/admin/attribute/:id", "admin.attribute.attributeDetails")
    .when("/admin/mail", "admin.mail")
    .when("/admin/mail/:id", "admin.mail.mailDetails")
    
    
     
    .segment("admin", {
      templateUrl : "pages/admin.html",
      controller : "eventController"
    })
      .within()
        .segment("validation", {
                 "default": true,
                 templateUrl: "pages/admin/validation.html"
        })
        .segment("object", {
                 templateUrl: "pages/admin/objmgt.html",
                 controller : "objectController"
        })
          .within()
             .segment("help", {
            "default": true,
            templateUrl: "pages/admin/object/help.html"})
            
            .segment("objectDetails", {
            templateUrl: "pages/admin/object/objectdetail.html",
            controller: "objectDetailController",
            dependencies: ["id"],
            resolve: {
              data: function($timeout) {
              return $timeout(function() { return 'SLOW DATA CONTENT'; }, 2000);
              }
            },
            resolveFailed : {
              templateUrl : "pages/common/error.html",
   
            }
            })
            
          .up()
        .segment("attribute", {
                 templateUrl: "pages/admin/attrmgt.html",
                 controller : "attributeController"
        })
          .within()
             .segment("help", {
            "default": true,
            templateUrl: "pages/admin/attribute/help.html"})
            
            .segment("attributeDetails", {
            templateUrl: "pages/admin/attribute/attributedetail.html",
            controller: "attributeDetailController",
            dependencies: ["id"]
            })
            
          .up()
          
        .segment("user", {
                 templateUrl: "pages/admin/usermgt.html",
                 controller : "userController"
        })
          .within()
             .segment("help", {
            "default": true,
            templateUrl: "pages/admin/user/help.html"})
            
            .segment("userDetails", {
            templateUrl: "pages/admin/user/userdetail.html",
            controller: "userDetailController",
            dependencies: ["id"]
            })
            
          .up()
        .segment("group", {
                 templateUrl: "pages/admin/groupmgt.html",
                 controller : "groupController"
        })
          .within()
             .segment("help", {
            "default": true,
            templateUrl: "pages/admin/group/help.html"})
            
            .segment("groupDetails", {
            templateUrl: "pages/admin/group/groupdetail.html",
            controller: "groupDetailController",
            dependencies: ["id"]
            })
            
          .up()
        .segment("mail", {
                 templateUrl: "pages/admin/mailmgt.html",
                 controller : "mailController"
        })
          .within()
             .segment("help", {
            "default": true,
            templateUrl: "pages/admin/mail/help.html"})
            
            .segment("mailDetails", {
            templateUrl: "pages/admin/mail/maildetail.html",
            controller: "mailDetailController",
            dependencies: ["id"]
            })
            
          .up()
     .up();
  // Also, we can add new item in a deep separately. This is useful when working
  // with
  // routes in every module individually

  $routeSegmentProvider

  .when("/events/:id/Z", "events.itemInfo.tab3")

  .within("events").within("itemInfo").segment("tab3", {
    templateUrl : "templates/section1/tabs/tab3.html"
  });

  // This is some usage of `resolve`, `untilResolved` and `resolveFailed`
  // features

  $routeSegmentProvider

  .when("/invalid-template", "events.invalidTemplate").when("/invalid-data",
      "events.invalidData").when("/slow-data", "events.slowDataSimple").when(
      "/slow-data-loading", "events.slowDataLoading").when("/inline-view",
      "events.inlineParent")
      .when("/events/:id/slow", "events.itemInfo.tabSlow")

      .within("events").segment("invalidTemplate", {
        templateUrl : "this-does-not-exist.html", // 404
        resolveFailed : {
          templateUrl : "templates/error.html",
          controller : "ErrorCtrl"
        }
      }).segment("invalidData", {
        templateUrl : "templates/section1/home.html", // Correct!
        resolve : {
          data : function($q) {
            return $q.reject("ERROR DESCRIPTION"); // Failed to load data
          }
        },
        resolveFailed : {
          templateUrl : "templates/error.html",
          controller : "ErrorCtrl"
        }
      }).segment("slowDataSimple", {
        templateUrl : "templates/section1/slow-data.html",
        controller : "SlowDataCtrl",
        resolve : {
          data : function($timeout, cfpLoadingBar) {
            cfpLoadingBar.start();
            return $timeout(function() {
              cfpLoadingBar.complete();
              return "SLOW DATA CONTENT";
            }, 2000);
          }
        }
      })
      // Dessen ass sou wei et sollt ausgesinn!!!!
      .segment("slowDataLoading", {
        templateUrl : "templates/section1/slow-data.html",
        controller : "SlowDataCtrl",
        resolve : {
          data : function($timeout, cfpLoadingBar) {
            cfpLoadingBar.start();
            return $timeout(function() {
              cfpLoadingBar.complete();
              return "SLOW DATA CONTENT";
            }, 2000);
          }
        },
        untilResolved : {
          templateUrl : "pages/common/loading.html"
        },
        resolveFailed : {
          templateUrl : "templates/error.html",
          controller : "ErrorCtrl"
        }
      }).segment("inlineParent", {
        templateUrl : "templates/section1/inline-view.html"
      }).within().segment("inlineChildren", {
        // no template here
        controller : "SlowDataCtrl",
        "default" : true,
        resolve : {
          data : function($timeout, cfpLoadingBar) {
            cfpLoadingBar.start();
            return $timeout(function(cfpLoadingBar) {
              cfpLoadingBar.complete();
              return "SLOW DATA CONTENT";
            }, 2000);
          }
        },
        untilResolved : {
          templateUrl : "pages/common/loading.html"
        },
        resolveFailed : {
          templateUrl : "templates/error.html",
          controller : "ErrorCtrl"
        }
      }).up()

      .within("itemInfo").segment("tabSlow", {
        templateUrl : "templates/section1/slow-data.html",
        controller : "SlowDataCtrl",
        resolve : {
          data : function($timeout, cfpLoadingBar) {
            cfpLoadingBar.start();
            return $timeout(function() {
              cfpLoadingBar.complete();
              return "SLOW DATA CONTENT";
            }, 2000);
          }
        },
        untilResolved : {
          templateUrl : "pages/common/loading.html"
        },
        resolveFailed : {
          templateUrl : "templates/error.html",
          controller : "ErrorCtrl"
        }
      });

  $routeProvider.otherwise({
    redirectTo : "/home"
  });

});

ce1susApp.config([ "cfpLoadingBarProvider", function(cfpLoadingBarProvider) {
  cfpLoadingBarProvider.includeBar = true;
  cfpLoadingBarProvider.includeSpinner = false;
  cfpLoadingBarProvider.latencyThreshold = 20;

} ]);