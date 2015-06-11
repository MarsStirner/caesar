'use strict';

WebMis20
.controller('SchemeMeasureConfigCtrl', ['$scope', '$controller', '$modal', 'ExpertScheme', 'ExpertSchemeMeasure',
        'Measure', 'MeasureSchedule',
        function ($scope, $controller, $modal, ExpertScheme, ExpertSchemeMeasure, Measure, MeasureSchedule) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    var schemeMeasureModalParams = {
        controller: function ($scope, $modalInstance, scheme_measure) {
            $scope.scheme_measure = scheme_measure;

            Measure.instantiateAll().then(function (items) {
                $scope.measure_list = items;
            });

            $scope.addSchedule = function () {
                MeasureSchedule.instantiate('new', $scope.scheme_measure.id).
                    then(function (measure_schedule) {
                        $scope.scheme_measure.schedules.push(measure_schedule);
                    });
            };
            $scope.removeSchedule = function (index) {
                $scope.scheme_measure.schedules.splice(index, 1);
            };
            $scope.close = function () {
                $scope.scheme_measure.save().
                    then(function (scheme_measure) {
                        $scope.$close(scheme_measure);
                    });
            };
        },
        size: 'lg',
        templateUrl: '/caesar/misconfig/expert/protocol/scheme-measure-edit-modal.html',
        resolve: {}
    };
    var get_scheme_edit_modal = function (scheme_measure) {
        schemeMeasureModalParams.resolve.scheme_measure = function () {
            return scheme_measure
        };
        return $modal.open(schemeMeasureModalParams);
    };

    $scope.formatSchedule = function (scheme_measure) {
        return '{0}c - {1}c, кол-во {2}'.format(
            scheme_measure.schedule.offset_start,
            scheme_measure.schedule.offset_end,
            scheme_measure.schedule.repeat_count
        );
    };
    $scope.createNewSchemeMeasure = function () {
        ExpertSchemeMeasure.instantiate('new', $scope.scheme.id).
            then(function (scheme_measure) {
                get_scheme_edit_modal(scheme_measure).result.then(function (scheme_measure) {
                    $scope.scheme.addSchemeMeasure(scheme_measure);
                });
            });
    };
    $scope.editSchemeMeasure = function (index) {
        var scheme_measure = $scope.scheme.scheme_measures[index].clone();
        get_scheme_edit_modal(scheme_measure).result.then(function () {
            $scope.scheme.scheme_measures.splice(index, 1, scheme_measure);
        });
    };

    ExpertScheme.instantiate($scope.getUrlParam('scheme_id')).
        then(function (scheme) {
            $scope.scheme = scheme;
            ExpertSchemeMeasure.instantiateByScheme($scope.getUrlParam('scheme_id')).
                then(function (scheme_measures) {
                    $scope.scheme.scheme_measures = scheme_measures;
                });
        });
}])
.directive('wmMeasureScheduleConf', function () {
    return {
        restrict: 'E',
        scope: {
            ident: '@',
            schedule: '='
        },
        template:
'<div class="form-group">\
    <label for="schedule_type">Тип расписания</label>\
    <select id="schedule_type" name="schedule_type" class="form-control"\
            ng-model="schedule.schedule_type" ref-book="rbMeasureScheduleType"\
            ng-options="item as item.name for item in $refBook.objects track by item.id">\
    </select>\
</div>\
<div class="row">\
<div class="col-md-5">\
    <div class="form-group">\
        <label for="offset_start">Начало смещения</label>\
        <wm-timestamp id="offset_start" name="offset_start" ident="[[ident]]_start"\
            ng-model="schedule.offset_start"></wm-timestamp>\
    </div>\
</div>\
<div class="col-md-offset-2 col-md-5">\
    <div class="form-group">\
        <label for="offset_end">Конец смещения</label>\
        <wm-timestamp id="offset_end" name="offset_end" ident="[[ident]]_end"\
            ng-model="schedule.offset_end"></wm-timestamp>\
    </div>\
</div>\
</div>\
<div class="form-group">\
    <label for="repeat_count">Количество повторений</label>\
    <input type="text" id="repeat_count" name="repeat_count" class="form-control"\
           ng-model="schedule.repeat_count">\
</div>',
        link: function (scope, element, attrs) {

        }
    }
})
.directive('wmTimestamp', function () {
    return {
        restrict: 'EA',
        replace: true,
        scope: {
            ident: '@',
            ngModel: '='
        },
        template:
'<div class="input-group">\
    <input type="text" ng-model="ngModel" wm-timestamp-formatter class="form-control">\
    <span class="input-group-addon">\
        <label class="radio-inline">\
            <input type="radio" name="tf_m_[[ident]]" id="tf_m" ng-model="time_format.type" ng-value="\'m\'"> мин.\
        </label>\
        <label class="radio-inline">\
            <input type="radio" name="tf_d_[[ident]]" id="tf_d" ng-model="time_format.type" ng-value="\'d\'"> дн.\
        </label>\
        <label class="radio-inline">\
            <input type="radio" name="tf_w_[[ident]]" id="tf_w" ng-model="time_format.type" ng-value="\'w\'"> нед.\
        </label>\
    </span>\
</div>',
        link: function (scope, element, attrs) {
            scope.time_format = {
                type: 'd'
            };
        }
    }
})
.directive('wmTimestampFormatter', function() {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function (scope, element, attrs, ngModelCtrl) {
            var formatViewValue = function (viewValue, format_type) {
                if (format_type === 'm') {
                    viewValue = viewValue / 60;
                } else if (format_type === 'd') {
                    viewValue = viewValue / 86400;
                } else if(format_type === 'w') {
                    viewValue = viewValue / 604800;
                }
                return viewValue;
            };
            scope.$watch('time_format.type', function (newVal) {
                ngModelCtrl.$setViewValue(formatViewValue(ngModelCtrl.$modelValue, newVal));
                ngModelCtrl.$render();
            });
            ngModelCtrl.$formatters.push(function (viewValue) {
                formatViewValue(viewValue, scope.time_format.type);
            });
            ngModelCtrl.$parsers.unshift(function (value) {
                if (scope.time_format.type === 'm') {
                    value = value * 60;
                } else if (scope.time_format.type === 'd') {
                    value = value * 86400;
                } else if(scope.time_format.type === 'w') {
                    value = value * 604800;
                }
                return value;
            });
        }
    }
})
;