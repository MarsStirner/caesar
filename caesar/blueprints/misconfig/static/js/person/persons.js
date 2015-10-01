'use strict';

WebMis20
.factory('Person', ['BasicModel', function (BasicModel) {
    var Person = function (data) {
        BasicModel.call(this, data);
    };
    Person.inheritsFrom(BasicModel);
    Person.initialize({
        fields: ['id', 'last_name', 'first_name', 'patr_name', 'name_text', 'post', 'speciality',
            'organisation', 'org_structure', 'deleted', 'inn', 'snils', 'birth_date', 'sex'
        ],
        base_url: '/misconfig/api/v1/person/'
    }, Person);
    return Person;
}])
.controller('PersonConfigCtrl', ['$scope', '$controller', 'Person',
        function ($scope, $controller, Person) {
    $controller('MisConfigBaseCtrl', {$scope: $scope});

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
        $scope.formatOrgName = function (org) {
            return org && org.short_name;
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