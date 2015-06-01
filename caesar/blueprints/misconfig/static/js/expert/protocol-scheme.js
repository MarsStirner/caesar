'use strict';

WebMis20
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
    return ExpertProtocol;
}])
.factory('ExpertScheme', ['BasicModel', 'ExpertSchemeMKB', 'ExpertSchemeMeasure',
        function (BasicModel, ExpertSchemeMKB, ExpertSchemeMeasure) {
    var ExpertScheme = function (data) {
        BasicModel.call(this, data);
        this.scheme_measures = [];
    };
    ExpertScheme.inheritsFrom(BasicModel);
    ExpertScheme.initialize({
        fields: ['id', 'code', 'name', 'number', 'protocol_id', {
            name: 'mkbs',
            klass: ExpertSchemeMKB
        }//, {
           // name: 'scheme_measures',
           // klass: ExpertSchemeMeasure}
        ],
        base_url: '/misconfig/api/v1/expert/protocol/scheme/'
    }, ExpertScheme);
    ExpertScheme.prototype.addMkb = function (rbMkb) {
        // TODO: redo
        var self = this;
        ExpertSchemeMKB.instantiate('new', self.id).
            then(function (scheme_mkb) {
                scheme_mkb.mkb = rbMkb;
                self.mkbs.push(scheme_mkb);
                return scheme_mkb;
            });
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
.controller('ExpertProtocolListConfigCtrl', ['$scope', '$controller', '$window', 'RbService',
        function ($scope, $controller, $window, RbService) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.create_new = function () {
        $window.location.href = '/misconfig/expert/protocol/protocols/protocol/#?protocol_id=new';
    };
    $scope.edit = function (index) {
        $window.location.href = '/misconfig/expert/protocol/protocols/protocol/#?protocol_id={0}'.format($scope.item_list[index].id);
    };
    RbService.getItemList('ExpertProtocol').then(function (protocols) {
        $scope.item_list = protocols;
    });
}])
.controller('ExpertProtocolConfigCtrl', ['$scope', '$controller', '$modal', '$window', 'ExpertProtocol', 'ExpertScheme',
        function ($scope, $controller, $modal, $window, ExpertProtocol, ExpertScheme) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    var schemeModalParams = {
        controller: function ($scope, $modalInstance, scheme) {
            $scope.scheme = scheme;
            $scope.proxy_mkb = {
                list: scheme.mkbs.map(function (mkb_scheme) { return mkb_scheme.mkb; })
            };

            $scope.$watchCollection('proxy_mkb.list', function (new_values) {
                var new_len = new_values.length;
                new_values.forEach(function (value, index) {
                    if ($scope.scheme.mkbs.length <= index) {
                        $scope.scheme.addMkb(value);
                    } else {
                        $scope.scheme.mkbs[index].mkb = value;
                    }
                });
                $scope.scheme.mkbs.splice(new_len);
            });

            $scope.close = function () {
                $scope.scheme.save().
                    then(function (scheme) {
                        $scope.$close(scheme);
                    });
            };
        },
        size: 'lg',
        templateUrl: '/caesar/misconfig/expert/protocol/scheme-edit-modal.html',
        resolve: {}
    };
    var get_scheme_edit_modal = function (scheme) {
        schemeModalParams.resolve.scheme = function () {
            return scheme
        };
        return $modal.open(schemeModalParams);
    };

    $scope.formatMkbList = function (mkbs) {
        return mkbs.map(function (mkb_scheme) {
            return mkb_scheme.mkb.code;
        }).join(', ');
    };
    $scope.saveProtocol = function () {
        $scope.protocol.save().
            then(function (protocol) {
                $window.location.href = '/misconfig/expert/protocol/protocols/protocol/#?protocol_id={0}'.format(protocol.id);
            });
    };
    $scope.createNewScheme = function () {
        ExpertScheme.instantiate('new', $scope.protocol.id).
            then(function (scheme) {
                get_scheme_edit_modal(scheme).result.then(function (scheme) {
                    $scope.protocol.schemes.push(scheme);
                });
            });
    };
    $scope.editScheme = function (index) {
        var scheme = $scope.protocol.schemes[index].clone();
        get_scheme_edit_modal(scheme).result.then(function () {
            $scope.protocol.schemes.splice(index, 1, scheme);
        });
    };
    $scope.editMeasures = function (index) {
        $window.location.href = '/misconfig/expert/protocol/protocols/scheme_measures/#?scheme_id={0}'.format(
            $scope.protocol.schemes[index].id
        );
    };

    ExpertProtocol.instantiate($scope.getUrlParam('protocol_id')).
        then(function (protocol) {
            $scope.protocol = protocol;
        });
}])
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