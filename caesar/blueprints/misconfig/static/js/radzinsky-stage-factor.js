'use strict';

WebMis20
.factory('rbRadzStageFactors', ['BasicModel', function (BasicModel) {
    var rbRadzStageFactors = function (data) {
        BasicModel.call(this, data);
    };
    rbRadzStageFactors.inheritsFrom(BasicModel);
    rbRadzStageFactors.initialize({
        fields: ['id', 'code', 'name', 'stage_factor_assoc'],
        base_url: '/misconfig/api/v1/rb_radzinsky_stage_factor/'
    }, rbRadzStageFactors);
    return rbRadzStageFactors;
}])
.controller('RadzStageFactorConfigCtrl', ['$scope', '$controller', 'rbRadzStageFactors',
        function ($scope, $controller, rbRadzStageFactors) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.model = {};

    $scope.startEditing = function (key) {
        $scope.model[key].editing = true;
    };
    $scope.cancelEditing = function (key) {
        $scope.model[key].editing = false;
    };
    $scope.finishEditing = function (key) {
        $scope.model[key].sf.save().then(function (sf) {
            $scope.model[key].sf = sf;
            $scope.cancelEditing(key);
        });
    };
    $scope.inEditState = function (key) {
        return $scope.model[key].editing;
    };
    $scope.btnAddFactorAvailable = function (key) {
        return $scope.model[key].newFactor !== null && $scope.model[key].newPoints !== null &&
            !$scope.model[key].factorDubl;
    };
    $scope.addFactor = function (key) {
        var sf = $scope.model[key].sf;
        sf.stage_factor_assoc.push({
            factor: $scope.model[key].newFactor,
            points: $scope.model[key].newPoints
        });
        $scope.model[key].newFactor = null;
        $scope.model[key].newPoints = null;
    };
    $scope.removeFactor = function (key, idx) {
        $scope.model[key].sf.stage_factor_assoc.splice(idx, 1);
    };
    $scope.checkFactorDubl = function (key) {
        var selected = $scope.model[key].sf.stage_factor_assoc.map(function (a) { return a.factor.id; });
        $scope.model[key].factorDubl = selected.has($scope.model[key].newFactor.id);
    };
    $scope.alertFactorDublVisible = function (key) {
        return $scope.model[key].factorDubl;
    };

    rbRadzStageFactors.instantiateAll().then(function (stage_factors) {
        $scope.model = {};
        angular.forEach(stage_factors, function (sf, key) {
            $scope.model[key] = {
                sf: sf,
                editing: false,
                newFactor: null,
                newPoints: null,
                factorDubl: false
            };
        });
    });
}])
;