'use strict';

WebMis20
.factory('rbService', ['SimpleRb', function (SimpleRb) {
    var rbService = function (data) {
        SimpleRb.call(this, data);
    };
    rbService.inheritsFrom(SimpleRb);
    rbService.initialize({
        fields: rbService.getFields().concat(['beg_date', 'end_date', 'is_complex', 'subservice_list']),
        base_url: '{0}rbService/'.format(rbService.getBaseUrl())
    }, rbService);
    return rbService;
}])
;