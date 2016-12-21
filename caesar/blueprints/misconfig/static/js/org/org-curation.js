'use strict';

WebMis20
.controller('OrgCurationConfigCtrl', ['$scope', '$controller', 'Organisation', 'PersonCuration',
        function ($scope, $controller, Organisation, PersonCuration) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setViewParams({paginate: true});
    $scope.EntityClass = Organisation;
    $scope.model = {};
    $scope.person_curation_list = [];

    $scope.startEditing = function (key) {
        $scope.model[key].editing = true;
    };
    $scope.cancelEditing = function (key) {
        $scope.model[key].editing = false;
    };
    $scope.finishEditing = function (key) {
        $scope.model[key].org.save(undefined, undefined, {
            with_curators: true
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
        org.org_curators.push($scope.model[key].newCuration);
        $scope.model[key].newCuration = null;
    };
    $scope.removeOrgCuration = function (key, idx) {
        $scope.model[key].org.org_curators.splice(idx, 1);
    };
    $scope.checkCurationDubl = function (key) {
        var selected = $scope.model[key].org.org_curators.map(function (pc) { return pc.id; });
        $scope.model[key].curationDubl = selected.has($scope.model[key].newCuration.id);
    };
    $scope.alertCurationDublVisible = function (key) {
        return $scope.model[key].curationDubl;
    };

    var setData = function (paged_data) {
        $scope.model = {};
        $scope.item_list = paged_data.items;
        $scope.pager.record_count = paged_data.count;
        $scope.pager.pages = paged_data.total_pages;
        angular.forEach(paged_data.items, function (org, key) {
            $scope.model[key] = {
                org: org,
                editing: false,
                newCuration: null,
                curationDubl: false
            };
        });
    };
    $scope.refreshData = function () {
        var args = {
            paginate: true,
            page: $scope.pager.current_page,
            per_page: $scope.pager.per_page,
            with_curators: true,
            is_lpu: true,
            name: $scope.flt.model.name || undefined
        };
        $scope._refreshData(args).then(setData);
    };
    $scope.onPageChanged = function () {
        $scope.refreshData();
    };
    $scope.init = function () {
        $scope.pager.per_page = 5;
        PersonCuration.instantiateAll()
            .then(function (pers_curs) {
                $scope.person_curation_list = pers_curs;
            });
        $scope.refreshData();
    };

    $scope.init();
}])
;