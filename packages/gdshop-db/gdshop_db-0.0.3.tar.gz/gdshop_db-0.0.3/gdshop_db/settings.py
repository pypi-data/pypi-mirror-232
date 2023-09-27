from pydantic import BaseSettings


class DBSettings(BaseSettings):
    DB_DSB: str
