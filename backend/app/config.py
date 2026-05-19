import os


# Runtime configuration is read from environment variables.
# This keeps deployment settings outside the source code.
raw_database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://warehouse:warehouse@localhost:5432/warehouse",
)
DATABASE_URL = (
    raw_database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    .replace("postgres://", "postgresql+psycopg://", 1)
)
AUTO_SEED = os.getenv("AUTO_SEED", "true").lower() in {"1", "true", "yes", "on"}
