'use strict';

WebMis20
.controller('OrgConfigCtrl', ['$scope', '$controller', 'Organisation',
        function ($scope, $controller, Organisation) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setViewParams({paginate: true});
    $scope.EntityClass = Organisation;
    $scope.setSimpleModalConfig({
        controller: 'OrgConfigModalCtrl',
        templateUrl: '/caesar/misconfig/org/org-edit-modal.html',
        size: 'lg'
    });

    var setData = function (paged_data) {
        $scope.item_list = paged_data.items;
        $scope.pager.record_count = paged_data.count;
        $scope.pager.pages = paged_data.total_pages;
    };
    $scope.refreshData = function () {
        var args = {
            paginate: true,
            page: $scope.pager.current_page,
            per_page: $scope.pager.per_page,
            name: $scope.flt.model.name || undefined,
            infis: $scope.flt.model.infis || undefined,
            is_lpu: $scope.flt.model.is_lpu || undefined,
            is_stationary: $scope.flt.model.is_stationary || undefined,
            is_insurer: $scope.flt.model.is_insurer || undefined
        };
        $scope._refreshData(args).then(setData);
    };
    $scope.onPageChanged = function () {
        $scope.refreshData();
    };

    $scope.init = function () {
        $scope.refreshData();
    };

    $scope.init();
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