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
.factory('ExpertProtocol', ['BasicModel', 'ExpertScheme', function (BasicModel, ExpertScheme) {
    var ExpertProtocol = function (data) {
        BasicModel.call(this, data);
    };
    ExpertProtocol.inheritsFrom(BasicModel);
    ExpertProtocol.initialize({
        fields: ['id', 'code', 'name', {
            name: 'schemes',
            klass: ExpertScheme
        }],
        base_url: '/misconfig/api/v1/expert/protocol/'
    }, ExpertProtocol);
    ExpertProtocol.prototype.getNewScheme = function () {
        return ExpertScheme.instantiate('new', this.id);
    };
    ExpertProtocol.prototype.addScheme = function (scheme) {
        this.schemes.push(scheme);
    };
    return ExpertProtocol;
}])
.factory('ExpertScheme', ['BasicModel', 'ExpertSchemeMKB', 'ExpertSchemeMeasure',
        function (BasicModel, ExpertSchemeMKB) {
    var ExpertScheme = function (data) {
        BasicModel.call(this, data);
        this.scheme_measures = [];
    };
    ExpertScheme.inheritsFrom(BasicModel);
    ExpertScheme.initialize({
        fields: ['id', 'code', 'name', 'number', 'protocol_id', {
            name: 'scheme_mkbs',
            klass: ExpertSchemeMKB
        }],
        base_url: '/misconfig/api/v1/expert/protocol/scheme/'
    }, ExpertScheme);
    ExpertScheme.prototype.getNewMkb = function () {
        return ExpertSchemeMKB.instantiate('new', this.id);
    };
    ExpertScheme.prototype.addMkb = function (scheme_mkb) {
        this.scheme_mkbs.push(scheme_mkb);
    };
    ExpertScheme.prototype.addSchemeMeasure = function (sm) {
        this.scheme_measures.push(sm);
    };
    return ExpertScheme;
}])
.factory('ExpertSchemeMKB', ['BasicModel', function (BasicModel) {
    var ExpertSchemeMKB = function (data) {
        BasicModel.call(this, data);
    };
    ExpertSchemeMKB.inheritsFrom(BasicModel);
    ExpertSchemeMKB.initialize({
        fields: ['id', 'scheme_id', 'mkb'],
        base_url: '/misconfig/api/v1/expert/protocol/scheme_mkb/'
    }, ExpertSchemeMKB);
    return ExpertSchemeMKB;
}])
.factory('ExpertSchemeMeasure', ['ApiCalls', 'BasicModel', 'Measure', 'MeasureSchedule',
        function (ApiCalls, BasicModel, Measure, MeasureSchedule) {
    var ExpertSchemeMeasure = function (data) {
        BasicModel.call(this, data);
    };
    ExpertSchemeMeasure.inheritsFrom(BasicModel);
    ExpertSchemeMeasure.initialize({
        fields: ['id', 'scheme_id', {
            name: 'measure',
            klass: Measure
        }, {
            name: 'schedule',
            klass: MeasureSchedule
        }],
        base_url: '/misconfig/api/v1/expert/protocol/scheme_measure/'
    }, ExpertSchemeMeasure);
    ExpertSchemeMeasure.instantiateByScheme = function (scheme_id) {
        var klass = this;
        var url = '/misconfig/api/v1/expert/protocol/scheme_measure/by_scheme/{0}/'.format(scheme_id);
        return ApiCalls.wrapper('GET', url)
            .then(function (data) {
                return data.items.map(function (item) {
                    return new klass(item);
                });
            });
    };
    return ExpertSchemeMeasure;
}])
.factory('MeasureSchedule', ['BasicModel', 'Measure', function (BasicModel) {
    var MeasureSchedule = function (data) {
        BasicModel.call(this, data);
    };
    MeasureSchedule.inheritsFrom(BasicModel);
    MeasureSchedule.initialize({
        fields: ['id', 'schedule_type', 'offset_start', 'offset_end', 'repeat_count'],
        base_url: '/misconfig/api/v1/expert/protocol/measure_schedule/'
    }, MeasureSchedule);
    return MeasureSchedule;
}])
;