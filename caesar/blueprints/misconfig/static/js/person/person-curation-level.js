'use strict';

WebMis20
.controller('PersonCurationConfigCtrl', ['$scope', '$controller', 'Person',
        function ($scope, $controller, Person) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.model = {};
    $scope.startEditing = function (key) {
        $scope.model[key].editing = true;
    };
    $scope.cancelEditing = function (key) {
        $scope.model[key].editing = false;
    };
    $scope.finishEditing = function (key) {
        $scope.model[key].person.save(undefined, undefined, {
            with_curations: true
        }).then(function (person) {
            $scope.model[key].person = person;
            $scope.cancelEditing(key);
        });
    };
    $scope.inEditState = function (key) {
        return $scope.model[key].editing;
    };
    $scope.btnAddCurationAvailable = function (key) {
        return $scope.model[key].newCuration !== null && !$scope.model[key].curationDubl;
    };
    $scope.addPersonCuration = function (key) {
        var person = $scope.model[key].person;
        person.curation_levels.push($scope.model[key].newCuration);
        $scope.model[key].newCuration = null;
    };
    $scope.removePersonCuration = function (key, idx) {
        $scope.model[key].person.curation_levels.splice(idx, 1);
    };
    $scope.checkCurationDubl = function (key) {
        var selected = $scope.model[key].person.curation_levels.map(function (cl) { return cl.id; });
        $scope.model[key].curationDubl = selected.has($scope.model[key].newCuration.id);
    };
    $scope.alertCurationDublVisible = function (key) {
        return $scope.model[key].curationDubl;
    };

    Person.instantiateAll({
        with_curations: true
    }).then(function (persons) {
        $scope.model = {};
        angular.forEach(persons, function (person, key) {
            $scope.model[key] = {
                person: person,
                editing: false,
                newCuration: null,
                curationDubl: false
            };
        });
    });
}])
;