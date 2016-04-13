'use strict';

WebMis20
.service('RbList', ['$injector', 'ApiCalls', function ($injector, ApiCalls) {
    var self = this;
    this.loading = ApiCalls.wrapper('GET', '/misconfig/api/v1/rb/list/')
        .then(function (data) {
            self.items = data.supported_rbs;
        });
    this.getByName = function (name) {
        var curRbList;
        for (var prop in self.items) {
            if (self.items.hasOwnProperty(prop)) {
                curRbList = self.items[prop].rb_list;
                for (var i = 0; i < curRbList.length; i++) {
                    if (curRbList[i].name === name) {
                        return curRbList[i];
                    }
                }
            }
        }
    };
    this.getEntityClass = function (name) {
        return $injector.get(name);
    };
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
    }, rbTreatmentType);
    return rbTreatmentType;
}])
.factory('rbPacientModel', ['SimpleRb', function (SimpleRb) {
    var rbPacientModel = function (data) {
        SimpleRb.call(this, data);
    };
    rbPacientModel.inheritsFrom(SimpleRb);
    rbPacientModel.initialize({
        base_url: '{0}rbPacientModel/'.format(rbPacientModel.getBaseUrl())
    }, rbPacientModel);
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
.factory('rbMeasureScheduleApplyType', ['SimpleRb', function (SimpleRb) {
    var rbMeasureScheduleApplyType = function (data) {
        SimpleRb.call(this, data);
    };
    rbMeasureScheduleApplyType.inheritsFrom(SimpleRb);
    rbMeasureScheduleApplyType.initialize({
        base_url: '{0}rbMeasureScheduleApplyType/'.format(rbMeasureScheduleApplyType.getBaseUrl())
    }, rbMeasureScheduleApplyType);
    return rbMeasureScheduleApplyType;
}])
.factory('rbPerinatalRiskRate', ['SimpleRb', function (SimpleRb) {
    var rbPerinatalRiskRate = function (data) {
        SimpleRb.call(this, data);
    };
    rbPerinatalRiskRate.inheritsFrom(SimpleRb);
    rbPerinatalRiskRate.initialize({
        base_url: '{0}rbPerinatalRiskRate/'.format(rbPerinatalRiskRate.getBaseUrl())
    }, rbPerinatalRiskRate);
    return rbPerinatalRiskRate;
}])
.factory('rbOrgCurationLevel', ['SimpleRb', function (SimpleRb) {
    var rbOrgCurationLevel = function (data) {
        SimpleRb.call(this, data);
    };
    rbOrgCurationLevel.inheritsFrom(SimpleRb);
    rbOrgCurationLevel.initialize({
        base_url: '{0}rbOrgCurationLevel/'.format(rbOrgCurationLevel.getBaseUrl())
    }, rbOrgCurationLevel);
    return rbOrgCurationLevel;
}])
.factory('rbPregnancyPathology', ['SimpleRb', function (SimpleRb) {
    var rbPregnancyPathology = function (data) {
        SimpleRb.call(this, data);
    };
    rbPregnancyPathology.inheritsFrom(SimpleRb);
    rbPregnancyPathology.initialize({
        base_url: '{0}rbPregnancyPathology/'.format(rbPregnancyPathology.getBaseUrl())
    }, rbPregnancyPathology);
    return rbPregnancyPathology;
}])
.factory('rbPost', ['SimpleRb', function (SimpleRb) {
    var rbPost = function (data) {
        SimpleRb.call(this, data);
    };
    rbPost.inheritsFrom(SimpleRb);
    rbPost.initialize({
        base_url: '{0}rbPost/'.format(rbPost.getBaseUrl())
    }, rbPost);
    return rbPost;
}])
.factory('rbSpeciality', ['SimpleRb', function (SimpleRb) {
    var rbSpeciality = function (data) {
        SimpleRb.call(this, data);
    };
    rbSpeciality.inheritsFrom(SimpleRb);
    rbSpeciality.initialize({
        base_url: '{0}rbSpeciality/'.format(rbSpeciality.getBaseUrl())
    }, rbSpeciality);
    return rbSpeciality;
}])
.factory('rbRequestType', ['SimpleRb', function (SimpleRb) {
    var rbRequestType = function (data) {
        SimpleRb.call(this, data);
    };
    rbRequestType.inheritsFrom(SimpleRb);
    rbRequestType.initialize({
        base_url: '{0}rbRequestType/'.format(rbRequestType.getBaseUrl())
    }, rbRequestType);
    return rbRequestType;
}])
.factory('rbResult', ['SimpleRb', function (SimpleRb) {
    var rbResult = function (data) {
        SimpleRb.call(this, data);
    };
    rbResult.inheritsFrom(SimpleRb);
    rbResult.initialize({
        base_url: '{0}rbResult/'.format(rbResult.getBaseUrl()),
        fields: rbResult.getFields().concat('event_purpose')
    }, rbResult);
    return rbResult;
}])
.factory('rbEventTypePurpose', ['SimpleRb', function (SimpleRb) {
    var rbEventTypePurpose = function (data) {
        SimpleRb.call(this, data);
    };
    rbEventTypePurpose.inheritsFrom(SimpleRb);
    rbEventTypePurpose.initialize({
        base_url: '{0}rbEventTypePurpose/'.format(rbEventTypePurpose.getBaseUrl())
    }, rbEventTypePurpose);
    return rbEventTypePurpose;
}])
.controller('RBConfigCtrl', ['$scope', '$controller', '$location', 'RbList',
        function ($scope, $controller, $location, RbList) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.RbList = RbList;
    $scope.model = {
        selected_rb: null
    };
    var changePath = function (rb_name) {
        var path = $location.path() + '?name=' + rb_name;
        $location.url(path).replace();
    };
    $scope.selectRb = function (rb_item) {
        $scope.model.selected_rb = rb_item;
        var template = '';
        if (rb_item.is_simple) {
            template = '/caesar/misconfig/refbook/simple-rb-edit-modal.html';
        } else {
            template = '/caesar/misconfig/refbook/{0}-edit-modal.html'.format(rb_item.name);
        }
        $scope.setSimpleModalConfig({
            templateUrl: template
        });
        $scope.EntityClass = RbList.getEntityClass(rb_item.name);
        $scope.EntityClass.instantiateAll().then(function (items) {
            $scope.item_list = items;
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
                    $scope.selectRb(rb_item);
                }
            });
        }
    };

    $scope.init();
}])
;