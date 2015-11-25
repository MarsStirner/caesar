'use strict';

WebMis20
.factory('Person', ['WMConfig', 'BasicModel', 'PersonCuration', function (WMConfig, BasicModel) {
    var Person = function (data) {
        BasicModel.call(this, data);
    };
    Person.inheritsFrom(BasicModel);
    Person.initialize({
        fields: ['id', 'last_name', 'first_name', 'patr_name', 'name_text', 'post', 'speciality',
            'organisation', 'org_structure', 'curation_levels'
        ],
        base_url:  WMConfig.url.misconfig.api_person_base,
        list_url: WMConfig.url.misconfig.api_person_list_base
    }, Person);
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
;