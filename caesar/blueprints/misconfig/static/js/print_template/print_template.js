'use strict';

WebMis20
.controller('PrintTemplateConfigCtrl', ['$scope', '$controller', 'rbPrintTemplate',
        function ($scope, $controller, rbPrintTemplate) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setSimpleModalConfig({
        controller: 'PrintTemplateConfigModalCtrl',
        templateUrl: '/caesar/misconfig/print_template/print-template-edit-modal.html',
        windowClass: 'modal-scrollable'
    });
    $scope.EntityClass = rbPrintTemplate;

    rbPrintTemplate.instantiateAll().then(function (orgs) {
        $scope.item_list = orgs;
    });
}])
.controller('PrintTemplateConfigModalCtrl', ['$scope', '$modalInstance', 'model',
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