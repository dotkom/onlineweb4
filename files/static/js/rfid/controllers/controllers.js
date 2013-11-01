'use strict'

function mainCtrl($scope, PersonService) {
    
    $scope.name = "";
    $scope.addPerson = function () {
        PersonService.addPerson($scope.name);  
    };
    $scope.getPeople = function () {
        return PeopleService.people;
    };
};
