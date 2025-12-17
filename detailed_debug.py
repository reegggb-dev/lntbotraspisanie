"""
Detailed debug of the schedule fetch process.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def detailed_fetch_test():
    """Test the exact flow with detailed logging."""
    print("🔍 Detailed Schedule Fetch Test\\n")
    print("=" * 60)
    
    group = "ИС-1-24"
    target_date = datetime.now()
    date_str = target_date.strftime("%Y-%m-%d")
    
    print(f"📅 Target date: {date_str}")
    print(f"📚 Target group: {group}\\n")
    
    # Create session
    session = requests.Session()
    
    # Step 1: Save date
    print("Step 1: Calling /save...")
    save_url = "http://lntrt.ru/save"
    save_params = {"dateSched": date_str, "academicYear": date_str}
    
    try:
        save_response = session.get(save_url, params=save_params, timeout=10)
        print(f"✅ Save response: {save_response.status_code}")
        print(f"   URL: {save_response.url}")
        print(f"   Cookies: {dict(session.cookies)}")
    except Exception as e:
        print(f"❌ Save failed: {e}")
        return
    
    # Step 2: Fetch schedule
    print("\\nStep 2: Calling /fulltime/schedule/daySchedule...")
    schedule_url = "http://lntrt.ru/fulltime/schedule/daySchedule"
    
    try:
        schedule_response = session.get(schedule_url, timeout=10)
        print(f"✅ Schedule response: {schedule_response.status_code}")
        print(f"   URL: {schedule_response.url}")
        print(f"   Content length: {len(schedule_response.content)} bytes")
        
        if schedule_response.status_code != 200:
            print(f"❌ Non-200 response!")
            print(f"   Response text: {schedule_response.text[:200]}")
            return
        
        # Parse HTML
        print("\\nStep 3: Parsing HTML...")
        soup = BeautifulSoup(schedule_response.content, 'lxml')
        
        # Find table
        table = soup.find('table', class_='border')
        print(f"   Table found: {table is not None}")
        
        if table:
            all_cells = table.find_all('td')
            print(f"   Total cells in table: {len(all_cells)}")
            
            # Look for group
            group_found = False
            for i, cell in enumerate(all_cells):
                cell_text = cell.get_text(strip=True)
                if cell_text == group:
                    group_found = True
                    print(f"   ✅ Found group '{group}' at cell index {i}")
                    # Show next few cells
                    print(f"   Next cells:")
                    for j in range(i+1, min(i+6, len(all_cells))):
                        print(f"      [{j}]: {all_cells[j].get_text(strip=True)[:50]}")
                    break
            
            if not group_found:
                print(f"   ❌ Group '{group}' not found in table")
                print(f"   Sample cell texts:")
                for i, cell in enumerate(all_cells[:20]):
                    print(f"      [{i}]: {cell.get_text(strip=True)[:30]}")
        
    except Exception as e:
        print(f"❌ Schedule fetch failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\\n" + "=" * 60)


if __name__ == "__main__":
    detailed_fetch_test()
