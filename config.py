from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    LISTEN_ADDR: str = "0.0.0.0:8080"

    DB_USER_NAME: str = "root"
    DB_ROOT_PASSWORD: str
    DB_NAME: str = "realms"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306

    R2_ENDPOINT: str
    R2_ACCESS_KEY: str
    R2_SECRET_KEY: str
    R2_BUCKET: str

    REALMSORCHESTRATOR_URL: str = "http://realmsorchestrator:8080"
    REALMSORCHESTRATOR_IP: str

settings = Settings()