'use strict';

WebMis20
.controller('MeasureConfigCtrl', ['$scope', '$controller', 'Measure',
        function ($scope, $controller, Measure) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setViewParams({paginate: false});
    $scope.setSimpleModalConfig({
        controller: 'MeasureConfigModalCtrl',
        templateUrl: '/caesar/misconfig/expert/protocol/measure-edit-modal.html'
    });
    $scope.EntityClass = Measure;

    var setData = function (items) {
        $scope.item_list = items;
    };
    $scope.refreshData = function () {
        $scope._refreshData().then(setData);
    };
    $scope.onPageChanged = function () {
        $scope.refreshData();
    };

    $scope.init = function () {
        $scope.refreshData();
    };

    $scope.init();
}])
.controller('MeasureConfigModalCtrl', ['$scope', '$modalInstance', 'model',
    function ($scope, $modalInstance, model) {
        $scope.model = model;
        $scope.close = function () {
            $scope.model.save().
                then(function (model) {
                    $scope.$close(model);
                });
        };
}])
;