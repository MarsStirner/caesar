'use strict';

WebMis20
.factory('PriceList', ['BasicModel', function (BasicModel) {
    var PriceList = function (data) {
        BasicModel.call(this, data);
    };
    PriceList.inheritsFrom(BasicModel);
    PriceList.initialize({
        fields: ['id', 'name', 'finance', 'deleted'],
        base_url: '/misconfig/api/v1/price/'
    }, PriceList);
    return PriceList;
}])
.factory('ContractTariff', ['BasicModel', function (BasicModel) {
    var ContractTariff = function (data) {
        BasicModel.call(this, data);
    };
    ContractTariff.inheritsFrom(BasicModel);
    ContractTariff.initialize({
        fields: ['id', 'name', 'code', 'deleted', 'begDate', 'endDate', 'amount', 'uet', 'rbServiceFinance', 'service', 'event_type'],
        base_url: '/misconfig/api/v1/tariff/'
    }, ContractTariff);
    return ContractTariff;
}])
.controller('PriceConfigCtrl', ['$scope', '$controller', 'PriceList',
        function ($scope, $controller, PriceList) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.EntityClass = PriceList;

    $scope.setSimpleModalConfig({
        controller: 'PriceConfigModalCtrl',
        size: 'lg',
        templateUrl: '/caesar/misconfig/price/price-edit-modal.html'
    });
    $scope.tariff_url = function (item){
        window.location = '/misconfig/price_list/' + item.id + '/';
    };

    $scope.model = [];
    PriceList.instantiateAll().then(function (pricelist) {
        $scope.item_list = pricelist;
    });
}])
.controller('PriceConfigModalCtrl', ['$scope', '$modalInstance', 'model', 'RefBookService',
    function ($scope, $modalInstance, model, RefBookService) {
        $scope.rbFinance = RefBookService.get('rbFinance');
        $scope.model = model;
        $scope.close = function () {
            $scope.model.save().
                then(function (model) {
                    $scope.$close(model);
                });
        };
}])
.controller('TariffConfigCtrl', ['$scope', '$controller', 'ContractTariff',
        function ($scope, $controller, ContractTariff) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.EntityClass = ContractTariff;

    $scope.init = function (price_id) {
        $scope.price_id = price_id;
        ContractTariff.instantiateAll({price_id: $scope.price_id}).then(function (tariff) {
            $scope.item_list = tariff;
        });
    };

    $scope.setSimpleModalConfig({
        controller: 'TariffConfigModalCtrl',
        size: 'lg',
        templateUrl: '/caesar/misconfig/price/tariff-edit-modal.html'
    });
}])
.controller('TariffConfigModalCtrl', ['$scope', '$modalInstance', 'model', 'RefBookService',
    function ($scope, $modalInstance, model, RefBookService) {
        $scope.rbService = RefBookService.get('rbService');
        $scope.eventType = RefBookService.get('eventType');
        $scope.rbServiceFinance = RefBookService.get('rbServiceFinance');
        $scope.model = model;
        $scope.close = function () {
            $scope.model.save().
                then(function (model) {
                    $scope.$close(model);
                });
        };
}])
;