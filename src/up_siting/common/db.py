"""Database connection settings, read from the environment (.env via make / docker compose).

Defaults match .env.example so a fresh checkout works without extra setup.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DbSettings:
    host: str
    port: int
    user: str
    password: str
    dbname: str

    @classmethod
    def from_env(cls) -> "DbSettings":
        return cls(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", "5432")),
            user=os.environ.get("POSTGRES_USER", "up_siting"),
            password=os.environ.get("POSTGRES_PASSWORD", "change-me-locally"),
            dbname=os.environ.get("POSTGRES_DB", "up_siting"),
        )

    def conninfo(self) -> str:
        """A libpq connection string for psycopg.connect(). Never log it: it holds the password."""
        return (
            f"host={self.host} port={self.port} user={self.user} "
            f"password={self.password} dbname={self.dbname}"
        )
