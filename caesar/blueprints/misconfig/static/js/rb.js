'use strict';

WebMis20
.service('RbList', ['ApiCalls', function (ApiCalls) {
    var self = this;
    ApiCalls.wrapper('GET', '/misconfig/api/v1/rb/list/')
    .then(function (data) {
        self.items = data.supported_rbs;
    })
}])
.factory('rbTreatment', ['SimpleRb', function (SimpleRb) {
    var name = 'rbTreatment',
        rbTreatment = function (data) {
            SimpleRb.call(this, name, data, ['treatment_type']);
        };
    rbTreatment.prototype = Object.create(SimpleRb.prototype);
    rbTreatment.prototype.constructor = rbTreatment;
    return rbTreatment;
}])
.factory('rbTreatmentType', ['SimpleRb', function (SimpleRb) {
    var name = 'rbTreatmentType',
        rbTreatmentType = function (data) {
            SimpleRb.call(this, name, data);
        };
    rbTreatmentType.prototype = Object.create(SimpleRb.prototype);
    rbTreatmentType.prototype.constructor = rbTreatmentType;
    return rbTreatmentType;
}])
.factory('rbPacientModel', ['SimpleRb', function (SimpleRb) {
    var name = 'rbPacientModel',
        rbPacientModel = function (data) {
            SimpleRb.call(this, name, data);
        };
    rbPacientModel.prototype = Object.create(SimpleRb.prototype);
    rbPacientModel.prototype.constructor = rbPacientModel;
    return rbPacientModel;
}])
.factory('rbFinance', ['SimpleRb', function (SimpleRb) {
    var name = 'rbFinance',
        rbFinance = function (data) {
            SimpleRb.call(this, name, data);
        };
    rbFinance.prototype = Object.create(SimpleRb.prototype);
    rbFinance.prototype.constructor = rbFinance;
    return rbFinance;
}])
.controller('RBConfigCtrl', ['$scope', '$controller', 'RbList', 'RbService',
        function ($scope, $controller, RbList, RbService) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.RbList = RbList;
    $scope.model = {
        selected_rb: null
    };
    $scope.select_rb = function (rb_item) {
        $scope.model.selected_rb = rb_item;
        $scope.modalTemplate = rb_item.is_simple ?
            '/caesar/misconfig/refbook/simple-rb-edit-modal.html' :
            '/caesar/misconfig/refbook/{0}-edit-modal.html'.format(rb_item.name);
        $scope.EntityClass = RbService.getClass(rb_item.name);
        RbService.getItemList(rb_item.name).then(function (orgs) {
            $scope.item_list = orgs;
        });
    };
    $scope.isSelected = function (name) {
        return $scope.model.selected_rb && $scope.model.selected_rb.name === name;
    };
    $scope.gotoIndex = function () {
        $scope.model.selected_rb = null;
        $scope.item_list = [];
    };
}])
;