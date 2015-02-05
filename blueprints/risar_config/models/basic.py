# coding: utf-8
from sqlalchemy import Column, DateTime, Index, Integer, SmallInteger, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class MKB(Base):
    __tablename__ = 'MKB'
    __table_args__ = (
        Index('BlockID', 'BlockID', 'DiagID'),
        Index('ClassID_2', 'ClassID', 'BlockID', 'BlockName'),
        Index('ClassID', 'ClassID', 'ClassName')
    )

    id = Column(Integer, primary_key=True)
    ClassID = Column(String(8), nullable=False)
    ClassName = Column(String(150), nullable=False)
    BlockID = Column(String(9), nullable=False)
    BlockName = Column(String(160), nullable=False)
    DiagID = Column(String(8), nullable=False, index=True)
    DiagName = Column(String(160), nullable=False, index=True)
    Prim = Column(String(1), nullable=False)
    sex = Column(Integer, nullable=False)
    age = Column(String(12), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    characters = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    service_id = Column(Integer, index=True)
    MKBSubclass_id = Column(Integer)


class Organisation(Base):
    __tablename__ = 'Organisation'
    __table_args__ = (
        Index('shortName', 'shortName', 'INN', 'OGRN'),
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    fullName = Column(String(255), nullable=False)
    shortName = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    net_id = Column(Integer, index=True)
    infisCode = Column(String(12), nullable=False, index=True)
    obsoleteInfisCode = Column(String(60), nullable=False)
    OKVED = Column(String(64), nullable=False, index=True)
    INN = Column(String(15), nullable=False, index=True)
    KPP = Column(String(15), nullable=False)
    OGRN = Column(String(15), nullable=False, index=True)
    OKATO = Column(String(15), nullable=False)
    OKPF_code = Column(String(4), nullable=False)
    OKPF_id = Column(Integer, index=True)
    OKFS_code = Column(Integer, nullable=False)
    OKFS_id = Column(Integer, index=True)
    OKPO = Column(String(15), nullable=False)
    FSS = Column(String(10), nullable=False)
    region = Column(String(40), nullable=False)
    Address = Column(String(255), nullable=False)
    chief = Column(String(64), nullable=False)
    phone = Column(String(255), nullable=False)
    accountant = Column(String(64), nullable=False)
    isInsurer = Column(Integer, nullable=False, index=True)
    compulsoryServiceStop = Column(Integer, nullable=False, server_default=u"'0'")
    voluntaryServiceStop = Column(Integer, nullable=False, server_default=u"'0'")
    area = Column(String(13), nullable=False)
    isHospital = Column(Integer, nullable=False, server_default=u"'0'")
    notes = Column(String, nullable=False)
    head_id = Column(Integer, index=True)
    miacCode = Column(String(10), nullable=False)
    isOrganisation = Column(Integer, nullable=False, server_default=u"'0'")
    uuid_id = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    OID = Column(String(127))

    def __json__(self):
        return {
            'id': self.id,
            'name': self.shortName,
        }