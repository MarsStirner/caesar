'use strict';

WebMis20
.controller('OrgCurationConfigCtrl', ['$scope', '$controller', 'Organisation', 'PersonCuration',
        function ($scope, $controller, Organisation, PersonCuration) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.model = {};
    $scope.startEditing = function (key) {
        $scope.model[key].editing = true;
    };
    $scope.cancelEditing = function (key) {
        $scope.model[key].editing = false;
    };
    $scope.finishEditing = function (key) {
        $scope.model[key].org.save(undefined, undefined, {
            with_curations: true
        }).then(function (org) {
            $scope.model[key].org = org;
            $scope.cancelEditing(key);
        });
    };
    $scope.inEditState = function (key) {
        return $scope.model[key].editing;
    };
    $scope.btnAddCurationAvailable = function (key) {
        return $scope.model[key].newCuration !== null && !$scope.model[key].curationDubl;
    };
    $scope.addOrgCuration = function (key) {
        var org = $scope.model[key].org;
        org.getNewOrgCuration().then(function (org_curation) {
            org_curation.person_curation = $scope.model[key].newCuration;
            org.addOrgCuration(org_curation);
            $scope.model[key].newCuration = null;
        });
    };
    $scope.removeOrgCuration = function (key, idx) {
        $scope.model[key].org.org_curations.splice(idx, 1);
    };
    $scope.checkCurationDubl = function (key) {
        var selected = $scope.model[key].org.org_curations.map(function (oc) { return oc.person_curation.id; });
        $scope.model[key].curationDubl = selected.has($scope.model[key].newCuration.id);
    };
    $scope.alertCurationDublVisible = function (key) {
        return $scope.model[key].curationDubl;
    };

    $scope.person_curation_list = [];
    PersonCuration.instantiateAll()
        .then(function (pers_curs) {
            $scope.person_curation_list = pers_curs;
        });
    Organisation.instantiateAll({
        with_curations: true
    }).then(function (orgs) {
        $scope.model = {};
        // TODO: filter on server
        orgs = orgs.filter(function (o) { return o.is_stationary; });
        angular.forEach(orgs, function (org, key) {
            $scope.model[key] = {
                org: org,
                editing: false,
                newCuration: null,
                curationDubl: false
            };
        });
    });
}])
;