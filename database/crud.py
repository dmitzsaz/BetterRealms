from typing import Optional, List
from .db import SessionLocal
from .models import World, Realm, Invite, RealmState, UUIDtoNickname

# Получить все миры
def get_worlds() -> List[World]:
    with SessionLocal() as session:
        return session.query(World).all()

# Получить мир по id
def get_world(world_id: int) -> Optional[World]:
    with SessionLocal() as session:
        return session.query(World).filter(World.id == world_id).first()

# Создать новый мир
def create_world(name: str, s3URL: str, status: str = "stopped", admins = [], players = []) -> World:
    with SessionLocal() as session:
        world = World(name=name, s3URL=s3URL, status=status, admins=admins, players=players)
        session.add(world)
        session.commit()
        session.refresh(world)
        return world

# Обновить мир
def update_world(world_id: int, **kwargs) -> World:
    with SessionLocal() as session:
        world = session.query(World).filter(World.id == world_id).first()
        if not world:
            raise ValueError("Мир не найден")
        for key, value in kwargs.items():
            if hasattr(world, key):
                setattr(world, key, value)
            else:
                raise ValueError(f"Некорректный атрибут: {key}")
        session.commit()
        session.refresh(world)
        return world

# Удалить мир
def delete_world(world_id: int) -> bool:
    with SessionLocal() as session:
        world = session.query(World).filter(World.id == world_id).first()
        if not world:
            return False
        session.delete(world)
        session.commit()
        return True 

def add_admin(world_id: int, admin_id: str) -> bool:
    with SessionLocal() as session:
        world = session.query(World).filter(World.id == world_id).first()
        if not world:
            return False
        world.admins.append(admin_id)
        session.commit()
        return True
    
def add_player(world_id: int, player_id: str) -> bool:
    with SessionLocal() as session:
        world = session.query(World).filter(World.id == world_id).first()
        if not world:
            return False
        world.players.append(player_id)
        session.commit()
        return True
    
def remove_admin(world_id: int, admin_id: str) -> bool:
    with SessionLocal() as session:
        world = session.query(World).filter(World.id == world_id).first()
        if not world:
            return False
        world.admins.remove(admin_id)
        session.commit()
        return True
    
def remove_player(world_id: int, player_id: str) -> bool:
    with SessionLocal() as session:
        world = session.query(World).filter(World.id == world_id).first()
        if not world:
            return False
        world.players.remove(player_id)
        session.commit()
        return True

def get_realms() -> List[Realm]:
    """Получить все Realms"""
    with SessionLocal() as session:
        return session.query(Realm).all()


def get_realm(realm_id: int) -> Optional[Realm]:
    """Получить Realm по id"""
    with SessionLocal() as session:
        return session.query(Realm).filter(Realm.id == realm_id).first()


def create_realm(
    name: str,
    motd: str = "",
    worlds: list | dict = None,
    owner: list[str] | None = None,
    ownerUUID: str | None = None,
    state: RealmState = RealmState.UNINITIALIZED,
    active_world: int | None = None,
    members: list[str] | None = None,
) -> Realm:
    """Создать новый Realm"""
    worlds = worlds or []
    owner = owner or []
    members = members or []
    with SessionLocal() as session:
        realm = Realm(
            name=name,
            motd=motd,
            worlds=worlds,
            owner=owner,
            members=members,
            ownerUUID=ownerUUID,
            state=state,
            active_world=active_world,
        )
        session.add(realm)
        session.commit()
        session.refresh(realm)
        return realm


def update_realm(realm_id: int, **kwargs) -> Realm:
    """Обновить Realm. Передайте любые валидные поля в kwargs"""
    with SessionLocal() as session:
        realm = session.query(Realm).filter(Realm.id == realm_id).first()
        if not realm:
            raise ValueError("Realm не найден")
        for key, value in kwargs.items():
            if hasattr(realm, key):
                setattr(realm, key, value)
            else:
                raise ValueError(f"Некорректный атрибут: {key}")
        session.commit()
        session.refresh(realm)
        return realm


