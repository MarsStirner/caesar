'use strict';

WebMis20
.factory('Organisation', ['BasicModel', 'OrganisationCuration', function (BasicModel, OrganisationCuration) {
    var Organisation = function (data) {
        BasicModel.call(this, data);
    };
    Organisation.inheritsFrom(BasicModel);
    Organisation.initialize({
        fields: ['id', 'short_name', 'full_name', 'title', 'infis', 'is_insurer',
            'is_hospital', 'address', 'phone', 'kladr_locality', 'deleted', {
                name: 'org_curations',
                optional: true,
                klass: OrganisationCuration
            }],
        base_url: '/misconfig/api/v1/org/'
    }, Organisation);
    Organisation.prototype.getNewOrgCuration = function () {
        var url = OrganisationCuration.getBaseUrl().format(this.id) + 'new/';
        return OrganisationCuration.instantiate(undefined, undefined, url);
    };
    Organisation.prototype.addOrgCuration = function (org_curation) {
        this.org_curations.push(org_curation);
    };
    return Organisation;
}])
.factory('OrganisationBirthCareLevel', ['BasicModel', 'OrganisationOBCL', function (BasicModel, OrganisationOBCL) {
    var OrganisationBirthCareLevel = function (data) {
        BasicModel.call(this, data);
    };
    OrganisationBirthCareLevel.inheritsFrom(BasicModel);
    OrganisationBirthCareLevel.initialize({
        fields: ['id', 'code', 'name', 'description', 'deleted', 'idx', 'perinatal_risk_rate', {
            name: 'org_obcls',
            optional: true,
            klass: OrganisationOBCL
        }, 'color'],
        base_url: '/misconfig/api/v1/org_birth_care_level/'
    }, OrganisationBirthCareLevel);
    OrganisationBirthCareLevel.prototype.getNewOrgOBCL = function (org_id) {
        var url = OrganisationOBCL.getBaseUrl().format(this.id) + 'new/';
        return OrganisationOBCL.instantiate(undefined, undefined, url, {
            org_id: org_id
        });
    };
    OrganisationBirthCareLevel.prototype.addOrgOBCL = function (org_obcl) {
        this.org_obcls.push(org_obcl);
    };
    return OrganisationBirthCareLevel;
}])
.factory('OrganisationOBCL', ['BasicModel', function (BasicModel) {
    var OrganisationOBCL = function (data) {
        BasicModel.call(this, data);
    };
    OrganisationOBCL.inheritsFrom(BasicModel);
    OrganisationOBCL.initialize({
        fields: ['id', 'obcl_id', 'org_id', 'organisation'],
        base_url: '/misconfig/api/v1/org_birth_care_level/{0}/orgs/'
    }, OrganisationOBCL);
    return OrganisationOBCL;
}])
.factory('OrganisationCuration', ['BasicModel', function (BasicModel) {
    var OrganisationCuration = function (data) {
        BasicModel.call(this, data);
    };
    OrganisationCuration.inheritsFrom(BasicModel);
    OrganisationCuration.initialize({
        fields: ['id', 'org_id', 'person_curation_id', 'person_curation'],
        base_url: '/misconfig/api/v1/org/{0}/curation/'
    }, OrganisationCuration);
    return OrganisationCuration;
}])
;