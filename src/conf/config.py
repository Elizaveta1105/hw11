from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator, EmailStr


class Settings(BaseSettings):
    DB_URL: str = "postgresql+psycopg2://postgres:password@localhost:5432/postgres"
    SECRET_KEY_JWT: str = 'secret'
    ALGORITHM: str = 'HS256'
    MAIL_USERNAME: EmailStr = 'username@test.com'
    MAIL_PASSWORD: str = 'password'
    MAIL_FROM: str = 'from@test.com'
    MAIL_PORT: int = 435
    MAIL_SERVER: str = 'smtp.meta.com'
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "test"
    CLD_NAME: str = 'cloud_name'
    CLD_API_KEY: str = 'api_key'
    CLD_API_SECRET: str = 'api'


    @field_validator('ALGORITHM')
    @classmethod
    def validate_algorithm(cls, value):
        if value not in ['HS256', 'HS384', 'HS512']:
            raise ValueError('Invalid algorithm')
        return value

    model_config = ConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8") # noqa


config = Settings()
