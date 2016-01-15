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
            per_page: $scope.pager.per_page  //,
            //number: $scope.flt.model.number || undefined,
            //finance_id: safe_traverse($scope.flt.model, ['finance_type', 'id']),
            //payer_query: $scope.flt.model.payer_query || undefined,
            //recipient_query: $scope.flt.model.recipient_query || undefined,
            //beg_date_from: $scope.flt.model.beg_date_from || undefined,
            //beg_date_to: $scope.flt.model.beg_date_to || undefined,
            //end_date_from: $scope.flt.model.end_date_from || undefined,
            //end_date_to: $scope.flt.model.end_date_to || undefined,
            //set_date_from: $scope.flt.model.set_date_from || undefined,
            //set_date_to: $scope.flt.model.set_date_to || undefined
        };
        $scope._refreshData(args).then(setData);
    };
    $scope.onPageChanged = function () {
        $scope.refreshData();
    };
    $scope.toggleFilter = function () {
        $scope.flt.enabled = !$scope.flt.enabled;
    };
    $scope.isFilterEnabled = function () {
        return $scope.flt.enabled;
    };
    $scope.clear = function () {
        $scope.pager.current_page = 1;
        $scope.pager.pages = null;
        $scope.pager.record_count = null;
        $scope.flt.model = {};
    };
    $scope.clearAll = function () {
        $scope.clear();
        $scope.item_list = [];
    };
    $scope.getData = function () {
        $scope.pager.current_page = 1;
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
            model: null
        };
        $scope.isComplex = function () {
            return $scope.model.is_complex;
        };
        $scope.addNewItem = function () {
            // disable simple looped service groups
            if ($scope.new_item.model.id === $scope.model.id) return;

            $scope.model.subservice_list.push($scope.new_item.model);
            $scope.new_item.model = null;
        };
        $scope.removeItem = function (idx) {
            $scope.model.subservice_list.splice(idx, 1);
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