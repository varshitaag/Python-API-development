from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str="localhost"
    database_name: str
    database_username: str="postgres"
    secret_key:str="24uijhdj"
    algorithm: str
    access_token_expire_minutes: int = Field(
        validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_MINUTES", "ACCESS_TOKEN_EXPIRY_MINUTES")
    )

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env")
    )


settings= Settings()