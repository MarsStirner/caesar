/**
 * Created by mmalkov on 04.02.15.
 */

RisarSetupApp = angular.module('RisarSetupApp', ['ngSanitize', 'ui.bootstrap']);
RisarSetupApp.config(function ($interpolateProvider, $tooltipProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
    $tooltipProvider.setTriggers({
        'mouseenter': 'mouseleave',
        'click': 'click',
        'focus': 'blur',
        'never': 'mouseleave',
        'show_popover': 'hide_popover'
    })
});

RisarSetupApp.controller('SetupMainCtrl', function ($scope, $window) {
    $scope.page = 0;
    $scope.save = function () {
    }
});

RisarSetupApp.controller('RisarRoutingSetup', function ($scope, $http) {
    $scope.query = '';
    $scope.list = [];
    $scope.clipboard = null;
    $scope.copy_clipboard = function (row) {
        $scope.clipboard = row.diagnoses;
    };
    $scope.paste_clipboard = function (row) {};
    $http.get('/risar_config/api/routing.json').success(function (data) {
        $scope.list = data.result;
    })
});