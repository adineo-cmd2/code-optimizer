from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./optimizer.db"
    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    backend_port: int = 8008
    frontend_origin: str = "http://localhost:4328"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
