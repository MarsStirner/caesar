# -*- coding: utf-8 -*-
import os
from nemesis.app import app, bootstrap_app
import config

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
    ), dict(
        link='tfoms.index',
        title=u'ТФОМС',
        visible=UserProfileManager.has_ui_admin(),
    )]
    return dict(main_menu=menu_items)


from blueprints.print_subsystem.app import module as print_subsystem_module
from blueprints.dict.app import module as dict_module
from blueprints.logging.app import module as logging_module
from blueprints.misconfig.app import module as misconfig_module
from blueprints.reports.app import module as reports_module
from blueprints.risar_config.app import module as risar_config_module
from blueprints.tfoms.app import module as tfoms_module
from blueprints.misconfig.app import module as misconfig_module

app.register_blueprint(print_subsystem_module, url_prefix='/print_subsystem')
app.register_blueprint(dict_module, url_prefix='/dict')
app.register_blueprint(logging_module, url_prefix='/logging')
app.register_blueprint(misconfig_module, url_prefix='/misconfig')
app.register_blueprint(reports_module, url_prefix='/reports')
app.register_blueprint(risar_config_module, url_prefix='/risar_config')
app.register_blueprint(tfoms_module, url_prefix='/tfoms')
app.register_blueprint(misconfig_module, url_prefix='/misconfig')

if __name__ == "__main__":
    app.run()