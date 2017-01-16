'use strict';

WebMis20
.controller('PersonCurationConfigCtrl', ['$scope', '$controller', 'Person',
        function ($scope, $controller, Person) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setViewParams({paginate: true});
    $scope.EntityClass = Person;
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
    $scope.fltCurLevel = function () {
        return function (level) {
            return level['code'] !== "0";
        }
    };
    $scope.clear = function () {
        $scope.flt.model = {};
    };
    $scope.clearAll = function () {
        $scope.clear();
        $scope.getData();

    };
    $scope.extendCurationLevel = function () {
        return function () {
            return [{id: 0, code: "0", name: 'без уровня курирования'}];
        }
    };
    $scope.onPageChanged = function () {
        $scope.refreshData();
    };

    var setData = function (paged_data) {
        $scope.model = {};
        $scope.item_list = paged_data.items;
        $scope.pager.record_count = paged_data.count;
        $scope.pager.pages = paged_data.total_pages;
        angular.forEach(paged_data.items, function (person, key) {
            $scope.model[key] = {
                person: person,
                editing: false,
                newCuration: null,
                curationDubl: false
            };
        });
    };
    $scope.refreshData = function () {
        var args = {
            with_profiles: true,
            with_curations: true,
            paginate: true,
            page: $scope.pager.current_page,
            per_page: $scope.pager.per_page,
            fio: $scope.flt.model.fio || undefined,
            speciality_id: safe_traverse($scope.flt.model, ['speciality', 'id']),
            post_id: safe_traverse($scope.flt.model, ['post', 'id']),
            curation_levels_ids: angular.toJson(_.pluck($scope.flt.model.curation_levels, 'id'))
        };
        $scope._refreshData(args).then(setData);
    };
    $scope.init = function () {
        $scope.toggleFilter();
        $scope.refreshData();
    };

    $scope.init();
}])
;