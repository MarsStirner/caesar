# -*- coding: utf-8 -*-
from application.database import db
from config import MODULE_NAME
from sqlalchemy import BigInteger, Column, Date, DateTime, Enum, Float, ForeignKey, Index, Integer, SmallInteger, \
    String, Table, Text, Time, Unicode, Boolean
from sqlalchemy.ext.declarative import declarative_base


TABLE_PREFIX = MODULE_NAME
Base = declarative_base()
metadata = Base.metadata


class Kladr(Base):
    __tablename__ = 'KLADR'
    __table_args__ = (
        Index('long_name', 'prefix', 'NAME', 'SOCR', 'STATUS'),
        Index('NAME', 'NAME', 'SOCR'),
        Index('parent', 'parent', 'NAME', 'SOCR', 'CODE')
    )

    NAME = Column(Unicode(40), nullable=False)
    SOCR = Column(Unicode(10), nullable=False)
    CODE = Column(String(13), primary_key=True)
    INDEX = Column(String(6), nullable=False)
    GNINMB = Column(String(4), nullable=False)
    UNO = Column(String(4), nullable=False)
    OCATD = Column(String(11), nullable=False, index=True)
    STATUS = Column(String(1), nullable=False)
    parent = Column(String(13), nullable=False)
    infis = Column(String(5), nullable=False, index=True)
    prefix = Column(String(2), nullable=False)
    id = Column(Integer, nullable=False, unique=True)


class Street(Base):
    __tablename__ = 'STREET'
    __table_args__ = (
        Index('NAME_SOCR', 'NAME', 'SOCR', 'CODE'),
    )

    NAME = Column(Unicode(40), nullable=False)
    SOCR = Column(Unicode(10), nullable=False)
    CODE = Column(String(17), primary_key=True)
    INDEX = Column(String(6), nullable=False)
    GNINMB = Column(String(4), nullable=False)
    UNO = Column(String(4), nullable=False)
    OCATD = Column(String(11), nullable=False)
    infis = Column(String(5), nullable=False, index=True)