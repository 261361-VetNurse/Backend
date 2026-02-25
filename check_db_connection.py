from pathlib import Path
import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import text

# Ensure the project's database .env is loaded (Backend/database/.env)
here = Path(__file__).resolve().parent
env_path = here / "database" / ".env"
if env_path.exists():
    load_dotenv(env_path)

from app.models_sql.base import get_async_engine


async def test_connection():
    engine = get_async_engine()
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            scalar = result.scalar()
            print("Database reachable, SELECT 1 returned:", scalar)
            return 0
    except Exception as exc:
        print("Failed to connect to database:", exc)
        return 2
    finally:
        await engine.dispose()


def main():
    code = asyncio.run(test_connection())
    raise SystemExit(code)


if __name__ == "__main__":
    main()
