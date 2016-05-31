'use strict';
WebMis20
.factory('Person', ['WMConfig', 'BasicModel', 'PersonContact',
        function (WMConfig, BasicModel, PersonContact) {
    var Person = function (data) {
        var self = this;
        BasicModel.call(this, data);
        this.phones = [];
        this.skypes = [];
        this.emails = [];
        _.map(this.contacts, function(contact){
                var contCode = contact.contact_type.code;
                if (contCode == '01' || contCode == '02'|| contCode == '03' || contCode == '13'){
                    self.phones.push(contact);
                } else if (contCode == '12') {
                    self.skypes.push(contact);
                } else if (contCode == '04') {
                    self.emails.push(contact);
                }
        });
    };
    Person.inheritsFrom(BasicModel);
    Person.initialize({
        fields: ['id', 'last_name', 'first_name', 'patr_name', 'name_text', 'post', 'speciality',
            'organisation', 'org_structure', 'deleted', 'inn', 'snils', 'birth_date', 'sex',
            'user_profiles', 'login', 'new_password', 'contacts',
            'curation_levels'
        ],
        base_url:  WMConfig.url.misconfig.api_person_base,
        list_url: WMConfig.url.misconfig.api_person_list_base
    }, Person);

    Person.prototype.save = function(url, data, args) {
        var allContacts = [].concat(this.phones, this.skypes, this.emails);
        allContacts = _.reject(allContacts, function(item){ return item.value === null; });
        this.contacts = allContacts;

        return BasicModel.prototype.save.call(this, url, data, args);
    };
    Person.prototype.addNewContact = function (ct, group) {
        var self = this;
        PersonContact.instantiate(undefined, {
            new: true
        }).then(function (new_contact) {
            new_contact.contact_type = ct;
            self[group].push(new_contact);
        });
    };

    return Person;
}])
.factory('PersonCuration', ['WMConfig', 'BasicModel', function (WMConfig, BasicModel) {
    var PersonCuration = function (data) {
        BasicModel.call(this, data);
    };
    PersonCuration.inheritsFrom(BasicModel);
    PersonCuration.initialize({
        fields: ['id', 'person_id', 'org_curation_level_id', 'org_curation_level', 'person'],
        list_url: WMConfig.url.misconfig.api_person_curation_level_list_get
    }, PersonCuration);
    return PersonCuration;
}])
.factory('PersonContact', ['WMConfig', 'BasicModel', function (WMConfig, BasicModel) {
    var PersonContact = function (data) {
        BasicModel.call(this, data);
    };
    PersonContact.inheritsFrom(BasicModel);
    PersonContact.initialize({
        fields: ['id', 'person_id', 'contact_type_id', 'contact_type', 'value'],
        base_url: WMConfig.url.misconfig.api_person_contact_base
    }, PersonContact);
    return PersonContact;
}]);