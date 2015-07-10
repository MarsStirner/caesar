'use strict';

WebMis20
.factory('Person', ['BasicModel', 'PersonCuration', function (BasicModel, PersonCuration) {
    var Person = function (data) {
        BasicModel.call(this, data);
    };
    Person.inheritsFrom(BasicModel);
    Person.initialize({
        fields: ['id', 'last_name', 'first_name', 'patr_name', 'name_text', 'post', 'speciality',
            'organisation', 'org_structure', {
                name: 'person_curations',
                optional: true,
                klass: PersonCuration
            }
        ],
        base_url: '/misconfig/api/v1/person/'
    }, Person);
    Person.prototype.getNewPersonCuration = function () {
        return PersonCuration.instantiate();
    };
    Person.prototype.addPersonCuration = function (person_curation) {
        this.person_curations.push(person_curation);
    };
    return Person;
}])
.factory('PersonCuration', ['BasicModel', function (BasicModel) {
    var PersonCuration = function (data) {
        BasicModel.call(this, data);
    };
    PersonCuration.inheritsFrom(BasicModel);
    PersonCuration.initialize({
        fields: ['id', 'person_id', 'org_curation_level_id', 'org_curation_level', 'person'],
        base_url: '/misconfig/api/v1/person_curation_level/'
    }, PersonCuration);
    return PersonCuration;
}])
;