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
.factory('ExpertScheme', ['BasicModel', 'ExpertSchemeMKB', function (BasicModel, ExpertSchemeMKB) {
    var ExpertScheme = function (data) {
        BasicModel.call(this, data);
    };
    ExpertScheme.inheritsFrom(BasicModel);
    ExpertScheme.initialize({
        fields: ['id', 'code', 'name', 'number', 'protocol_id', {
            name: 'mkbs',
            klass: ExpertSchemeMKB
        }],
        base_url: '/misconfig/api/v1/expert/protocol/scheme/'
    }, ExpertScheme);
    return ExpertScheme;
}])
.factory('ExpertSchemeMKB', ['BasicModel', function (BasicModel) {
    var ExpertSchemeMKB = function (data) {
        BasicModel.call(this, data);
    };
    ExpertSchemeMKB.inheritsFrom(BasicModel);
    ExpertSchemeMKB.initialize({
        fields: ['id', 'scheme_id', 'mkb']
    }, ExpertSchemeMKB);
    return ExpertSchemeMKB;
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
.controller('ExpertProtocolConfigCtrl', ['$scope', '$controller', '$modal', 'ExpertProtocol', 'ExpertScheme',
        function ($scope, $controller, $modal, ExpertProtocol, ExpertScheme) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    var schemeModalParams = {
        controller: function ($scope, $modalInstance, scheme) {
            $scope.scheme = scheme;

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
    $scope.create_new_scheme = function () {
        ExpertScheme.instantiate('new', $scope.protocol.id).
            then(function (scheme) {
                get_scheme_edit_modal(scheme).result.then(function () {
                    $scope.protocol.schemes.push(scheme);
                });
            });
    };
    $scope.edit_scheme = function (index) {
        var scheme = $scope.protocol.schemes[index].clone();
        get_scheme_edit_modal(scheme).result.then(function () {
            $scope.protocol.schemes.splice(index, 1, scheme);
        });
    };
    ExpertProtocol.instantiate($scope.getUrlParam('protocol_id')).
        then(function (protocol) {
            $scope.protocol = protocol;
        });
}])
;