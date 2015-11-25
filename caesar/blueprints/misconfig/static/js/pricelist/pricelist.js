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

    $scope.model = [];
    PriceList.instantiateAll().then(function (pricelist) {
        $scope.item_list = pricelist;
    });
}])
.controller('PricelistConfigCtrl', ['$scope', '$controller', 'PriceListItem',
        function ($scope, $controller, PriceListItem) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.EntityClass = PriceListItem;

    $scope.create_new = function () {
        $scope.EntityClass.instantiate(undefined, {'new': true, pricelist_id: $scope.pricelist_id}).
            then(function (item) {
                $scope._editNew(item);
            });
    };

    $scope.init = function (pricelist_id) {
        $scope.pricelist_id = pricelist_id;
        PriceListItem.instantiateAll({
            pricelist_id: $scope.pricelist_id
        }).then(function (items) {
            $scope.item_list = items;
        });
    };

    $scope.setSimpleModalConfig({
        controller: 'PricelistItemConfigModalCtrl',
        size: 'lg',
        templateUrl: '/caesar/misconfig/pricelist/pricelist-item-edit-modal.html'
    });
}])
.controller('PricelistItemConfigModalCtrl', ['$scope', '$modalInstance', 'model',
    function ($scope, $modalInstance, model) {
        $scope.model = model;

        $scope.onServiceChanged = function () {
            $scope.model.service_code = $scope.model.service.code;
            $scope.model.service_name = $scope.model.service.name;
        };
        $scope.close = function () {
            $scope.model.save().
                then(function (model) {
                    $scope.$close(model);
                });
        };
}])
;