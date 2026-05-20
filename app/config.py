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

    mail_username: str = Field(default="", validation_alias=AliasChoices("mail_username", "MAIL_USERNAME"))
    mail_password: str = Field(default="", validation_alias=AliasChoices("mail_password", "MAIL_PASSWORD"))
    mail_from: str = Field(default="", validation_alias=AliasChoices("mail_from", "MAIL_FROM"))
    mail_port: int = Field(default=587, validation_alias=AliasChoices("mail_port", "MAIL_PORT"))
    mail_server: str = Field(default="", validation_alias=AliasChoices("mail_server", "MAIL_SERVER"))

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env")
    )


settings= Settings()