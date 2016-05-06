# -*- coding: utf-8 -*-
import os

from nemesis.app import app, bootstrap_app
from tsukino_usagi.client import TsukinoUsagiClient
from version import version as app_version

__author__ = 'viruzzz-kun'


class CaesarUsagiClient(TsukinoUsagiClient):
    def on_configuration(self, configuration):
        configuration['APP_VERSION'] = app_version
        app.config.update(configuration)
        bootstrap_app(os.path.join(os.path.dirname(__file__), 'templates'))

        from blueprints.print_subsystem.app import module as print_subsystem_module
        # from blueprints.dict.app import module as dict_module
        from blueprints.logging.app import module as logging_module
        # from blueprints.reports.app import module as reports_module
        from blueprints.risar_config.app import module as risar_config_module
        # from blueprints.tfoms.app import module as tfoms_module
        from blueprints.misconfig.app import module as misconfig_module

        app.register_blueprint(print_subsystem_module, url_prefix='/print_subsystem')
        # app.register_blueprint(dict_module, url_prefix='/dict')
        app.register_blueprint(logging_module, url_prefix='/logging')
        # app.register_blueprint(reports_module, url_prefix='/reports')
        app.register_blueprint(risar_config_module, url_prefix='/risar_config')
        # app.register_blueprint(tfoms_module, url_prefix='/tfoms')
        app.register_blueprint(misconfig_module, url_prefix='/misconfig')
