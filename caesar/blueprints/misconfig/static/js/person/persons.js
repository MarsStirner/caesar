'use strict';

WebMis20
.controller('PersonConfigCtrl', ['$scope', '$controller', 'Person',
        function ($scope, $controller, Person) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.setViewParams({paginate: true});
    $scope.EntityClass = Person;
    $scope.setSimpleModalConfig({
        controller: 'PersonConfigModalCtrl',
        size: 'lg',
        templateUrl: '/caesar/misconfig/person/person-edit-modal.html'
    });

    var setData = function (paged_data) {
        $scope.item_list = paged_data.items;
        $scope.pager.record_count = paged_data.count;
        $scope.pager.pages = paged_data.total_pages;
    };
    $scope.refreshData = function () {
        var args = {
            with_profiles: true,
            paginate: true,
            page: $scope.pager.current_page,
            per_page: $scope.pager.per_page,
            fio: $scope.flt.model.fio || undefined,
            speciality_id: safe_traverse($scope.flt.model, ['speciality', 'id']),
            post_id: safe_traverse($scope.flt.model, ['post', 'id']),
            org_id: safe_traverse($scope.flt.model, ['org', 'id'])
        };
        $scope._refreshData(args).then(setData);
    };
    $scope.onPageChanged = function () {
        $scope.refreshData();
    };
    $scope.create_new = function () {
        $scope.EntityClass.instantiate(undefined, {'new': true, with_profiles: true}).
            then(function (item) {
                $scope._editNew(item);
            });
    };

    $scope.init = function () {
        $scope.refreshData();
    };

    $scope.init();
}])
.controller('PersonConfigModalCtrl', ['$scope', '$modalInstance', 'model', 'RefBookService',
    function ($scope, $modalInstance, model, RefBookService) {
        $scope.rbGender = RefBookService.get('Gender');
        $scope.rbUserProfile = RefBookService.get('rbUserProfile');
        $scope.formatOrgName = function (org) {
            return org && org.short_name;
        };
        $scope.has_role = function (profile) {
            return _.where($scope.model.user_profiles,profile).length > 0;
        };
        $scope.toggleRole = function (profile) {
            for (var i = 0; i < $scope.model.user_profiles.length; i++) {
                if ($scope.model.user_profiles[i].code == profile.code) {
                    $scope.model.user_profiles.splice(i, 1);
                    return;
                }
            }
            $scope.model.user_profiles.push(profile);
        };
        $scope.model = model;
        $scope.close = function () {
            $scope.model.save().
                then(function (model) {
                    $scope.$close(model);
                });
        };
}])
;