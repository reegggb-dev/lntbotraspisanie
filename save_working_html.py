"""
Save the actual schedule response with correct endpoint and header.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime


date_str = "2025-12-17"

session = requests.Session()
headers = {"X-Requested-With": "XMLHttpRequest"}

# Step 1: Set date
session.get(f"http://lntrt.ru/save?dateSched={date_str}&academicYear={date_str}", headers=headers)

# Step 2: Get schedule
response = session.get("http://lntrt.ru/schedule/daySchedule", headers=headers)

print(f"Status: {response.status_code}")
print(f"Length: {len(response.content)}")

# Save
with open('working_schedule.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

# Parse and analyze
soup = BeautifulSoup(response.content, 'lxml')
table = soup.find('table', class_='border')

if table:
    print("✅ Found table with class='border'!")
    
    # Count rows and cells
    rows = table.find_all('tr')
    print(f"Rows: {len(rows)}")
    
    # Check first row - should have group names
    if rows:
        first_row = rows[0]
        cells = first_row.find_all(['td', 'th'])
        print(f"\nFirst row has {len(cells)} cells:")
        for i, cell in enumerate(cells[:15]):  # First 15 cells
            text = cell.get_text(strip=True)
            print(f"  [{i}]: '{text}'")
    
    # Look for groups
    all_cells = table.find_all('td')
    test_groups = ["ИС-1-24", "ПГ-1-25", "М-25"]
    for group in test_groups:
        for i, cell in enumerate(all_cells):
            if group == cell.get_text(strip=True):
                print(f"\n✅ Found '{group}' at cell index {i}")
                # Show next 3 cells
                for j in range(i+1, min(i+4, len(all_cells))):
                    print(f"  Next [{j}]: {all_cells[j].get_text(strip=True)[:80]}")
                break
else:
    print("❌ No table with class='border'")
    # Show all tables
    all_tables = soup.find_all('table')
    print(f"Found {len(all_tables)} tables total")

print("\nSaved to working_schedule.html")
