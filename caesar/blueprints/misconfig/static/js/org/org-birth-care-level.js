'use strict';

WebMis20
.controller('OrgBCLConfigCtrl', ['$scope', '$controller', 'OrganisationBirthCareLevel',
        function ($scope, $controller, OrganisationBirthCareLevel) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setSimpleModalConfig({
        templateUrl: '/caesar/misconfig/org/org-bcl-edit-modal.html'
    });
    $scope.EntityClass = OrganisationBirthCareLevel;
    OrganisationBirthCareLevel.instantiateAll({
        with_deleted: true
    }).then(function (orgs) {
        $scope.item_list = orgs;
    });
}])
.controller('OrgOBCLConfigCtrl', ['$scope', '$controller', 'OrganisationBirthCareLevel',
        function ($scope, $controller, OrganisationBirthCareLevel) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.model = {};
    $scope.formatOrgName = function (org) {
        return org && org.short_name;
    };
    $scope.startEditing = function (key) {
        $scope.model[key].editing = true;
    };
    $scope.cancelEditing = function (key) {
        $scope.model[key].editing = false;
    };
    $scope.finishEditing = function (key) {
        $scope.model[key].obcl.save(undefined, undefined, {
            with_orgs: true
        }).then(function (obcl) {
            $scope.model[key].obcl = obcl;
            $scope.cancelEditing(key);
        });
    };
    $scope.inEditState = function (key) {
        return $scope.model[key].editing;
    };
    $scope.btnAddOrgAvailable = function (key) {
        return $scope.model[key].newOrg !== null && !$scope.model[key].orgDubl;
    };
    $scope.addOrgOBCL = function (key) {
        var obcl = $scope.model[key].obcl;
        obcl.getNewOrgOBCL($scope.model[key].newOrg.id).then(function (org_obcl) {
            obcl.addOrgOBCL(org_obcl);
            $scope.model[key].newOrg = null;
        });
    };
    $scope.removeOrgOBCL = function (key, idx) {
        $scope.model[key].obcl.org_obcls.splice(idx, 1);
    };
    $scope.checkOrgDubl = function (key) {
        var selectedOrgIds = $scope.model[key].obcl.org_obcls.map(function (o) { return o.org_id; });
        $scope.model[key].orgDubl = selectedOrgIds.has($scope.model[key].newOrg.id);
    };
    $scope.alertOrgDublVisible = function (key) {
        return $scope.model[key].orgDubl;
    };
    $scope.fltStationaryLPU = function () {
        return function (org) {
            return org && Boolean(org.is_stationary);
        }
    };

    OrganisationBirthCareLevel.instantiateAll({
        with_orgs: true
    }).then(function (obcls) {
        $scope.model = {};
        angular.forEach(obcls, function (obcl, key) {
            $scope.model[key] = {
                obcl: obcl,
                editing: false,
                newOrg: null,
                orgDubl: false
            };
        });
    });
}])
;