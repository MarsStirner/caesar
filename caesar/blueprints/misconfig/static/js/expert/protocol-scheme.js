'use strict';

WebMis20
.controller('ExpertProtocolListConfigCtrl', ['$scope', '$controller', '$window', 'WMConfig', 'ExpertProtocol',
        function ($scope, $controller, $window, WMConfig, ExpertProtocol) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

    $scope.create_new = function () {
        $window.location.href = WMConfig.url.misconfig.html_expert_protocol_protocols + '#?protocol_id=new';
    };
    $scope.edit = function (index) {
        $window.location.href = WMConfig.url.misconfig.html_expert_protocol_protocols + '#?protocol_id=' + $scope.item_list[index].id;
    };
    ExpertProtocol.instantiateAll().then(function (protocols) {
        $scope.item_list = protocols;
    });
}])
.controller('ExpertProtocolConfigCtrl', ['$scope', '$controller', '$window', 'WMConfig', 'ExpertProtocol',
        function ($scope, $controller, $window, WMConfig, ExpertProtocol) {
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

    $scope.formatMkbList = function (mkbs) {
        return mkbs.map(function (mkb) {
            return mkb.code;
        }).join(', ');
    };
    $scope.saveProtocol = function () {
        $scope.protocol.save().
            then(function (protocol) {
                $window.location.href = WMConfig.url.misconfig.html_expert_protocol_protocols + '#?protocol_id=' + protocol.id;
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
    $scope.removeScheme = function (index) {
        $scope._remove($scope.protocol.schemes[index]);
    };
    $scope.restoreScheme = function (index) {
        $scope._restore($scope.protocol.schemes[index]);
    };
    $scope.editMeasures = function (index) {
        $window.location.href =  WMConfig.url.misconfig.html_expert_protocol_scheme_measures + '#?scheme_id=' + $scope.protocol.schemes[index].id;
    };

    ExpertProtocol.instantiate($scope.getUrlParam('protocol_id'), { with_schemes: true }).
        then(function (protocol) {
            $scope.protocol = protocol;
        });
}])
.controller('ExpertSchemeConfigModalCtrl', ['$scope', '$modalInstance', 'scheme',
        function ($scope, $modalInstance, scheme) {
    $scope.scheme = scheme;

    $scope.close = function () {
        $scope.scheme.save().
            then(function (scheme) {
                $scope.$close(scheme);
            });
    };
}])
;