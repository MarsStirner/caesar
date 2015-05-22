'use strict';

WebMis20
.service('RbList', ['ApiCalls', function (ApiCalls) {
    var self = this;
    this.loading = ApiCalls.wrapper('GET', '/misconfig/api/v1/rb/list/')
    .then(function (data) {
        self.items = data.supported_rbs;
    });
    this.getByName = function (name) {
        return _.find(self.items, function (item) {
            return item.name === name;
        })
    }
}])
.factory('rbTreatment', ['SimpleRb', function (SimpleRb) {
    var rbTreatment = function (data) {
        SimpleRb.call(this, data);
    };
    rbTreatment.inheritsFrom(SimpleRb);
    rbTreatment.initialize({
        fields: rbTreatment.getFields().concat('treatment_type'),
        base_url: '{0}rbTreatment/'.format(rbTreatment.getBaseUrl())
    }, rbTreatment);
    return rbTreatment;
}])
.factory('rbTreatmentType', ['SimpleRb', function (SimpleRb) {
    var rbTreatmentType = function (data) {
        SimpleRb.call(this, data);
    };
    rbTreatmentType.inheritsFrom(SimpleRb);
    rbTreatmentType.initialize({
        base_url: '{0}rbTreatmentType/'.format(rbTreatmentType.getBaseUrl())
    });
    return rbTreatmentType;
}])
.factory('rbPacientModel', ['SimpleRb', function (SimpleRb) {
    var rbPacientModel = function (data) {
        SimpleRb.call(this, data);
    };
    rbPacientModel.inheritsFrom(SimpleRb);
    rbPacientModel.initialize({
        base_url: '{0}rbPacientModel/'.format(rbPacientModel.getBaseUrl())
    });
    return rbPacientModel;
}])
.factory('rbFinance', ['SimpleRb', function (SimpleRb) {
    var rbFinance = function (data) {
        SimpleRb.call(this, data);
    };
    rbFinance.inheritsFrom(SimpleRb);
    rbFinance.initialize({
        base_url: '{0}rbFinance/'.format(rbFinance.getBaseUrl())
    }, rbFinance);
    return rbFinance;
}])
.factory('rbMeasureType', ['SimpleRb', function (SimpleRb) {
    var rbMeasureType = function (data) {
        SimpleRb.call(this, data);
    };
    rbMeasureType.inheritsFrom(SimpleRb);
    rbMeasureType.initialize({
        base_url: '{0}rbMeasureType/'.format(rbMeasureType.getBaseUrl())
    }, rbMeasureType);
    return rbMeasureType;
}])
.factory('rbMeasureScheduleType', ['SimpleRb', function (SimpleRb) {
    var rbMeasureScheduleType = function (data) {
        SimpleRb.call(this, data);
    };
    rbMeasureScheduleType.inheritsFrom(SimpleRb);
    rbMeasureScheduleType.initialize({
        base_url: '{0}rbMeasureScheduleType/'.format(rbMeasureScheduleType.getBaseUrl())
    }, rbMeasureScheduleType);
    return rbMeasureScheduleType;
}])
.controller('RBConfigCtrl', ['$scope', '$controller', '$location', 'RbList', 'RbService',
        function ($scope, $controller, $location, RbList, RbService) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.RbList = RbList;
    $scope.model = {
        selected_rb: null
    };
    var changePath = function (rb_name) {
        var path = $location.path() + '?name=' + rb_name;
        $location.url(path).replace();
    };
    $scope.select_rb = function (rb_item) {
        $scope.model.selected_rb = rb_item;
        var template = '';
        if (rb_item.is_simple) {
            template = '/caesar/misconfig/refbook/simple-rb-edit-modal.html';
        } else {
            template = '/caesar/misconfig/refbook/{0}-edit-modal.html'.format(rb_item.name);
        }
        $scope.setModalParams({
            templateUrl: template
        });
        $scope.EntityClass = RbService.getClass(rb_item.name);
        RbService.getItemList(rb_item.name).then(function (orgs) {
            $scope.item_list = orgs;
        });
        changePath(rb_item.name)
    };
    $scope.isSelected = function (name) {
        return $scope.model.selected_rb && $scope.model.selected_rb.name === name;
    };
    $scope.gotoIndex = function () {
        $scope.model.selected_rb = null;
        $scope.item_list = [];
    };
    $scope.init = function () {
        var selected_rb = $scope.getUrlParam('name');
        if (selected_rb) {
            $scope.RbList.loading.then(function () {
                var rb_item = $scope.RbList.getByName(selected_rb);
                if (rb_item) {
                    $scope.select_rb(rb_item);
                }
            });
        }
    };

    $scope.init();
}])
;