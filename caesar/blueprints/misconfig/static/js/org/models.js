'use strict';

WebMis20
.factory('Organisation', ['SimpleRb', function (SimpleRb) {
    var Organisation = function (data) {
        SimpleRb.call(this, data);
    };
    Organisation.inheritsFrom(SimpleRb);
    Organisation.initialize({
        fields: ['id', 'short_name', 'full_name', 'title', 'infis', 'is_insurer',
            'is_hospital', 'address', 'phone', 'kladr_locality', 'deleted'],
        base_url: '{0}Organisation/'.format(Organisation.getBaseUrl())
    }, Organisation);
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
        }],
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
;