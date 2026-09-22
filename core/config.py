from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "gasuser"
    DB_PASSWORD: str = "gaspassword"
    DB_NAME: str = "gas_db"
    MINIO_BASE: str = "http://localhost:9000/media"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
