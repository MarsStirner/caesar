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
                url = url || '{0}{|1|/}'.formatNonEmpty(self.constructor.getBaseUrl(data), self.id || undefined);
            return ApiCalls.wrapper('POST', url, args, data)
                .then(function (result) {
                    return self.fill(result);
                });
        },
        del: function (url) {
            var self = this,
                data = this._pickData(),
                url = url || '{0}{|1|/}'.formatNonEmpty(self.constructor.getBaseUrl(data), self.id);
            return ApiCalls.wrapper('DELETE', url)
                .then(function (result) {
                    return self.fill(result);
                });
        },
        undel: function (url) {
            var self = this,
                data = this._pickData(),
                url = url || '{0}{|1|/undelete/}'.formatNonEmpty(self.constructor.getBaseUrl(data), self.id);
            return ApiCalls.wrapper('POST', url)
                .then(function (result) {
                    return self.fill(result);
                });
        },
        clone: function () {
            return new this.constructor(this._pickData());
        },
        _pickData: function () {
            var copy = _.deepCopy(this),
                field_list = this._fields.map(function (f) {
                    return _.isObject(f) ? f.name : f;
                });
            return _.pick(copy, field_list);
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
            url = klass.getBaseUrl(args);
            if (item_id !== undefined) url = '{0}{1}/'.formatNonEmpty(url, item_id);
        }
        return ApiCalls.wrapper('GET', url, args)
            .then(function (data) {
                return new klass(data.item);
            });
    };
    BasicModelConstructor.instantiateAll = function (args) {
        var klass = this;
        var url = klass.getListUrl(args);
        var paginate = args === undefined ? false : Boolean(args.paginate);
        return ApiCalls.wrapper('GET', url, args)
            .then(function (data) {
                if (paginate) {
                    data.items = data.items.map(function (item) {
                        return new klass(item);
                    });
                } else {
                    data = data.items.map(function (item) {
                        return new klass(item);
                    });
                }
                return data;
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
    /* API контроллера для редактирования списка записей:
     - setViewParams - установка параметров поведения формы (страничный режим, наличие фильтра и пр.)
     - setSimpleModalConfig - установка параметров модального диалога редактирования записи
     - getEditModal - получить объект нового открытого модального диалога
     - getUrlParam - получить значение аргумента из url
     - _refreshData - обновить список записей
     - create_new - получение новой модели записи с вызовом _editNew()
     - _editNew - открытие диалога редактирования записи с последующим обновлением списка записей
     - edit - редактирование записи с поледующим обновлением списка
     - remove - получение записи по индексу и вызов _remove()
     - _remove - процесс удаления записи
     - restore - получение записи по индексу и вызов _restore()
     - _remove - процесс отмены удаления записи
     - canEdit - можно ли редактировать
     - canDelete - можно ли удалить
     - canUndelete - можно ли отменить удаление

     */
    var viewParams = {
        paginate: false,
        filter: false
    };
    $scope.setViewParams = function (new_params) {
        angular.extend(viewParams, new_params);
    };
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
    $scope.pager = {
        current_page: 1,
        per_page: 15,
        max_pages: 15,
        pages: null,
        record_count: null
    };
    $scope.flt = {
        enabled: false,
        model: {}
    };
    $scope._refreshData = function (args) {
        return $scope.EntityClass.instantiateAll(args);
    };
    $scope.create_new = function () {
        $scope.EntityClass.instantiate(undefined, {'new': true}).
            then(function (item) {
                $scope._editNew(item);
            });
    };
    $scope._editNew = function (item) {
        getSimpleEditModal(item).result.then(function (item) {
            if (viewParams.paginate) {
                $scope.refreshData();
            } else {
                $scope.item_list.push(item);
            }
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
    $scope.toggleFilter = function () {
        $scope.flt.enabled = !$scope.flt.enabled;
    };
    $scope.isFilterEnabled = function () {
        return $scope.flt.enabled;
    };
    $scope.clear = function () {
        $scope.flt.model = {};
    };
    $scope.clearAll = function () {
        $scope.clear();
        $scope.pager.current_page = 1;
        $scope.pager.pages = null;
        $scope.pager.record_count = null;
        $scope.item_list = [];
    };
    $scope.getData = function () {
        $scope.pager.current_page = 1;
        $scope.refreshData();
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