def delete_realm(realm_id: int) -> bool:
    """Удалить Realm"""
    with SessionLocal() as session:
        realm = session.query(Realm).filter(Realm.id == realm_id).first()
        if not realm:
            return False
        session.delete(realm)
        session.commit()
        return True


def add_member(realm_id: int, uuid: str) -> bool:
    """Добавить участника в Realm"""
    with SessionLocal() as session:
        realm = session.query(Realm).filter(Realm.id == realm_id).first()
        if not realm:
            return False
        if uuid not in realm.members:
            realm.members.append(uuid)
            session.commit()
        return True


def remove_member(realm_id: int, uuid: str) -> bool:
    """Удалить участника из Realm"""
    with SessionLocal() as session:
        realm = session.query(Realm).filter(Realm.id == realm_id).first()
        if not realm:
            return False
        if uuid in realm.members:
            realm.members.remove(uuid)
            session.commit()
        return True

def get_invite_by_username(invited_username: str) -> Optional[Invite]:
    with SessionLocal() as session:
        return session.query(Invite).filter(Invite.invited_username == invited_username).all()

def get_invite(realm_id: int, invited_username: str) -> Optional[Invite]:
    with SessionLocal() as session:
        return session.query(Invite).filter(Invite.realms_id == realm_id, Invite.invited_username == invited_username).first()

def get_invites() -> List[Invite]:
    with SessionLocal() as session:
        return session.query(Invite).all()


def get_invites_by_realm(realm_id: int) -> List[Invite]:
    with SessionLocal() as session:
        return session.query(Invite).filter(Invite.realms_id == realm_id).all()


def create_invite(realm_id: int, invited_username: str, invited_uuid: str) -> Invite:
    with SessionLocal() as session:
        invite = Invite(realms_id=realm_id, invited_username=invited_username, invited_uuid=invited_uuid)
        session.add(invite)
        session.commit()
        session.refresh(invite)
        return invite


def delete_invite(invite_id: int) -> bool:
    with SessionLocal() as session:
        invite = session.query(Invite).filter(Invite.id == invite_id).first()
        if not invite:
            return False
        session.delete(invite)
        session.commit()
        return True


def accept_invite(invite_id: int) -> bool:
    with SessionLocal() as session:
        invite = session.query(Invite).filter(Invite.id == invite_id).first()
        if not invite:
            return False
        realm = session.query(Realm).filter(Realm.id == invite.realms_id).first()
        if not realm:
            # Нет Realm – удаляем invite
            session.delete(invite)
            session.commit()
            return False
        if invite.invited_uuid not in realm.members:
            realm.members.append(invite.invited_uuid)
        session.delete(invite)
        session.commit()
        return True

def get_uuid_to_nickname(uuid: str) -> Optional[UUIDtoNickname]:
    with SessionLocal() as session:
        return session.query(UUIDtoNickname).filter(UUIDtoNickname.uuid == uuid).first()

def get_uuid_to_nickname_by_username(username: str) -> Optional[UUIDtoNickname]:
    with SessionLocal() as session:
        return session.query(UUIDtoNickname).filter(UUIDtoNickname.nickname == username).first()

def create_uuid_to_nickname(uuid: str, nickname: str) -> UUIDtoNickname:
    with SessionLocal() as session:
        uuid_to_nickname = UUIDtoNickname(uuid=uuid, nickname=nickname)
        session.add(uuid_to_nickname)
        session.commit()
        session.refresh(uuid_to_nickname)
    
def update_uuid_to_nickname(uuid: str, nickname: str) -> UUIDtoNickname:
    with SessionLocal() as session:
        uuid_to_nickname = session.query(UUIDtoNickname).filter(UUIDtoNickname.uuid == uuid).first()
        if not uuid_to_nickname:
            return False
        uuid_to_nickname.nickname = nickname
        session.commit()
        session.refresh(uuid_to_nickname)
        return uuid_to_nickname