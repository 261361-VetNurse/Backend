"""
Standalone scheduler worker process.
Run with: python -m app.scheduler_worker
Connects to the database and runs the APScheduler loop indefinitely.
"""
import asyncio
from app.database_sql import connect_to_mysql, close_mysql_connection
from app.services.notification_scheduler_sql import notification_scheduler_sql


async def main():
    await connect_to_mysql()
    notification_scheduler_sql.start()
    print("Scheduler worker is running. Press Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(60)
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        notification_scheduler_sql.shutdown()
        await close_mysql_connection()


if __name__ == "__main__":
    asyncio.run(main())
