'use strict';

WebMis20
.factory('Measure', ['SimpleRb', function (SimpleRb) {
    var Measure = function (data) {
        SimpleRb.call(this, data);
    };
    Measure.inheritsFrom(SimpleRb);
    Measure.initialize({
        fields: ['id', 'measure_type', 'code', 'name', 'deleted', 'uuid', 'action_type',
            'template_action', 'data_model'],
        base_url: '{0}Measure/'.format(Measure.getBaseUrl())
    }, Measure);
    return Measure;
}])
.factory('ExpertProtocol', ['WMConfig', 'BasicModel', 'ExpertScheme', function (WMConfig, BasicModel, ExpertScheme) {
    var ExpertProtocol = function (data) {
        BasicModel.call(this, data);
    };
    ExpertProtocol.inheritsFrom(BasicModel);
    ExpertProtocol.initialize({
        fields: ['id', 'code', 'name', 'deleted', {
            name: 'schemes',
            optional: true,
            klass: ExpertScheme
        }],
        base_url: WMConfig.url.misconfig.api_expert_protocol_base,
        list_url: WMConfig.url.misconfig.api_expert_protocol_list_base
    }, ExpertProtocol);
    ExpertProtocol.prototype.getNewScheme = function () {
        return ExpertScheme.instantiate(undefined, {
            'new': true,
            protocol_id: this.id
        });
    };
    ExpertProtocol.prototype.addScheme = function (scheme) {
        this.schemes.push(scheme);
    };
    return ExpertProtocol;
}])
.factory('ExpertScheme', ['WMConfig', 'BasicModel',
        function (WMConfig, BasicModel) {
    var ExpertScheme = function (data) {
        BasicModel.call(this, data);
    };
    ExpertScheme.inheritsFrom(BasicModel);
    ExpertScheme.initialize({
        fields: ['id', 'code', 'name', 'number', 'deleted', 'protocol_id', 'mkbs'],
        base_url: WMConfig.url.misconfig.api_expert_scheme_base
    }, ExpertScheme);
    return ExpertScheme;
}])
.factory('ExpertSchemeMeasureSchedule', ['WMConfig', 'ApiCalls', 'BasicModel', 'Measure', 'MeasureSchedule',
        function (WMConfig, ApiCalls, BasicModel, Measure, MeasureSchedule) {
    var ExpertSchemeMeasureSchedule = function (data) {
        BasicModel.call(this, data);
    };
    ExpertSchemeMeasureSchedule.inheritsFrom(BasicModel);
    ExpertSchemeMeasureSchedule.initialize({
        fields: ['id', 'scheme_id', {
            name: 'measure',
            klass: Measure
        }, {
            name: 'schedule',
            klass: MeasureSchedule
        }, 'deleted'],
        base_url: WMConfig.url.misconfig.api_expert_scheme_measure_base,
        list_url: WMConfig.url.misconfig.api_expert_scheme_measure_list_base
    }, ExpertSchemeMeasureSchedule);
    return ExpertSchemeMeasureSchedule;
}])
.factory('MeasureSchedule', ['WMConfig', 'BasicModel', function (WMConfig, BasicModel) {
    var MeasureSchedule = function (data) {
        BasicModel.call(this, data);
    };
    MeasureSchedule.inheritsFrom(BasicModel);
    MeasureSchedule.initialize({
        fields: ['id', 'apply_type', 'apply_bound_range_low', 'apply_bound_range_low_unit',
            'apply_bound_range_low_max', 'apply_bound_range_low_max_unit',
            'apply_bound_range_high', 'apply_bound_range_high_unit',
            'period', 'period_unit', 'frequency', 'count',
            'schedule_types', 'additional_text', 'additional_mkbs']
    }, MeasureSchedule);
    return MeasureSchedule;
}])
;