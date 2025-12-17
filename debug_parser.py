"""
Debug script to analyze the HTML structure of the schedule page.
"""

import requests
from bs4 import BeautifulSoup


def debug_schedule_page():
    """Debug the schedule page structure."""
    print("🔍 Debugging Schedule Page\n")
    print("=" * 50)
    
    url = "http://lntrt.ru/fulltime/daySchedule"
    
    try:
        print(f"📡 Fetching: {url}")
        response = requests.get(url, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"\n📊 Found {len(tables)} tables")
        
        # Look for table with class 'border'
        border_table = soup.find('table', class_='border')
        print(f"🎯 Table with class 'border': {'Found' if border_table else 'Not found'}")
        
        if border_table:
            # Get first few rows to see structure
            rows = border_table.find_all('tr')[:5]
            print(f"\n📋 First {len(rows)} rows:")
            for i, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                print(f"\nRow {i}: {len(cells)} cells")
                for j, cell in enumerate(cells[:5]):  # First 5 cells
                    text = cell.get_text(strip=True)[:50]  # First 50 chars
                    print(f"  Cell {j}: {text}")
        
        # Look for group names
        print("\n" + "=" * 50)
        print("🔍 Searching for group names...")
        all_text = soup.get_text()
        test_groups = ["ИС-1-24", "ПГ-1-25", "М-25"]
        for group in test_groups:
            if group in all_text:
                print(f"✅ Found: {group}")
            else:
                print(f"❌ Not found: {group}")
        
        # Save HTML to file for inspection
        with open('debug_schedule.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("\n💾 Saved HTML to debug_schedule.html")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Debug completed!")


if __name__ == "__main__":
    debug_schedule_page()
