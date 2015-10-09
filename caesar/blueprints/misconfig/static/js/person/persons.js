'use strict';

WebMis20
.factory('Person', ['BasicModel', function (BasicModel) {
    var Person = function (data) {
        BasicModel.call(this, data);
    };
    Person.inheritsFrom(BasicModel);
    Person.initialize({
        fields: ['id', 'last_name', 'first_name', 'patr_name', 'name_text', 'post', 'speciality',
            'organisation', 'org_structure', 'deleted', 'inn', 'snils', 'birth_date', 'sex', 'user_profiles', 'login', 'new_password'
        ],
        base_url: '/misconfig/api/v1/person/'
    }, Person);
    return Person;
}])
.controller('PersonConfigCtrl', ['$scope', '$controller', 'Person',
        function ($scope, $controller, Person) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});
    $scope.EntityClass = Person;
    $scope.setSimpleModalConfig({
        controller: 'PersonConfigModalCtrl',
        size: 'lg',
        templateUrl: '/caesar/misconfig/person/person-edit-modal.html'
    });

    $scope.model = [];
    Person.instantiateAll().then(function (persons) {
        $scope.item_list = persons;
    });
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