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
.controller('HTMCConfigCtrl', function ($scope, $modal, HTMCConfigService) {
    $scope.models = {
        level: 0,
        catalog_list: []
    };
    $scope.catalog = {
        list: function () {
            HTMCConfigService.catalog.get_list().then(function (result) {
                $scope.models.catalog_list = result;
            })
        },
        switch_to: function (catalog) {
            $scope.models.level = 1;
        },
        clone: function (catalog) {},
        delete: function (catalog) {},
        edit: function (catalog) {},
        create: function () {
            var instance = $modal.open({
                controller: CatalogEditModalCtrl,
                size: 'lg',
                templateUrl: '/caesar/misconfig/htmc/catalog-edit-modal.html',
                resolve: {
                    model: function () {return {}}
                }
            });
            instance.result.then(function (model) {
                HTMCConfigService.catalog.create(model).then(function (result) {
                    $scope.models.catalog_list.push(result);
                });
            })
        }
    };
    $scope.catalog.list();
    var CatalogEditModalCtrl = function ($scope, $modalInstance, model) {
        $scope.model = model;
    }
})
;