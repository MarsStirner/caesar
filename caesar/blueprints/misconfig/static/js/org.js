'use strict';

WebMis20
.factory('Organisation', ['SimpleRb', function (SimpleRb) {
    var Organisation = function (data) {
        SimpleRb.call(this, data);
    };
    Organisation.inheritsFrom(SimpleRb);
    Organisation.initialize({
        fields: ['id', 'short_name', 'full_name', 'title', 'infis', 'is_insurer',
            'is_hospital', 'address', 'phone', 'kladr_locality'],
        base_url: '{0}Organisation/'.format(Organisation.getBaseUrl())
    }, Organisation);
    return Organisation;
}])
.controller('OrgConfigCtrl', ['$scope', '$controller', 'Organisation',
        function ($scope, $controller, Organisation) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setSimpleModalConfig({
        templateUrl: '/caesar/misconfig/refbook/org-edit-modal.html'
    });
    $scope.EntityClass = Organisation;
    Organisation.instantiateAll().then(function (orgs) {
        $scope.item_list = orgs;
    });
}])
;