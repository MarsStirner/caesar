/**
 * Created by mmalkov on 19.03.15.
 */
'use strict';

WebMis20
.service('HTMCConfigService', function (ApiCalls, NotificationService) {
    var wrapper = ApiCalls.wrapper;
    var quota_catalog_url = '/misconfig/api/v1/quota_catalog';
    this.catalog = {
        get_list: function () {
            return wrapper('GET', quota_catalog_url)
        },
        details: function (id) {
            return wrapper('GET', quota_catalog_url + '/' + id)
        },
        create: function (data) {
            return wrapper('POST', quota_catalog_url, undefined, data)
        },
        update: function (id, data) {
            return wrapper('POST', quota_catalog_url +'/' + id, undefined, data)
        }
    }
})
.controller('HTMCConfigCtrl', function ($scope, HTMCConfigService) {
    $scope.level = 0;
    $scope.catalog_list = [];
    $scope.load_catalog_list = function () {
        HTMCConfigService.catalog.get_list().then(function (result) {
            $scope.catalog_list = result;
        });
    };
    $scope.switch_to_catalog = function (id) {
        $scope.level = 1;
    };
    $scope.clone_catalog = function (id) {};
    $scope.delete_catalog = function (id) {};
    $scope.new_catalog = function () {};
    $scope.load_catalog_list();
})
;