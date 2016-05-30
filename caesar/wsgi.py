# -*- coding: utf-8 -*-

import os
import config

from flask import url_for

from nemesis.app import app, bootstrap_app
from nemesis.lib.frontend import frontend_config
from usagicompat import CaesarUsagiClient
from version import version as app_version

__author__ = 'viruzzz-kun'

usagi = CaesarUsagiClient(app.wsgi_app, os.getenv('TSUKINO_USAGI_URL', 'http://127.0.0.1:5900'), 'caesar')
app.wsgi_app = usagi.app
usagi()


@app.context_processor
def general_menu():
    from nemesis.lib.user import UserProfileManager
    from nemesis.lib.settings import Settings
    mis_settings = Settings()
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
        link='logging.index',
        title=u'Журнал',
        visible=UserProfileManager.has_ui_admin(),
    ), dict(
        link='print_subsystem.index',
        title=u'Печать',
        visible=UserProfileManager.has_ui_admin(),
    )
    # dict(
    #     link='dict.index',
    #     title=u'Справочники',
    #     visible=UserProfileManager.has_ui_admin(),
    # ), dict(
    #     link='reports.index',
    #     title=u'Отчёты',
    #     visible=UserProfileManager.has_ui_admin(),
    # ),
    ]
    if mis_settings.getBool('RISAR.Enabled', False):
        menu_items.append(dict(
            link='risar_config.index',
            title=u'РИСАР',
            visible=UserProfileManager.has_ui_admin(),
        ))
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
                #person_contact
                'api_person_contact_base': url_for('misconfig.api_v1_person_contact_get'),
                # print_template
                'api_print_template_base': url_for('misconfig.api_v1_print_template_get'),
                'api_print_template_list_base': url_for('misconfig.api_v1_print_template_list_get'),
                # pricelist
                'html_price_list': url_for('misconfig.price_list_html'),
                'api_pricelist_base': url_for('misconfig.api_v1_pricelist_get'),
                'api_pricelist_list_base': url_for('misconfig.api_v1_pricelist_list_get'),
                'api_pricelist_item_base': url_for('misconfig.api_v1_pricelist_item_get', pricelist_id=-99999).replace('-99999', '{0}'),
                'api_pricelist_item_list_base': url_for('misconfig.api_v1_pricelist_item_list_get', pricelist_id=-99999).replace('-99999', '{0}'),
                # rbservice
                'api_rb_service_group_assoc_base': url_for('misconfig.api_v1_rb_service_group_assoc_get')
            }
        },
    }


if __name__ == "__main__":
    app.run(port=app.config.get('SERVER_PORT', 6601))