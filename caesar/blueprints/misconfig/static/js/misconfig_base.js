'use strict';

WebMis20
.factory('BasicModel', ['ApiCalls', function (ApiCalls) {
    var BasicModelConstructor = function (data) {
        if (this._fields) this.fill(data);
    };
    BasicModelConstructor.prototype = {
        fill: function (data) {
            var self = this;
            if (_.isObject(data)) {
                this._fields.forEach(function (field) { self[field] = data[field]; });
            } else {
                this._fields.forEach(function (field) { self[field] = null; });
            }
            return this;
        },
        save: function (url, data) {
            var self = this;
            var data = data || _.pick(self, this._fields),
                url = url || '{0}{|1|/}'.formatNonEmpty(this._base_url, self.id || undefined);
            return ApiCalls.wrapper('POST', url, undefined, data)
                .then(function (result) {
                    return self.fill(result);
                });
        },
        del: function (url) {
            return ApiCalls.wrapper('DELETE', url);
        },
        clone: function () {
            var what = this,
                where = new this.constructor();
            return angular.copy(what, where);
        }
    };
    // static methods
    BasicModelConstructor.initialize = function (params, obj) {
        if (params.base_url) {
            obj.prototype._base_url = params.base_url;
            obj.getBaseUrl = function () {
                return obj.prototype._base_url;
            };
        }
        if (params.fields) {
            obj.prototype._fields = params.fields;
            obj.getFields = function () {
                return obj.prototype._fields;
            };
        }
    };
    BasicModelConstructor.initialize({base_url:'', fields:[]}, BasicModelConstructor);
    return BasicModelConstructor;
}])
.factory('SimpleRb', ['BasicModel', function (BasicModel) {
    var _fields = ['id', 'code', 'name', 'deleted'],
        _base_url = '/misconfig/api/v1/rb/';
    var SimpleRb = function (data) {
        BasicModel.call(this, data);
    };
    SimpleRb.inheritsFrom(BasicModel);
    SimpleRb.initialize({
        base_url: _base_url,
        fields: _fields
    }, SimpleRb);
    //SimpleRb.prototype.save = function () {
    //    var data = _.pick(this, this._fields),
    //        url = '/misconfig/api/v1/rb/{0}/{1|/}'.formatNonEmpty(this.rb_name, this.id || undefined);
    //    return BasicModel.prototype.save.call(this, url, data);
    //};
    //SimpleRb.prototype.del = function () {
    //    var url = '/misconfig/api/v1/rb/{0}/{1}/'.format(this.rb_name, this.id);
    //    return BasicModel.prototype.del.call(this, url);
    //};
    return SimpleRb;
}])
.service('RbService', ['$injector', 'ApiCalls', function ($injector, ApiCalls) {
    this.getItemList = function (name) {
        var klass = $injector.get(name);
        var url = klass.getBaseUrl();
        return ApiCalls.wrapper('GET', url) // '/misconfig/api/v1/rb/{0}/'.format(name)
            .then(function (data) {
                return data.items.map(function (item) {
                    return new klass(item);
                });
            });
    };
    this.getClass = function (name) {
        return $injector.get(name);
    };
}])
.controller('MisConfigBaseCtrl', ['$scope', '$modal', 'MessageBox',
        function ($scope, $modal, MessageBox) {
    var _modalParams = {
        controller: function ($scope, $modalInstance, model) {
            $scope.model = model;
        },
        size: 'lg',
        templateUrl: null,
        resolve: {}
    };
    $scope.setModalParams = function (params) {
        _.extend(_modalParams, params);
    };
    var get_edit_modal = function (get_model_callback) {
        _modalParams.resolve.model = get_model_callback;
        return $modal.open(_modalParams);
    };
    var url_params = aux.getQueryParams();

    //$scope.modalTemplate = '';
    $scope.EntityClass = null;
    $scope.item_list = [];

    $scope.create_new = function () {
        var item = new $scope.EntityClass();
        get_edit_modal(function () {
            return item;
        }).result.then(function () {
            item.save().then(function (result) {
                $scope.item_list.push(result);
            });
        });
    };
    $scope.edit = function (index) {
        var item = $scope.item_list[index].clone();
        get_edit_modal(function () {
            return item;
        }).result.then(function () {
            item.save().then(function (result) {
                $scope.item_list.splice(index, 1, result)
            });
        });
    };
    $scope.remove = function (index) {
        var item = $scope.item_list[index];
        MessageBox.question('Удаление записи', 'Действительно удалить?').then(function (result) {
            if (result) {
                item.del().then(function (result) {
                    if (item.hasOwnProperty('deleted')) {
                        $scope.model.rb_list.splice(index, 1, result)
                    } else {
                        $scope.model.rb_list.splice(index, 1);
                    }
                });
            }
        })
    };

    $scope.getUrlParam = function (name) {
        return url_params[name];
    }
}])
;