'use strict';

WebMis20
.controller('PricelistListConfigCtrl', ['$scope', '$controller', '$window', 'WMConfig', 'PriceList',
        function ($scope, $controller, $window, WMConfig, PriceList) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.EntityClass = PriceList;

    $scope.setSimpleModalConfig({
        size: 'lg',
        templateUrl: '/caesar/misconfig/pricelist/pricelist-edit-modal.html'
    });
    $scope.openPriceListItems = function (idx) {
        $window.location.href = WMConfig.url.misconfig.html_price_list + $scope.item_list[idx].id;
    };

    PriceList.instantiateAll().then(function (pricelist) {
        $scope.item_list = pricelist;
    });
}])
.controller('PricelistConfigCtrl', ['$scope', '$controller', 'PriceListItem',
        function ($scope, $controller, PriceListItem) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setViewParams({paginate: true});
    $scope.EntityClass = PriceListItem;
    $scope.setSimpleModalConfig({
        controller: 'PricelistItemConfigModalCtrl',
        size: 'lg',
        templateUrl: '/caesar/misconfig/pricelist/pricelist-item-edit-modal.html'
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
            pricelist_id: $scope.pricelist_id,
            name: $scope.flt.model.name || undefined,
            code: $scope.flt.model.code || undefined,
            beg_date_from: $scope.flt.model.beg_date_from || undefined,
            beg_date_to: $scope.flt.model.beg_date_to || undefined,
            end_date_from: $scope.flt.model.end_date_from || undefined,
            end_date_to: $scope.flt.model.end_date_to || undefined
        };
        $scope._refreshData(args).then(setData);
    };
    $scope.onPageChanged = function () {
        $scope.refreshData();
    };
    $scope.create_new = function () {
        $scope.EntityClass.instantiate(undefined, {'new': true, pricelist_id: $scope.pricelist_id}).
            then(function (item) {
                $scope._editNew(item);
            });
    };

    $scope.init = function (pricelist_id) {
        $scope.pricelist_id = pricelist_id;
        $scope.refreshData();
    };
}])
.controller('PricelistItemConfigModalCtrl', ['$scope', '$modalInstance', 'model',
    function ($scope, $modalInstance, model) {
        $scope.model = model;

        $scope.onServiceChanged = function () {
            $scope.model.service_code = $scope.model.service.code;
            $scope.model.service_name = $scope.model.service.name;
        };
        $scope.onChkAggregatedChanged = function () {
            if ($scope.model.is_accumulative_price) {
                $scope.model.price = '0';
            }
        };
        $scope.close = function () {
            $scope.model.save().
                then(function (model) {
                    $scope.$close(model);
                });
        };
}])
;