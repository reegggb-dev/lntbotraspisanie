import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Schedule URL
SCHEDULE_URL = "http://lntrt.ru/fulltime/daySchedule"

# All groups from the website (extracted during analysis)
GROUPS = [
    "СЭН-25", "ПГ-1-25", "ПГ-2-25", "ЭП-25", "М-25", 
    "ИС-1-25", "ИС-2-25", "ЭКС-1-25", "ЭКС-2-25", "ЭКС-3-25",
    "Б-25", "ГР-1-25", "ГР-2-25", "АСУ-1-25", "АСУ-2-25",
    "ГП-1-25", "ГП-2-25", "ГП-1-24", "ГП-2-24", "ИС-1-24",
    "ИС-2-24", "ПГ-1-24", "ПГ-2-24", "ПН-24", "АСУ-1-24",
    "АСУ-2-24", "М-24", "ЭП-24", "Б-24", "ЭКС-1-24",
    "ЭКС-2-24", "ЭКС-3-24", "ГП-1-23", "ГП-2-23", "ГР-1-23",
    "Б-1-23", "ЭКС-1-23", "ЭКС-2-23", "ИС-1-23", "ИС-2-23",
    "М-23", "ЭП-23", "ПГ-23", "СЭН-23", "ПН-23"
]

# Groups per page for pagination
GROUPS_PER_PAGE = 10
