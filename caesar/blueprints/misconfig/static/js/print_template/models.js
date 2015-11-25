'use strict';

WebMis20
.factory('rbPrintTemplate', ['WMConfig', 'BasicModel', function (WMConfig, BasicModel) {
    var rbPrintTemplate = function (data) {
        BasicModel.call(this, data);
    };
    rbPrintTemplate.inheritsFrom(BasicModel);
    rbPrintTemplate.initialize({
        fields: ['id', 'code', 'name', 'context', 'template_text', 'deleted'],
        base_url: WMConfig.url.misconfig.api_print_template_base,
        list_url: WMConfig.url.misconfig.api_print_template_list_base
    }, rbPrintTemplate);
    return rbPrintTemplate;
}])
;