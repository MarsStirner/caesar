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
.controller('PersonConfigModalCtrl', ['$scope','$q', '$modalInstance', 'model', 'RefBookService',
    function ($scope, $q, $modalInstance, model, RefBookService) {
        $scope.rbGender = RefBookService.get('Gender');
        $scope.rbUserProfile = RefBookService.get('rbUserProfile');
        $scope.rbContactType = RefBookService.get('rbContactType');
        $scope.contactTypeByCode = {};
        $scope.init = function () {
            $q.all([$scope.rbContactType.loading]).then(function () {
                _.map($scope.rbContactType.objects, function(item) {
                        $scope.contactTypeByCode[item.code] = item;
                });

            });

        };
        $scope.forms = {};
        $scope.ableToSave = true;
        $scope.$watch('forms.CRD.password.$error.pattern', function(n, o){
            $scope.ableToSave = n;
        });

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

        $scope.addContact = function(group, code){
            var ct = $scope.contactTypeByCode[code];
            $scope.model.addNewContact(ct, group);
        };

        $scope.deleteContact = function(conGroup){
            // conGroup=one from ['phones', 'skypes', 'emails']
            var ind = $scope.model[conGroup].indexOf(this.cont);
            if (ind !== -1) {$scope.model[conGroup].splice(ind, 1)};
        }
        $scope.close = function () {
            $scope.model.save(undefined, undefined, {
                with_profiles: true
            }).
                then(function (model) {
                    $scope.$close(model);
                });
        };
        $scope.init();
}])
;