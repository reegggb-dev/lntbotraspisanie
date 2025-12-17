"""
Scheduler for automated notifications.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from parser import fetch_schedule, format_schedule
from database import Database


async def send_daily_schedule(bot, db: Database):
    """
    Send tomorrow's schedule to all users with notifications enabled.
    Runs daily at 18:00.
    """
    print(f"[{datetime.now()}] Starting daily schedule notification...")
    
    # Get all users who want notifications
    users = db.get_all_users_with_notifications()
    
    sent_count = 0
    error_count = 0
    
    for user_id, group in users:
        try:
            # Fetch tomorrow's schedule
            lessons = fetch_schedule(group, days_offset=1)
            
            if lessons is not None:
                # Format the schedule
                schedule_text = format_schedule(lessons, group, days_offset=1)
                
                # Add header
                message = f"🔔 **Расписание на завтра**\n\n{schedule_text}"
                
                # Send to user
                await bot.send_message(user_id, message, parse_mode="Markdown")
                sent_count += 1
            
        except Exception as e:
            print(f"Error sending to user {user_id}: {e}")
            error_count += 1
    
    print(f"Notifications sent: {sent_count}, errors: {error_count}")


def setup_scheduler(bot, db: Database):
    """
    Setup the scheduler for daily notifications.
    """
    scheduler = AsyncIOScheduler()
    
    # Schedule daily notification at 18:00 (6 PM)
    scheduler.add_job(
        send_daily_schedule,
        'cron',
        hour=18,
        minute=0,
        args=[bot, db],
        id='daily_schedule',
        replace_existing=True
    )
    
    return scheduler
