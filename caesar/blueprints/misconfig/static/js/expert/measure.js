'use strict';

WebMis20
.factory('Measure', ['SimpleRb', function (SimpleRb) {
    var name = 'Measure',
        _fields = ['id', 'measure_type', 'code', 'name', 'deleted', 'uuid', 'action_type',
            'template_action', 'data_model'];
    var Measure = function (data) {
        SimpleRb.call(this, name, data, _fields);
    };
    Measure.prototype = Object.create(SimpleRb.prototype);
    Measure.prototype.constructor = Measure;
    return Measure;
}])
.controller('MeasureConfigCtrl', ['$scope', '$controller', 'RbService',
        function ($scope, $controller, RbService) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setModalParams({
        controller: function ($scope, $modalInstance, model) {
            $scope.model = model;
            $scope.measure_data_is_at = function () {
                return model.data_model === 'action_type'
            };
            $scope.measure_data_is_template_action = function () {
                return model.data_model === 'template_action'
            };
        },
        templateUrl: '/caesar/misconfig/expert/protocol/measure-edit-modal.html'
    });
    $scope.EntityClass = RbService.getClass('Measure');

    RbService.getItemList('Measure').then(function (measures) {
        $scope.item_list = measures;
    });
}])
;