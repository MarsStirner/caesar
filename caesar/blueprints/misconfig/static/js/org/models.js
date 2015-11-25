'use strict';

WebMis20
.factory('Organisation', ['WMConfig', 'BasicModel', function (WMConfig, BasicModel) {
    var Organisation = function (data) {
        BasicModel.call(this, data);
    };
    Organisation.inheritsFrom(BasicModel);
    Organisation.initialize({
        fields: ['id', 'short_name', 'full_name', 'title', 'infis', 'is_insurer', 'is_hospital', 'is_lpu',
            'is_stationary', 'address', 'phone', 'kladr_locality', 'deleted', 'org_curators'],
        base_url: WMConfig.url.misconfig.api_org_base,
        list_url: WMConfig.url.misconfig.api_org_list_base
    }, Organisation);
    return Organisation;
}])
.factory('OrganisationBirthCareLevel', ['WMConfig', 'BasicModel', function (WMConfig, BasicModel) {
    var OrganisationBirthCareLevel = function (data) {
        BasicModel.call(this, data);
    };
    OrganisationBirthCareLevel.inheritsFrom(BasicModel);
    OrganisationBirthCareLevel.initialize({
        fields: ['id', 'code', 'name', 'description', 'deleted', 'idx', 'perinatal_risk_rate', 'orgs', 'color'],
        base_url:  WMConfig.url.misconfig.api_org_birth_care_level_base,
        list_url:  WMConfig.url.misconfig.api_org_birth_care_level_list_base
    }, OrganisationBirthCareLevel);
    return OrganisationBirthCareLevel;
}])
;