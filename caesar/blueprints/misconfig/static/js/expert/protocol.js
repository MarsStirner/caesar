'use strict';

WebMis20
.factory('ExpertProtocol', ['BasicModel', function (BasicModel) {
    var _fields = ['id', 'code', 'name'],
        _base_url = '/misconfig/api/v1/expert/protocol/';
    var ExpertProtocol = function (data) {
        BasicModel.call(this, data);
    };
    ExpertProtocol.inheritsFrom(BasicModel);
    ExpertProtocol.initialize({
        base_url: _base_url,
        fields: _fields
    });
    ExpertProtocol.prototype.save = function () {
        return BasicModel.prototype.save.call(this);
    };
    ExpertProtocol.prototype.del = function () {
        var url = '/misconfig/api/v1/rb/{0}/{1}/'.format(this.rb_name, this.id);
        return BasicModel.prototype.del.call(this, url);
    };
    return ExpertProtocol;
}])
.controller('ExpertProtocolConfigCtrl', ['$scope', '$controller', 'RbService',
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
        templateUrl: '/caesar/misconfig/expert/protocol/protocol-edit-modal.html'
    });
    $scope.EntityClass = RbService.getClass('ExpertProtocol');

    RbService.getItemList('ExpertProtocol').then(function (protocols) {
        $scope.item_list = protocols;
    });
}])
;