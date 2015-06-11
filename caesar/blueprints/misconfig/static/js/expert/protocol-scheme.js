'use strict';

WebMis20
.controller('ExpertProtocolListConfigCtrl', ['$scope', '$controller', '$window', 'ExpertProtocol',
        function ($scope, $controller, $window, ExpertProtocol) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.create_new = function () {
        $window.location.href = '/misconfig/expert/protocol/protocols/protocol/#?protocol_id=new';
    };
    $scope.edit = function (index) {
        $window.location.href = '/misconfig/expert/protocol/protocols/protocol/#?protocol_id={0}'.format(
            $scope.item_list[index].id
        );
    };
    ExpertProtocol.instantiateAll().then(function (protocols) {
        $scope.item_list = protocols;
    });
}])
.controller('ExpertProtocolConfigCtrl', ['$scope', '$controller', '$window', 'ExpertProtocol',
        function ($scope, $controller, $window, ExpertProtocol) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    var _schemeModalParams = {
        controller: 'ExpertSchemeConfigModalCtrl',
        size: 'lg',
        templateUrl: '/caesar/misconfig/expert/protocol/scheme-edit-modal.html',
        resolve: {}
    };
    var getSchemeEditModal = function (scheme) {
        _schemeModalParams.resolve.scheme = function () {
            return scheme
        };
        return $scope.getEditModal(_schemeModalParams);
    };

    $scope.formatMkbList = function (scheme_mkbs) {
        return scheme_mkbs.map(function (mkb_scheme) {
            return mkb_scheme.mkb.code;
        }).join(', ');
    };
    $scope.saveProtocol = function () {
        $scope.protocol.save().
            then(function (protocol) {
                $window.location.href = '/misconfig/expert/protocol/protocols/protocol/#?protocol_id={0}'.format(
                    protocol.id
                );
            });
    };
    $scope.createNewScheme = function () {
        $scope.protocol.getNewScheme().
            then(function (scheme) {
                getSchemeEditModal(scheme).result.then(function (scheme) {
                    $scope.protocol.addScheme(scheme);
                });
            });
    };
    $scope.editScheme = function (index) {
        var scheme = $scope.protocol.schemes[index].clone();
        getSchemeEditModal(scheme).result.then(function () {
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
.controller('ExpertSchemeConfigModalCtrl', ['$scope', '$modalInstance', 'scheme',
        function ($scope, $modalInstance, scheme) {
    $scope.scheme = scheme;
    $scope.proxy_mkb = {
        list: scheme.scheme_mkbs.map(function (mkb_scheme) { return mkb_scheme.mkb; })
    };

    $scope.$watchCollection('proxy_mkb.list', function (new_values) {
        var new_len = new_values.length;
        new_values.forEach(function (value, index) {
            if ($scope.scheme.scheme_mkbs.length <= index) {
                $scope.scheme.getNewMkb().
                    then(function (scheme_mkb) {
                        scheme_mkb.mkb = value;
                        $scope.scheme.addMkb(scheme_mkb);
                    });
            } else {
                $scope.scheme.scheme_mkbs[index].mkb = value;
            }
        });
        $scope.scheme.scheme_mkbs.splice(new_len);
    });
    $scope.filterMkbChoices = function (mkb) {
        var used_codes = $scope.scheme.scheme_mkbs.map(function (scheme_mkb) { return scheme_mkb.mkb.code });
        return !used_codes.has(mkb.code);
    };
    $scope.close = function () {
        $scope.scheme.save().
            then(function (scheme) {
                $scope.$close(scheme);
            });
    };
}])
;