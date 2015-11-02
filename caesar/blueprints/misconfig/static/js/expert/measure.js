'use strict';

WebMis20
.controller('MeasureConfigCtrl', ['$scope', '$controller', 'Measure',
        function ($scope, $controller, Measure) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setSimpleModalConfig({
        controller: 'MeasureConfigModalCtrl',
        templateUrl: '/caesar/misconfig/expert/protocol/measure-edit-modal.html'
    });
    $scope.EntityClass = Measure;
    Measure.instantiateAll().then(function (measures) {
        $scope.item_list = measures;
    });
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