"""
Save HTML for analysis and test parsing.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def save_and_analyze_html():
    """Fetch and save HTML, then analyze structure."""
    print("🔍 Fetching and analyzing schedule HTML\n")
    
    # Get today's schedule
    target_date = datetime.now()
    date_str = target_date.strftime("%Y-%m-%d")
    
    session = requests.Session()
    
    # Step 1: Set date
    save_url = "http://lntrt.ru/save"
    save_params = {"dateSched": date_str, "academicYear": date_str}
    session.get(save_url, params=save_params, timeout=10)
    
    # Step 2: Get schedule
    schedule_url = "http://lntrt.ru/fulltime/daySchedule"
    response = session.get(schedule_url, timeout=10)
    
    # Save HTML
    with open('schedule_full.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("✅ Saved to schedule_full.html")
    
    # Parse and analyze
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Find table
    table = soup.find('table', class_='border')
    if not table:
        print("❌ Table with class='border' not found!")
        # Try other tables
        all_tables = soup.find_all('table')
        print(f"Found {len(all_tables)} tables total")
        for i, t in enumerate(all_tables):
            print(f"  Table {i}: class='{t.get('class')}', id='{t.get('id')}'")
        return
    
    print(f"✅ Found table with class='border'")
    
    # Analyze structure
    rows = table.find_all('tr')
    print(f"📊 Table has {len(rows)} rows\n")
    
    # Look at first few rows
    print("First 3 rows:")
    for i, row in enumerate(rows[:3]):
        cells = row.find_all(['td', 'th'])
        print(f"\n  Row {i}: {len(cells)} cells")
        for j, cell in enumerate(cells[:10]):  # First 10 cells
            text = cell.get_text(strip=True)
            # Check if cell has class 'group'
            cell_class = cell.get('class', [])
            print(f"    Cell {j}: class={cell_class}, text='{text[:40]}'")
    
    # Search for group names
    print("\n" + "=" * 60)
    print("Searching for group names...")
    test_groups = ["ИС-1-24", "ПГ-1-25", "М-25", "СЭН-25"]
    
    all_cells = table.find_all('td')
    for group in test_groups:
        for i, cell in enumerate(all_cells):
            if group in cell.get_text(strip=True):
                print(f"✅ Found '{group}' in cell {i}")
                print(f"   Cell HTML: {str(cell)[:200]}")
                # Show next 5 cells
                print(f"   Next cells:")
                for j in range(i+1, min(i+6, len(all_cells))):
                    text = all_cells[j].get_text(strip=True)
                    print(f"     [{j}]: {text[:60]}")
                break


if __name__ == "__main__":
    save_and_analyze_html()
