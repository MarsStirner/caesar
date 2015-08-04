'use strict';

WebMis20
.factory('rbPerinatalRiskRateWithMkbs', ['BasicModel', 'rbPerinatalRiskRateMkb', function (BasicModel, rbPerinatalRiskRateMkb) {
    var rbPerinatalRiskRateWithMkbs = function (data) {
        BasicModel.call(this, data);
    };
    rbPerinatalRiskRateWithMkbs.inheritsFrom(BasicModel);
    rbPerinatalRiskRateWithMkbs.initialize({
        fields: ['id', 'code', 'name', {
            name: 'prr_mkbs',
            klass: rbPerinatalRiskRateMkb
        }],
        base_url: '/misconfig/api/v1/rb_perinatal_risk_rate/'
    }, rbPerinatalRiskRateWithMkbs);
    rbPerinatalRiskRateWithMkbs.prototype.getNewMkb = function () {
        var url = rbPerinatalRiskRateMkb.getBaseUrl().format(this.id) + 'new/';
        return rbPerinatalRiskRateMkb.instantiate(undefined, undefined, url);
    };
    rbPerinatalRiskRateWithMkbs.prototype.addMkb = function (prr_mkb) {
        this.prr_mkbs.push(prr_mkb);
    };
    return rbPerinatalRiskRateWithMkbs;
}])
.factory('rbPerinatalRiskRateMkb', ['BasicModel', function (BasicModel) {
    var rbPerinatalRiskRateMkb = function (data) {
        BasicModel.call(this, data);
    };
    rbPerinatalRiskRateMkb.inheritsFrom(BasicModel);
    rbPerinatalRiskRateMkb.initialize({
        fields: ['id', 'risk_rate_id', 'mkb'],
        base_url: '/misconfig/api/v1/rb_perinatal_risk_rate/{0}/mkbs/'
    }, rbPerinatalRiskRateMkb);
    return rbPerinatalRiskRateMkb;
}])
.controller('PRRMKBConfigCtrl', ['$scope', '$controller', 'rbPerinatalRiskRateWithMkbs',
        function ($scope, $controller, rbPerinatalRiskRateWithMkbs) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.model = {};
    $scope.startEditing = function (key) {
        $scope.model[key].prr_copy = $scope.model[key].prr.clone();
        $scope.model[key].editing = true;
    };
    $scope.cancelEditing = function (key) {
        $scope.model[key].prr = $scope.model[key].prr_copy;
        $scope.model[key].prr_copy = null;
        $scope.model[key].proxyMkbList = $scope.model[key].prr.prr_mkbs.map(function (prr_mkb) { return prr_mkb.mkb; });
        $scope.model[key].editing = false;
    };
    $scope.finishEditing = function (key) {
        $scope.model[key].prr.save().then(function (prr) {
            $scope.model[key].prr_copy = prr;
            $scope.cancelEditing(key);
        });
    };
    $scope.inEditState = function (key) {
        return $scope.model[key].editing;
    };
    $scope.filterMkbChoices = function (item) {
        return function (mkb) {
            var used_codes = item.prr.prr_mkbs.map(function (prr_mkb) { return prr_mkb.mkb.code });
            return !used_codes.has(mkb.code);
        }
    };
    $scope.onMkbListChanged = function (item) {
        var new_values = item.proxyMkbList;
        var new_len = new_values.length;
        new_values.forEach(function (value, index) {
            if (item.prr.prr_mkbs.length <= index) {
                item.prr.getNewMkb().
                    then(function (prr_mkb) {
                        prr_mkb.mkb = value;
                        item.prr.addMkb(prr_mkb);
                    });
            } else {
                item.prr.prr_mkbs[index].mkb = value;
            }
        });
        item.prr.prr_mkbs.splice(new_len);
    };

    rbPerinatalRiskRateWithMkbs.instantiateAll().then(function (prrs) {
        $scope.model = {};
        angular.forEach(prrs, function (prr, key) {
            $scope.model[key] = {
                prr: prr,
                prr_copy: null,
                editing: false,
                proxyMkbList: prr.prr_mkbs.map(function (prr_mkb) { return prr_mkb.mkb; })
            };
        });
    });
}])
;