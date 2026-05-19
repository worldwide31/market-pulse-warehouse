import os


# Runtime configuration is read from environment variables.
# This keeps deployment settings outside the source code.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://warehouse:warehouse@localhost:5432/warehouse",
)
AUTO_SEED = os.getenv("AUTO_SEED", "true").lower() in {"1", "true", "yes", "on"}
