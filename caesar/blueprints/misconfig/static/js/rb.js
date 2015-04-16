'use strict';

WebMis20
.service('RbList', ['ApiCalls', function (ApiCalls) {
    var self = this;
    ApiCalls.wrapper('GET', '/misconfig/api/v1/rb/list/')
    .then(function (data) {
        self.items = data.supported_rbs;
    })
}])
.factory('BasicModel', [function () {
    var BasicModelConstructor = function (fields, data) {
        this._fields = fields;
        if (fields) this.fill(data);
    };
    BasicModelConstructor.prototype = {
        fill: function (data) {
            var self = this;
            if (_.isObject(data)) {
                this._fields.forEach(function (field) { self[field] = data[field] });
            } else {
                this._fields.forEach(function (field) { self[field] = null });
            }
            return this;
        },
        save: function () { },
        del: function () { },
        clone: function (what, where) {
            return angular.copy(what || this, where || {});
        }
    };
    return BasicModelConstructor;
}])
.factory('RbBasic', ['ApiCalls', 'BasicModel', function (ApiCalls, BasicModel) {
    var fields = ['id', 'code', 'name', 'deleted'];
    var RbBasic = function (name, data) {
        BasicModel.call(this, fields, data);
        this.rb_name = name;
    };
    RbBasic.prototype = new BasicModel();
    RbBasic.prototype.constructor = RbBasic;
    RbBasic.getByName = function (name) {
        return ApiCalls.wrapper('GET', '/misconfig/api/v1/rb/{0}/'.format(name))
            .then(function (data) {
                return data.items.map(function (item) {
                    return new RbBasic(name, item);
                });
            });
    };
    RbBasic.prototype.save = function () {
        var self = this,
            data = _.pick(self, fields),
            url = '/misconfig/api/v1/rb/{0}/{1|/}'.formatNonEmpty(this.rb_name, this.id || undefined);
        return ApiCalls.wrapper('POST', url, undefined, data)
            .then(function (result) {
                return self.fill(result);
            });
    };
    RbBasic.prototype.del = function () {
        var url = '/misconfig/api/v1/rb/{0}/{1}/'.format(this.rb_name, this.id);
        return ApiCalls.wrapper('DELETE', url);
    };
    RbBasic.prototype.clone = function () {
        return BasicModel.prototype.clone(this, new RbBasic(this.rb_name));
    };
    return RbBasic;
}])
.controller('RBConfigCtrl', ['$scope', '$modal', 'RbList', 'RbBasic', 'MessageBox',
        function ($scope, $modal, RbList, RbBasic, MessageBox) {
    $scope.RbList = RbList;
    $scope.model = {
        selected_rb: null,
        rb_list: []
    };
    $scope.select_rb = function (rb_item) {
        $scope.model.selected_rb = rb_item;
        RbBasic.getByName(rb_item.name).then(function (items) {
            $scope.model.rb_list = items;
        });
    };
    $scope.isSelected = function (name) {
        return $scope.model.selected_rb && $scope.model.selected_rb.name === name;
    };
    $scope.gotoIndex = function () {
        $scope.model.selected_rb = null;
        $scope.model.rb_list = [];
    };

    var get_edit_modal = function (get_model_callback) {
        return $modal.open({
            controller: function ($scope, $modalInstance, model) { $scope.model = model; },
            size: 'lg',
            templateUrl: "/caesar/misconfig/htmc/rb-edit-modal.html",
            resolve: { model: get_model_callback }
        });
    };
    $scope.create_new = function (name) {
        var item = new RbBasic(name);
        get_edit_modal(function () {
            return item;
        }).result.then(function () {
            item.save().then(function (result) {
                $scope.model.rb_list.push(result);
            });
        });
    };
    $scope.edit = function (index) {
        var item = $scope.model.rb_list[index].clone();
        get_edit_modal(function () {
            return item;
        }).result.then(function () {
            item.save().then(function (result) {
                $scope.model.rb_list.splice(index, 1, result)
            });
        });
    };
    $scope.remove = function (index) {
        var item = $scope.model.rb_list[index];
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
}])
;