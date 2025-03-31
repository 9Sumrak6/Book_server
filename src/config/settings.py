from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # for PostgreSQL
    db_host: str = "127.0.0.1:5432"
    db_name: str = "your_db_name"
    db_username: str = "your_username"
    db_password: str = "your_password"
    db_test_name: str = "your_db_test_name"
    max_connection_count: int = 10

    @property
    def database_url(self) -> str:
        return "postgresql+asyncpg://" + self.db_username + ":" + self.db_password + "@" + self.db_host + "/" + self.db_name

    @property
    def database_test_url(self) -> str:
        return "postgresql+asyncpg://" + self.db_username + ":" + self.db_password + "@" + self.db_host + "/" + self.db_test_name

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()