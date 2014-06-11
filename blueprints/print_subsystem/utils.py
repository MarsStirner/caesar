# -*- encoding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from application.utils import create_config_func
from blueprints.print_subsystem.models.models_all import ConfigVariables
from .config import MODULE_NAME, LPU_DB_CONNECT_STRING, KLADR_DB_CONNECT_STRING

_config = create_config_func(MODULE_NAME, ConfigVariables)
