/**
 * Created by mmalkov on 19.03.15.
 */
'use strict';

WebMis20
.filter('pluck', function () {
    return function (array, attribute) {
        return _.pluck(array, attribute)
    }
})
.filter('default', function () {
    return function (value, d) {
        return value || d
    }
})
.factory('QuotaClass', function (ApiCalls, $log, $q) {
    var wrapper = ApiCalls.wrapper;
    return function (url, fields, master_field, slave_class) {
        var QuotaClass = function (data) {
            this.fill(data);
        };
        QuotaClass.all = function (id) {
            var final_url;
            if (master_field) {
                final_url = url + '/' + id;
            } else {
                final_url = url;
            }
            $log.info('Loading all using "GET {0}"'.format(final_url));
            return ApiCalls.wrapper('GET', final_url)
                .then(function (result) {
                    return result.map(function (item) {
                        return new QuotaClass(item);
                    })
                })
        };
        QuotaClass.prototype.fill = function (data) {
            var self = this;
            if (_.isObject(data)) {
                fields.forEach(function (field) { self[field] = data[field] });
                if (!!slave_class) { self.children = data.children || [] }
            } else {
                fields.forEach(function (field) { self[field] = null });
                if (!!slave_class) { self.children = [] }
            }
            return this;
        };
        if (!!slave_class) {
            QuotaClass.prototype.load_slaves = function () {
                var self = this;
                slave_class.all(this.id).then(function (result) {
                    self.children = result;
                    return result;
                })
            }
        }
        if (!!master_field) {
            QuotaClass.prototype.set_master_id = function (master_id) {
                this[master_field] = master_id;
            }
        } else {
            QuotaClass.prototype.set_master_id = function () {}
        }
        QuotaClass.prototype.save = function () {
            var self = this,
                object = _.pick(self, fields),
                full_url = url;
            if (master_field) { full_url = full_url + '/' + self[master_field] }
            if (self.id) { full_url = full_url + '/' + self.id }
            $log.info('Using "POST {0}" to save data'.format(full_url));
            return wrapper('POST', full_url, undefined, object).then(function (result) {
                return self.fill(result);
            })
        };
        QuotaClass.prototype.clone = function () {
            var self = this,
                object = _.pick(self, fields),
                full_url = url;
            if (master_field) { full_url = full_url + '/' + self[master_field] }
            full_url = full_url + '/' + self.id + '/clone';
            $log.info('Using "POST {0}" to save data'.format(full_url));
            return wrapper('POST', full_url, undefined, {}).then(function (result) {
                return new QuotaClass(result);
            })
        };
        QuotaClass.prototype.delete = function () {
            var self = this,
                full_url = url;
            if (master_field) {
                full_url = full_url + '/' + self[master_field]
            }
            if (self.id) {
                full_url = full_url + '/' + self.id
            } else {
                return $q.reject(null)
            }
            $log.info('Using "DELETE {0}" to delete object'.format(full_url));
            return wrapper('DELETE', full_url)
        };
        return QuotaClass;
    }
})
.factory('QuotaDetails', function (QuotaClass) {
    var quota_detail_url = '/misconfig/api/v1/quota_detail';
    return QuotaClass(
        quota_detail_url,
        ['id','quota_type_id','patient_model','treatment', 'mkb'],
        'quota_type_id'
    )
})
.factory('QuotaType', function (QuotaClass, QuotaDetails) {
    var quota_type_url = '/misconfig/api/v1/quota_type';
    return QuotaClass(
        quota_type_url,
        ['id', 'profile_id', 'group_code', 'code', 'name', 'price'],
        'profile_id',
        QuotaDetails
    )
})
.factory('QuotaProfile', function (QuotaClass, QuotaType) {
    var quota_profile_url = '/misconfig/api/v1/quota_profile';
    return QuotaClass(
        quota_profile_url,
        ['id', 'catalog_id', 'code', 'name'],
        'catalog_id',
        QuotaType
    )
})
.factory('QuotaCatalog', function (QuotaClass, QuotaProfile) {
    var quota_catalog_url = '/misconfig/api/v1/quota_catalog';
    return QuotaClass(
        quota_catalog_url,
        ['id', 'finance', 'beg_date', 'end_date', 'catalog_number', 'document_number', 'document_date', 'document_corresp', 'comment'],
        null,
        QuotaProfile
    )
})
.controller('HTMCConfigCtrl', function ($scope, $modal, QuotaCatalog, QuotaProfile, QuotaType, QuotaDetails, MessageBox) {
    $scope.models = {
        level: 0,
        catalog_list: [],
        catalog_selected: null,
        profile_list: [],
        profile_selected: null,
        types_list: [],
        types_selected: null,
        details_list: []
    };
    var UI = function (klass, template_url, base_name, level, child_ui) {
        var get_edit_modal = function (get_model_callback) {
            return $modal.open({
                controller: function ($scope, $modalInstance, model) { $scope.model = model; },
                size: 'lg',
                templateUrl: template_url,
                resolve: { model: get_model_callback }
            })
        };
        var self = this,
            base_list = '{0}_list'.format(base_name),
            base_selected = '{0}_selected'.format(base_name),
            current_master_id;
        self.level = level;
        if (!_.isUndefined(child_ui)) {
            this.switch_to = function (index) {
                var object = $scope.models[base_list][index];
                $scope.models[base_selected] = object;
                child_ui.list(object.id).then(function (result) {
                    $scope.models.level = child_ui.level;
                })
            }
        }
        this.list = function (master_id) {
            current_master_id = master_id;
            return klass.all(master_id).then(function (result) {
                $scope.models[base_list] = result;
                return result;
            })
        };
        this.create = function () {
            get_edit_modal(function () {
                var obj = new klass();
                obj.set_master_id(current_master_id);
                return obj;
            }).result.then(function (model) {
                model.save().then(function (result) {
                    $scope.models[base_list].push(result);
                });
            })
        };
        this.edit = function (index) {
            get_edit_modal(function () {
                var obj = new klass($scope.models[base_list][index]);
                obj.set_master_id(current_master_id);
                return obj;
            }).result.then(function (model) {
                model.save().then(function (result) {
                    $scope.models[base_list].splice(index, 1, result);
                });
            })
        };
        this.clone = function (index) {
            MessageBox.question('Копирование', 'Действительно копировать?').then(function (result) {
                if (result) {
                    $scope.models[base_list][index].clone().then(function (result) {
                        $scope.models[base_list].push(result);
                    })
                }
            })
        };
        this.delete = function (index) {
            var obj = $scope.models[base_list][index];
            MessageBox.question('Удаление', 'Действительно удалить?').then(function (result) {
                if (result) {
                    obj.set_master_id(current_master_id);
                    obj.delete().then(function () {
                        self.list(current_master_id);
                    })
                }
            })
        }
    };
    $scope.details = new UI(QuotaDetails, '/caesar/misconfig/htmc/details-edit-modal.html', 'details', 3);
    $scope.types   = new UI(QuotaType,    '/caesar/misconfig/htmc/type-edit-modal.html',    'types',   2, $scope.details);
    $scope.profile = new UI(QuotaProfile, '/caesar/misconfig/htmc/profile-edit-modal.html', 'profile', 1, $scope.types);
    $scope.catalog = new UI(QuotaCatalog, '/caesar/misconfig/htmc/catalog-edit-modal.html', 'catalog', 0, $scope.profile);

    $scope.catalog.list();
})
;