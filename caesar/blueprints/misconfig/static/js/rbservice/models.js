'use strict';

WebMis20
.factory('rbService', ['SimpleRb', 'rbServiceGroupAssoc', function (SimpleRb, rbServiceGroupAssoc) {
    var rbService = function (data) {
        SimpleRb.call(this, data);
    };
    rbService.inheritsFrom(SimpleRb);
    rbService.initialize({
        fields: rbService.getFields().concat(['beg_date', 'end_date', 'is_complex', 'subservice_assoc']),
        base_url: '{0}rbService/'.format(rbService.getBaseUrl())
    }, rbService);
    rbService.prototype.getNewGroupItem = function () {
        return rbServiceGroupAssoc.instantiate(undefined, {'new': true})
            .then(function (group) {
                return group;
            });
    };
    rbService.prototype.addGroupItem = function (assoc_group) {
        this.subservice_assoc.push(assoc_group);
    };
    rbService.prototype.removeGroupItem = function (idx) {
        this.subservice_assoc.splice(idx, 1);
    };
    return rbService;
}])
.factory('rbServiceGroupAssoc', ['BasicModel', 'WMConfig', function (BasicModel, WMConfig) {
    var rbServiceGroupAssoc = function (data) {
        BasicModel.call(this, data);
    };
    rbServiceGroupAssoc.inheritsFrom(BasicModel);
    rbServiceGroupAssoc.initialize({
        fields: ['id', 'group_id', 'service_id', 'subservice', 'service_kind'],
        base_url: WMConfig.url.misconfig.api_rb_service_group_assoc_base
    }, rbServiceGroupAssoc);
    return rbServiceGroupAssoc;
}])
;