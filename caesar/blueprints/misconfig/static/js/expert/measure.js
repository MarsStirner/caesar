'use strict';

WebMis20
.controller('MeasureConfigCtrl', ['$scope', '$controller', 'Measure',
        function ($scope, $controller, Measure) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setViewParams({paginate: true});
    $scope.setSimpleModalConfig({
        controller: 'MeasureConfigModalCtrl',
        templateUrl: '/caesar/misconfig/expert/protocol/measure-edit-modal.html'
    });
    $scope.EntityClass = Measure;

    var setData = function (paged_data) {
        $scope.item_list = paged_data.items;
        $scope.pager.record_count = paged_data.count;
        $scope.pager.pages = paged_data.total_pages;
    };
    $scope.refreshData = function () {
        var args = {
            paginate: true,
            page: $scope.pager.current_page,
            per_page: $scope.pager.per_page
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
.controller('MeasureConfigModalCtrl', ['$scope', '$modalInstance', 'model',
    function ($scope, $modalInstance, model) {
        $scope.model = model;
        $scope.close = function () {
            $scope.model.save().
                then(function (model) {
                    $scope.$close(model);
                });
        };
}])
;