import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from handlers import router
from database import Database
from scheduler import setup_scheduler


# Load environment variables
load_dotenv()

# Get bot token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables. Please set it in .env file.")

# Initialize database
db = Database()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Main function to run the bot.
    """
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register router
    dp.include_router(router)
    
    # Setup and start scheduler
    scheduler = setup_scheduler(bot, db)
    scheduler.start()
    logger.info("📅 Scheduler started - daily notifications enabled at 18:00")
    
    logger.info("🚀 Bot started successfully!")
    
    try:
        # Start polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Shutdown scheduler on exit
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
