'use strict';

WebMis20
.controller('SchemeMeasureConfigCtrl', [
        '$scope', '$controller', '$modal', 'ExpertProtocol', 'ExpertScheme', 'ExpertSchemeMeasureSchedule',
        function ($scope, $controller, $modal, ExpertProtocol, ExpertScheme, ExpertSchemeMeasureSchedule) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    var schemeMeasureModalParams = {
        controller: 'ExpertSchemeMeasureScheduleConfigModalCtrl',
        size: 'lg',
        templateUrl: '/caesar/misconfig/expert/protocol/scheme-measure-edit-modal.html',
        windowClass: 'modal-scrollable',
        resolve: {}
    };
    var get_scheme_edit_modal = function (scheme_measure) {
        schemeMeasureModalParams.resolve.scheme_measure = function () {
            return scheme_measure
        };
        return $modal.open(schemeMeasureModalParams);
    };

    $scope.formatSchedule = function (scheme_measure) {
        return '';
    };
    $scope.createNewSchemeMeasure = function () {
        ExpertSchemeMeasureSchedule.instantiate(undefined, {
            'new': true,
            scheme_id: $scope.scheme.id
        }).then(function (scheme_measure) {
            get_scheme_edit_modal(scheme_measure).result.then(function (scheme_measure) {
                $scope.scheme_measures.push(scheme_measure);
            });
        });
    };
    $scope.editSchemeMeasure = function (index) {
        var scheme_measure = $scope.scheme_measures[index].clone();
        get_scheme_edit_modal(scheme_measure).result.then(function () {
            $scope.scheme_measures.splice(index, 1, scheme_measure);
        });
    };
    $scope.removeSchemeMeasure = function (index) {
        $scope._remove($scope.scheme_measures[index]);
    };
    $scope.restoreSchemeMeasure = function (index) {
        $scope._restore($scope.scheme_measures[index]);
    };

    $scope.scheme_measures = [];
    ExpertScheme.instantiate($scope.getUrlParam('scheme_id')).
        then(function (scheme) {
            $scope.scheme = scheme;
            ExpertProtocol.instantiate($scope.scheme.protocol_id).
                then(function (protocol) {
                    $scope.protocol = protocol;
                });
            ExpertSchemeMeasureSchedule.instantiateAll({
                scheme_id: $scope.getUrlParam('scheme_id')
            }).then(function (scheme_measures) {
                $scope.scheme_measures = scheme_measures;
            });
        });
}])
.controller('ExpertSchemeMeasureScheduleConfigModalCtrl', ['$scope', '$modalInstance', 'Measure', 'RefBookService',
        'MeasureSchedule', 'scheme_measure',
        function ($scope, $modalInstance, Measure, RefBookService, MeasureSchedule, scheme_measure) {
    $scope.scheme_measure = scheme_measure;

    Measure.instantiateAll().then(function (items) {
        $scope.measure_list = items;
    });

    $scope.MeasureScheduleType = RefBookService.get('MeasureScheduleType');
    $scope.rbMeasureScheduleApplyType = RefBookService.get('MeasureScheduleApplyType');
    $scope.rbMeasureScheduleApplyType.loading.then(function () {
        var cur_sat_id = safe_traverse($scope.scheme_measure, ['schedule', 'apply_type', 'id']),
            selected = $scope.rbMeasureScheduleApplyType.objects.filter(function (sat) {
                return sat.id === cur_sat_id;
            });
        $scope.scheme_measure.schedule.apply_type = selected.length ? selected[0] : null;
    });
    if (!scheme_measure.id) {
        $scope.MeasureScheduleType.loading.then(function () {
            var av = _.find($scope.MeasureScheduleType.objects, function (item) { return item.code === 'after_visit' });
            if (av) {
                $scope.scheme_measure.schedule.schedule_types.push(av);
            }
        });
    }

    $scope.isSchedTypeChecked = function (sched_type) {
        return $scope.scheme_measure.schedule.schedule_types.some(function (st) {
            return st.id === sched_type.id;
        });
    };
    $scope.stControlForAddMkb = function (sched_type) { return sched_type.code === 'in_presence_diag'; };
    $scope.stControlForAddNote = function (sched_type) { return sched_type.code === 'text'; };

    $scope.isSchedApplyTypeSelected = function (sched_apply_type) {
        return safe_traverse($scope.scheme_measure, ['schedule', 'apply_type', 'id']) === sched_apply_type.id;
    };
    $scope.satControlForCountFromObjDate = function (sched_apply_type) { return sched_apply_type.code === 'rel_obj_date_count'; };
    $scope.stControlForRangeFromRefDate = function (sched_apply_type) { return sched_apply_type.code === 'rel_ref_date_range'; };
    $scope.stControlForCountFromConditionalDate = function (sched_apply_type) { return sched_apply_type.code === 'rel_conditional_count'; };
    $scope.schedApplyTypeControlsVisible = function (sched_apply_type) { return $scope.isSchedApplyTypeSelected(sched_apply_type); };

    var stControlsDefaults = {
        in_presence_diag: {
            additional_mkbs: []
        },
        upon_med_indication: {
            additional_text: null
        }
    };
    $scope.toggleSchedType = function (sched_type) {
        var idx = _.indexOfObj($scope.scheme_measure.schedule.schedule_types, function (st) {
            return st.id === sched_type.id;
        });
        if (idx > -1) {
            $scope.scheme_measure.schedule.schedule_types.splice(idx, 1);
            angular.forEach(stControlsDefaults[sched_type.code], function (value, attr) {
                $scope.scheme_measure.schedule[attr] = value;
            });
        } else {
            $scope.scheme_measure.schedule.schedule_types.push(sched_type);
        }
    };

    var satControlsDefaults = {
            period: null,
            period_unit: null,
            frequency: null,
            count: null,
            apply_bound_range_low: null,
            apply_bound_range_low_unit: null,
            apply_bound_range_low_max: null,
            apply_bound_range_low_max_unit: null,
            apply_bound_range_high: null,
            apply_bound_range_high_unit: null
    };
    $scope.$watch('scheme_measure.schedule.apply_type', function (newValue, oldValue) {
        if (oldValue && !angular.equals(newValue, oldValue)) {
            angular.forEach(satControlsDefaults, function (value, attr) {
                $scope.scheme_measure.schedule[attr] = value;
            });
        }
    });

    $scope.close = function () {
        $scope.scheme_measure.save().
            then(function (scheme_measure) {
                $scope.$close(scheme_measure);
            });
    };
}])
;