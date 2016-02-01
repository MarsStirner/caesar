'use strict';

WebMis20
.controller('RbServiceListConfigCtrl', ['$scope', '$controller', 'WMConfig', 'rbService',
        function ($scope, $controller, WMConfig, rbService) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setViewParams({paginate: true});
    $scope.EntityClass = rbService;
    $scope.setSimpleModalConfig({
        controller: 'RbServiceConfigModalCtrl',
        size: 'lg',
        templateUrl: '/caesar/misconfig/refbook/rbservice-edit-modal.html'
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
            code: $scope.flt.model.code || undefined,
            beg_date_from: $scope.flt.model.beg_date_from || undefined,
            beg_date_to: $scope.flt.model.beg_date_to || undefined,
            end_date_from: $scope.flt.model.end_date_from || undefined,
            end_date_to: $scope.flt.model.end_date_to || undefined,
            is_complex: $scope.flt.model.is_complex !== undefined ? $scope.flt.model.is_complex : undefined
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
.controller('RbServiceConfigModalCtrl', ['$scope', '$modalInstance', 'model',
    function ($scope, $modalInstance, model) {
        $scope.model = model;
        $scope.new_item = {
            model: null,
            service_kind: null
        };
        $scope.isComplex = function () {
            return $scope.model.is_complex;
        };
        $scope.addNewItem = function () {
            // disable simple looped service groups
            if ($scope.new_item.model.id === $scope.model.id) return;

            $scope.model.getNewGroupItem()
                .then(function (assoc_group) {
                    assoc_group.service_kind = $scope.new_item.service_kind;
                    assoc_group.subservice = $scope.new_item.model;

                    $scope.model.addGroupItem(assoc_group);
                    $scope.new_item.model = null;
                    $scope.new_item.service_kind = null;
                });
        };
        $scope.removeItem = function (idx) {
            $scope.model.removeGroupItem(idx)
        };
        $scope.btnAddItemDisabled = function () {
            return !safe_traverse($scope.new_item, ['model', 'id']);
        };

        $scope.close = function () {
            $scope.model.save().
                then(function (model) {
                    $scope.$close(model);
                });
        };
}])
;