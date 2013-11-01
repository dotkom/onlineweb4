var app = angular.module('rfid', [
    'ng',
    'ngRoute'
    ]
);

app.config(function($routeProvider) {
    
    $routeProvider.when('/', {
        templateUrl: "../index.html",
        controller: "mainCtrl"
    }).when('/events', {
        templateUrl: "../views/events.html",
        controller: "controllers.eventCtrl"
    }).when('/events/:eventID', {
        templateUrl: "../views/event_detail.html",
        controller: "controllers.eventDetailCtrl"
    }).otherwise({
        redirectTo: '/'
    });
});

app.directive('alertable', function() {
    return {
        restrict : 'A',
        link: function(scope, element, attrs) {
            element.bind('click', function() {
                alert(attrs.alertable);
            });
        }
    };
});

app.factory('PersonService', function () {
    var PersonService = {};
    PersonService.people = [];
    PersonService.addPerson = function(person) {
        PersonService.people.push(person);
    };
    return PersonService;
});
