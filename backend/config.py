from pydantic import BaseModel


class Settings(BaseModel):
    secret_key: str = "your_secret_key"  # Замените на свой ключ
    algorithm: str = "HS256"  # Алгоритм шифрования
    access_token_expire_minutes: int = 120  # Время жизни токена (в минутах)

    class Config:
        env_file = ".env"


settings = Settings()
