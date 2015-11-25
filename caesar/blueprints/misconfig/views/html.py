# -*- coding: utf-8 -*-
from flask import render_template, abort
from ..app import module
from nemesis.systemwide import db
from nemesis.models.person import Person
from nemesis.models.exists import PriceList

__author__ = 'viruzzz-kun'


@module.route('/')
def index_html():
    return render_template('misconfig/index.html')


@module.route('/htmc/')
def htmc_html():
    return render_template('misconfig/htmc.html')


@module.route('/rb/')
def rb_html():
    return render_template('misconfig/rb.html')


@module.route('/org/')
def org_html():
    return render_template('misconfig/org/org.html')


@module.route('/print-template/')
def print_template_html():
    return render_template('misconfig/print_template/print-template-list.html')


@module.route('/expert/protocol/')
@module.route('/expert/protocol/index/')
def expert_protocol_index_html():
    return render_template('misconfig/expert/protocol/index.html')


@module.route('/expert/protocol/measures/')
def expert_protocol_measures_html():
    return render_template('misconfig/expert/protocol/measure-list.html')


@module.route('/expert/protocol/protocols/')
def expert_protocol_protocols_html():
    return render_template('misconfig/expert/protocol/protocol-list.html')


@module.route('/expert/protocol/protocols/protocol/')
def expert_protocol_protocol_html():
    return render_template('misconfig/expert/protocol/protocol-edit.html')


@module.route('/expert/protocol/protocols/scheme-measures/')
def expert_protocol_scheme_measures_html():
    return render_template('misconfig/expert/protocol/scheme-measure-edit.html')


@module.route('/org/org-birth-care-level/')
def org_birth_care_level_html():
    return render_template('misconfig/org/org-birth-care-level.html')


@module.route('/org/org-birth-care-level/orgs/')
def org_obcl_html():
    return render_template('misconfig/org/org-birth-care-level-orgs.html')


@module.route('/person-curation-level/')
def person_curation_level_html():
    return render_template('misconfig/person/person-curation-level.html')


@module.route('/org/org-curation/')
def org_curation_html():
    return render_template('misconfig/org/org-curation.html')


@module.route('/perinatal-risk-rate-mkb/')
def perinatal_risk_rate_mkb_html():
    return render_template('misconfig/perinatal-risk-rate-mkb.html')


@module.route('/pregnancy-pathology-mkb/')
def pregnancy_pathology_mkb_html():
    return render_template('misconfig/pregnancy_pathology_mkb.html')


@module.route('/person/')
def person_html():
    return render_template('misconfig/person/person-list.html')


@module.route('/price_list/')
@module.route('/price_list/<int:_id>/')
def price_list(_id=None):
    if _id is not None:
        price = db.session.query(PriceList).get(_id)
        if not price:
            abort(404)
        return render_template('misconfig/price/tariff.html', price=price)
    return render_template('misconfig/price/list.html')
