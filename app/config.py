from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # The contract between our code and the environment.
    # If DATABASE_URL or SECRET_KEY are missing, the app crashes at startup
    # with a clear error  much better than a mysterious 500 in production.
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

# Single instance  imported wherever config is needed
settings = Settings()
