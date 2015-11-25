# -*- coding: utf-8 -*-

import os
import config

from flask import url_for

from nemesis.app import app, bootstrap_app
from nemesis.lib.frontend import frontend_config
from version import version as app_version

__author__ = 'viruzzz-kun'

app.config.from_object(config)
bootstrap_app(os.path.join(os.path.dirname(__file__), 'templates'))


@app.context_processor
def general_menu():
    from nemesis.lib.user import UserProfileManager
    menu_items = [dict(
        link='index',
        title=u'Главная страница',
        homepage=True,
        visible=(not UserProfileManager.has_ui_registrator_cut())
    ), dict(
        link='misconfig.index_html',
        title=u'Настройки МИС',
        visible=UserProfileManager.has_ui_admin(),
    ), dict(
        link='dict.index',
        title=u'Справочники',
        visible=UserProfileManager.has_ui_admin(),
    ), dict(
        link='logging.index',
        title=u'Журнал',
        visible=UserProfileManager.has_ui_admin(),
    ), dict(
        link='reports.index',
        title=u'Отчёты',
        visible=UserProfileManager.has_ui_admin(),
    ), dict(
        link='risar_config.index',
        title=u'РИСАР',
        visible=True,
    ), dict(
        link='print_subsystem.index',
        title=u'Печать',
        visible=UserProfileManager.has_ui_admin(),
    )]
    return dict(main_menu=menu_items)


@app.context_processor
def app_enum():
    return {
        'app_version': app_version,
        'version': app_version
    }


@frontend_config
def caesar_urls():
    """
    URL'ы caesar
    :return:
    """
    return {
        'url': {
            'misconfig': {
                # expert protocols
                'html_expert_protocol_protocols': url_for('misconfig.expert_protocol_protocol_html'),
                'html_expert_protocol_scheme_measures': url_for('misconfig.expert_protocol_scheme_measures_html'),
                'api_expert_protocol_base': url_for('misconfig.api_v1_expert_protocol_get'),
                'api_expert_protocol_list_base': url_for('misconfig.api_v1_expert_protocol_list_get'),
                'api_expert_scheme_base': url_for('misconfig.api_v1_expert_scheme_get'),
                'api_expert_scheme_measure_base': url_for('misconfig.api_v1_expert_scheme_measure_get'),
                'api_expert_scheme_measure_list_base': url_for('misconfig.api_v1_expert_scheme_measure_list_get'),
                # org
                'api_org_base': url_for('misconfig.api_v1_org_get'),
                'api_org_list_base': url_for('misconfig.api_v1_org_list_get'),
                'api_org_birth_care_level_base': url_for('misconfig.api_v1_org_birth_care_level_get'),
                'api_org_birth_care_level_list_base': url_for('misconfig.api_v1_org_birth_care_level_list_get'),
                # person
                'api_person_base': url_for('misconfig.api_v1_person_get'),
                'api_person_list_base': url_for('misconfig.api_v1_person_list_get'),
                'api_person_curation_level_list_get': url_for('misconfig.api_v1_person_curation_level_list_get'),
                # print_template
                'api_print_template_base': url_for('misconfig.api_v1_print_template_get'),
                'api_print_template_list_base': url_for('misconfig.api_v1_print_template_list_get'),
            }
        },
    }


from blueprints.print_subsystem.app import module as print_subsystem_module
from blueprints.dict.app import module as dict_module
from blueprints.logging.app import module as logging_module
from blueprints.reports.app import module as reports_module
from blueprints.risar_config.app import module as risar_config_module
# from blueprints.tfoms.app import module as tfoms_module
from blueprints.misconfig.app import module as misconfig_module

app.register_blueprint(print_subsystem_module, url_prefix='/print_subsystem')
app.register_blueprint(dict_module, url_prefix='/dict')
app.register_blueprint(logging_module, url_prefix='/logging')
app.register_blueprint(reports_module, url_prefix='/reports')
app.register_blueprint(risar_config_module, url_prefix='/risar_config')
# app.register_blueprint(tfoms_module, url_prefix='/tfoms')
app.register_blueprint(misconfig_module, url_prefix='/misconfig')

if __name__ == "__main__":
    app.run(port=app.config['SERVER_PORT'])