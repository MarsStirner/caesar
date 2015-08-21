'use strict';

WebMis20
.factory('rbPregnancyPathologyWithMkbs', ['BasicModel', 'rbPregnancyPathologyMkb', function (BasicModel, rbPregnancyPathologyMkb) {
    var rbPregnancyPathologyWithMkbs = function (data) {
        BasicModel.call(this, data);
    };
    rbPregnancyPathologyWithMkbs.inheritsFrom(BasicModel);
    rbPregnancyPathologyWithMkbs.initialize({
        fields: ['id', 'code', 'name', {
            name: 'pp_mkbs',
            klass: rbPregnancyPathologyMkb
        }],
        base_url: '/misconfig/api/v1/rb_pregnancy_pathology/'
    }, rbPregnancyPathologyWithMkbs);
    rbPregnancyPathologyWithMkbs.prototype.getNewMkb = function () {
        var url = rbPregnancyPathologyMkb.getBaseUrl().format(this.id) + 'new/';
        return rbPregnancyPathologyMkb.instantiate(undefined, undefined, url);
    };
    rbPregnancyPathologyWithMkbs.prototype.addMkb = function (prr_mkb) {
        this.pp_mkbs.push(prr_mkb);
    };
    return rbPregnancyPathologyWithMkbs;
}])
.factory('rbPregnancyPathologyMkb', ['BasicModel', function (BasicModel) {
    var rbPregnancyPathologyMkb = function (data) {
        BasicModel.call(this, data);
    };
    rbPregnancyPathologyMkb.inheritsFrom(BasicModel);
    rbPregnancyPathologyMkb.initialize({
        fields: ['id', 'pathology_id', 'mkb'],
        base_url: '/misconfig/api/v1/rb_pregnancy_pathology/{0}/mkbs/'
    }, rbPregnancyPathologyMkb);
    return rbPregnancyPathologyMkb;
}])
.controller('PregnancyPathologyMKBConfigCtrl', ['$scope', '$controller', 'rbPregnancyPathologyWithMkbs',
        function ($scope, $controller, rbPregnancyPathologyWithMkbs) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.model = {};
    $scope.startEditing = function (key) {
        $scope.model[key].preg_pathg_copy = $scope.model[key].preg_pathg.clone();
        $scope.model[key].editing = true;
    };
    $scope.cancelEditing = function (key) {
        $scope.model[key].preg_pathg = $scope.model[key].preg_pathg_copy;
        $scope.model[key].preg_pathg_copy = null;
        $scope.model[key].proxyMkbList = $scope.model[key].preg_pathg.pp_mkbs.map(function (pp_mkb) { return pp_mkb.mkb; });
        $scope.model[key].editing = false;
    };
    $scope.finishEditing = function (key) {
        $scope.model[key].preg_pathg.save().then(function (preg_pathg) {
            $scope.model[key].preg_pathg_copy = preg_pathg;
            $scope.cancelEditing(key);
        });
    };
    $scope.inEditState = function (key) {
        return $scope.model[key].editing;
    };
    $scope.filterMkbChoices = function (item) {
        return function (mkb) {
            var used_codes = item.preg_pathg.pp_mkbs.map(function (pp_mkb) { return pp_mkb.mkb.code });
            return !used_codes.has(mkb.code);
        }
    };
    $scope.onMkbListChanged = function (item) {
        var new_values = item.proxyMkbList;
        var new_len = new_values.length;
        new_values.forEach(function (value, index) {
            if (item.preg_pathg.pp_mkbs.length <= index) {
                item.preg_pathg.getNewMkb().
                    then(function (preg_pathg_mkb) {
                        preg_pathg_mkb.mkb = value;
                        item.preg_pathg.addMkb(preg_pathg_mkb);
                    });
            } else {
                item.preg_pathg.pp_mkbs[index].mkb = value;
            }
        });
        item.preg_pathg.pp_mkbs.splice(new_len);
    };
    var locked_pathg_codes = ['undefined', 'combined'];
    $scope.mkbEditable = function (preg_pathg) {
        return !locked_pathg_codes.has(preg_pathg.code);
    };

    rbPregnancyPathologyWithMkbs.instantiateAll().then(function (preg_pathgs) {
        $scope.model = {};
        angular.forEach(preg_pathgs, function (preg_pathg, key) {
            $scope.model[key] = {
                preg_pathg: preg_pathg,
                preg_pathg_copy: null,
                editing: false,
                proxyMkbList: preg_pathg.pp_mkbs.map(function (pp_mkb) { return pp_mkb.mkb; })
            };
        });
    });
}])
;