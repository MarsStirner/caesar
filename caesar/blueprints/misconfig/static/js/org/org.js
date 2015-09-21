'use strict';

WebMis20
.controller('OrgConfigCtrl', ['$scope', '$controller', 'Organisation',
        function ($scope, $controller, Organisation) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setSimpleModalConfig({
        controller: 'OrgConfigModalCtrl',
        templateUrl: '/caesar/misconfig/org/org-edit-modal.html'
    });
    $scope.EntityClass = Organisation;

    Organisation.instantiateAll().then(function (orgs) {
        $scope.item_list = orgs;
    });
}])
.controller('OrgConfigModalCtrl', ['$scope', '$modalInstance', 'model',
        function ($scope, $modalInstance, model) {
    $scope.model = model;
    $scope.close = function () {
        $scope.model.save().
            then(function (org) {
                $scope.$close(org);
            });
    };
}])
;