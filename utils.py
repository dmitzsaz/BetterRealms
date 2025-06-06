from aiohttp import web, ClientSession
import time
import boto3
import asyncio
from concurrent.futures import ThreadPoolExecutor
from botocore.config import Config
import requests

from config import settings
from database import crud

verifiedTokens = {}

@web.middleware
async def logging_middleware(request, handler):
    method = request.method
    path = request.path
    query = dict(request.query)
    try:
        body = await request.text()
    except Exception:
        body = ''

    print(f"[LOG] {method} {path} | query={query} | body={body}")

    # Формируем curl-команду для воспроизведения запроса
    curl_cmd = f"curl -X {method} '{request.url}'"
    # Добавляем заголовки
    for k, v in request.headers.items():
        curl_cmd += f" -H '{k}: {v}'"
    # Добавляем тело, если оно есть и не пустое
    if body:
        curl_cmd += f" --data '{body}'"
    #print(f"[CURL] {curl_cmd}")

    response = await handler(request)
    return response

@web.middleware
async def validateAuth(request, handler):
    username, uuid, version, fullToken = None, None, None, None

    cookies = request.headers.get("Cookie", "").split(";")

    for i in cookies:
        parts = i.split("=")
        name = parts[0].strip()
        data = parts[1].strip()

        if name == "user":
            username = data
        if name == "sid":
            uuid = data.split(":")[2]
            fullToken = data
        if name == "version":
            version = data

    if fullToken in verifiedTokens and time.time() - verifiedTokens[fullToken]['ttl'] < 600:
        request['AuthData'] = verifiedTokens[fullToken]
        return await handler(request)

    url = "https://pc.realms.minecraft.net/mco/available"

    cookie_str = f"user={username}; sid={fullToken}; version={version}"
    headers = {
        "Cookie": cookie_str,
        "User-Agent": "Java/1.6.0_27"
    }

    request['AuthData'] = {"username": username, "uuid": uuid}
    if username and uuid:
        if not crud.update_uuid_to_nickname(uuid, username):
            crud.create_uuid_to_nickname(uuid, username)
    return await handler(request)

    async with ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.text()
                if data == "true":
                    verifiedTokens[fullToken] = {
                        "username": username,
                        "uuid": uuid,
                        "ttl": time.time() + 600
                    }
                    request['AuthData'] = {"username": username, "uuid": uuid}
                    return await handler(request)
    return web.Response(status=401)


def upload_to_r2_sync(file_path: str, object_name: str) -> str:
    session = boto3.session.Session()
    client = session.client(
        service_name='s3',
        aws_access_key_id=settings.R2_ACCESS_KEY,
        aws_secret_access_key=settings.R2_SECRET_KEY,
        endpoint_url=settings.R2_ENDPOINT,
        config=Config(signature_version='s3v4'),
        region_name='auto'
    )
    client.upload_file(file_path, settings.R2_BUCKET, object_name)
    return f"https://{settings.R2_BUCKET}.{settings.R2_ENDPOINT.replace('https://', '')}/{object_name}"

async def upload_to_r2(file_path: str, object_name: str) -> str:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, upload_to_r2_sync, file_path, object_name)

async def getUUIDtoNickname(username: str) -> str:
    uuid_to_nickname = crud.get_uuid_to_nickname_by_username(username)
    if uuid_to_nickname:
        return uuid_to_nickname.nickname

    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    async with ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                udid = data.get("id")
                return udid

    return None

def getPlayerNameSync(uuid: str) -> str:
    uuid_to_nickname = crud.get_uuid_to_nickname(uuid)
    if uuid_to_nickname:
        return uuid_to_nickname.nickname

    url = f"https://api.mojang.com/user/profiles/{uuid}/names"
    with requests.get(url) as resp:
        if resp.status_code == 200:
            data = resp.json()
            return data[0]["name"]

    return None

async def getPlayerName(uuid: str) -> str:
    uuid_to_nickname = crud.get_uuid_to_nickname(uuid)
    if uuid_to_nickname:
        return uuid_to_nickname.nickname

    url = f"https://api.mojang.com/user/profiles/{uuid}/names"
    async with ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()

    return None