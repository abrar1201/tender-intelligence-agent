from apscheduler.schedulers.blocking import BlockingScheduler
import asyncio
from main import run
from emailer import send_daily_summary

scheduler = BlockingScheduler()

# Run every day at 9 AM
@scheduler.scheduled_job('cron', hour=9, minute=0)
def daily_job():
    print("Running scheduled tender job...")
    asyncio.run(run())
    send_daily_summary()
    print("Job completed.")


if __name__ == "__main__":
    print("Tender Intelligence Scheduler started...")
    scheduler.start()