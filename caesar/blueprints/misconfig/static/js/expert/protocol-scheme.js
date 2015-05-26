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
        }, //{
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
.factory('ExpertSchemeMeasure', ['ApiCalls', 'BasicModel', 'Measure', function (ApiCalls, BasicModel, Measure) {
    var ExpertSchemeMeasure = function (data) {
        BasicModel.call(this, data);
    };
    ExpertSchemeMeasure.inheritsFrom(BasicModel);
    ExpertSchemeMeasure.initialize({
        fields: ['id', 'scheme_id', {
            name: 'measure',
            klass: Measure
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
                console.log('watch called: ' + new_values);
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
.controller('SchemeMeasureConfigCtrl', ['$scope', '$controller', '$modal', 'ExpertScheme', 'ExpertSchemeMeasure', 'Measure',
        function ($scope, $controller, $modal, ExpertScheme, ExpertSchemeMeasure, Measure) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    var schemeMeasureModalParams = {
        controller: function ($scope, $modalInstance, scheme_measure) {
            $scope.scheme_measure = scheme_measure;

            Measure.instantiateAll().then(function (items) {
                $scope.measure_list = items;
            });

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

    $scope.formatMkbList = function (mkbs) {
        return mkbs.map(function (mkb_scheme) {
            return mkb_scheme.mkb.code;
        }).join(', ');
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
        });
    ExpertSchemeMeasure.instantiateByScheme($scope.getUrlParam('scheme_id')).
        then(function (scheme_measures) {
            $scope.scheme.scheme_measures = scheme_measures;
        })
}])
;