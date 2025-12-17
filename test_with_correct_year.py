"""
Test with correct year 2024.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime


# IMPORTANT: Use 2024 not 2025!
date_str = "2024-12-17"  # Today is December 17, 2024

session = requests.Session()

# Step 1: Set date
print(f"Setting date: {date_str}")
save_url = "http://lntrt.ru/save"
save_params = {"dateSched": date_str, "academicYear": date_str}
session.get(save_url, params=save_params, timeout=10)

# Step 2: Get schedule
schedule_url = "http://lntrt.ru/fulltime/daySchedule"
response = session.get(schedule_url, timeout=10)

print(f"Response status: {response.status_code}")
print(f"Content length: {len(response.content)}")

# Check for title
soup = BeautifulSoup(response.content, 'lxml')
title = soup.find('title')
print(f"Page title: {title.get_text() if title else 'N/A'}")

# Look for schedule table
table = soup.find('table', class_='border')
print(f"Table with class='border': {table is not None}")

# Look for group names
test_group = "ИС-1-24"
all_text = soup.get_text()
if test_group in all_text:
    print(f"✅ Found group '{test_group}' in page!")
else:
    print(f"❌ Group '{test_group}' not found")

# Save
with open('schedule_2024.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Saved to schedule_2024.html")
