from sqlalchemy import Column, Integer, String, JSON, BigInteger, ForeignKey, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime
import enum


class RealmState(enum.Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    UNINITIALIZED = "UNINITIALIZED"


class World(Base):
    __tablename__ = "worlds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=False)
    s3URL = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    admins = Column(JSON, nullable=False, default=list)
    players = Column(JSON, nullable=False, default=list)


class Realm(Base):
    __tablename__ = "realms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    motd = Column(String(255), nullable=True)
    worlds = Column(JSON, nullable=False, default=list)
    members = Column(JSON, nullable=False, default=list)
    owner = Column(JSON, nullable=False, default=list)
    state = Column(SqlEnum(RealmState), nullable=False, default=RealmState.UNINITIALIZED)
    active_world = Column(Integer, nullable=True)
    ownerUUID = Column(String(64), nullable=True)

    # relationships
    invites = relationship("Invite", back_populates="realm", cascade="all, delete, delete-orphan")


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, index=True)
    realms_id = Column(Integer, ForeignKey("realms.id", ondelete="CASCADE"), nullable=False)
    invited_uuid = Column(String(64), nullable=True)
    invited_username = Column(String(255), nullable=False)

    # relationships
    realm = relationship("Realm", back_populates="invites")

class UUIDtoNickname(Base):
    __tablename__ = "uuidtonickname"

    uuid = Column(String(64), nullable=False, primary_key=True)
    nickname = Column(String(255), nullable=False)