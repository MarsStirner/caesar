'use strict';

WebMis20
.factory('Organisation', ['SimpleRb', function (SimpleRb) {
    var name = 'Organisation',
        _fields = ['id', 'short_name', 'full_name', 'title', 'infis', 'is_insurer',
            'is_hospital', 'address', 'phone', 'kladr_locality'];
    var Organisation = function (data) {
        SimpleRb.call(this, name, data, _fields);
    };
    Organisation.prototype = Object.create(SimpleRb.prototype);
    Organisation.prototype.constructor = Organisation;
    return Organisation;
}])
.controller('OrgConfigCtrl', ['$scope', '$controller', 'RbService',
        function ($scope, $controller, RbService) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.modalTemplate = "/caesar/misconfig/refbook/org-edit-modal.html";
    $scope.EntityClass = RbService.getClass('Organisation');
    RbService.getItemList('Organisation').then(function (orgs) {
        $scope.item_list = orgs;
    });
}])
;