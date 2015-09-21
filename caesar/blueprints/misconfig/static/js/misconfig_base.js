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
                this._fields.forEach(function (field) {
                    if (field.optional && !data.hasOwnProperty(field.name)) {
                        return;
                    }
                    if (_.isObject(field)) {
                        // TODO: переделать под instantiate_all
                        if (_.isArray(data[field.name])) {
                            self[field.name] = data[field.name].map(function (d) {
                                return new field.klass(d);
                            });
                        } else {
                            self[field.name] = new field.klass(data[field.name]);
                        }
                    } else {
                        self[field] = data[field];
                    }
                });
            } else {
                this._fields.forEach(function (field) { self[field] = null; });
            }
            return this;
        },
        save: function (url, data, args) {
            var self = this;
            var data = data || this._pickData(),
                url = url || '{0}{|1|/}'.formatNonEmpty(this._base_url, self.id || undefined);
            return ApiCalls.wrapper('POST', url, args, data)
                .then(function (result) {
                    return self.fill(result);
                });
        },
        del: function (url) {
            var self = this,
                url = url || '{0}{|1|/}'.formatNonEmpty(this._base_url, self.id);
            return ApiCalls.wrapper('DELETE', url)
                .then(function (result) {
                    return self.fill(result);
                });
        },
        undel: function (url) {
            var self = this,
                url = url || '{0}{|1|/undelete/}'.formatNonEmpty(this._base_url, self.id);
            return ApiCalls.wrapper('POST', url)
                .then(function (result) {
                    return self.fill(result);
                });
        },
        clone: function () {
            return new this.constructor(this._pickData());
        },
        _pickData: function () {
            var self = this,
                field_list = this._fields.map(function (f) {
                    return _.isObject(f) ? f.name : f;
                });
            return _.pick(self, function (value, key) {
                return field_list.has(key);
            });
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
        if (params.list_url) {
            obj.prototype._list_url = params.list_url;
            obj.getListUrl = function () {
                return obj.prototype._list_url;
            };
        } else if (params.base_url) {
            obj.getListUrl = function () {
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
    BasicModelConstructor.initialize({base_url: '', fields: []}, BasicModelConstructor);
    BasicModelConstructor.instantiate = function (item_id, args, url) {
        var klass = this;
        if (!url) {
            url = klass.getBaseUrl();
            if (item_id !== undefined) url = '{0}{1}/'.formatNonEmpty(url, item_id);
        }
        return ApiCalls.wrapper('GET', url, args)
            .then(function (data) {
                return new klass(data.item);
            });
    };
    BasicModelConstructor.instantiateAll = function (args) {
        var klass = this;
        var url = klass.getListUrl();
        return ApiCalls.wrapper('GET', url, args)
            .then(function (data) {
                return data.items.map(function (item) {
                    return new klass(item);
                });
            });
    };
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
    return SimpleRb;
}])
.controller('MisConfigBaseCtrl', ['$scope', '$modal', 'MessageBox',
        function ($scope, $modal, MessageBox) {
    var _simpleModalConfig = {
        controller: 'SimpleConfigModalCtrl',
        size: 'lg',
        backdrop: 'static',
        templateUrl: null,
        resolve: {}
    };
    $scope.setSimpleModalConfig = function (config) {
        _.extend(_simpleModalConfig, config);
    };
    var getSimpleEditModal = function (model) {
        _simpleModalConfig.resolve.model = function () {
            return model;
        };
        return $scope.getEditModal(_simpleModalConfig);
    };
    $scope.getEditModal = function (config) {
        return $modal.open(config);
    };

    var url_params = aux.getQueryParams();
    $scope.getUrlParam = function (name) {
        return url_params[name];
    };

    $scope.EntityClass = null;
    $scope.item_list = [];
    $scope.create_new = function () {
        $scope.EntityClass.instantiate(undefined, {'new': true}).
            then(function (item) {
                $scope._editNew(item);
            });
    };
    $scope._editNew = function (item) {
        getSimpleEditModal(item).result.then(function (item) {
            $scope.item_list.push(item);
        });
    };
    $scope.edit = function (index) {
        var item = $scope.item_list[index].clone();
        getSimpleEditModal(item).result.then(function (item) {
            $scope.item_list.splice(index, 1, item)
        });
    };
    $scope._remove = function (item) {
        MessageBox.question('Удаление записи', 'Действительно удалить?').then(function (result) {
            if (result) {
                item.del();
            }
        });
    };
    $scope.remove = function (index) {
        var item = $scope.item_list[index];
        $scope._remove(item);
    };
    $scope._restore = function (item) {
        item.undel();
    };
    $scope.restore = function (index) {
        var item = $scope.item_list[index];
        $scope._restore(item);
    };
    $scope.canEdit = function (item) {
        return !item.deleted;
    };
    $scope.canDelete = function (item) {
        return item.deleted !== undefined && !item.deleted;
    };
    $scope.canUndelete = function (item) {
        return item.deleted !== undefined && item.deleted;
    };
}])
.controller('SimpleConfigModalCtrl', ['$scope', '$modalInstance', 'model',
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