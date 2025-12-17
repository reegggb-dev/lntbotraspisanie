"""
Test different API endpoints to find the working one.
"""

import requests

def test_endpoints():
    """Test various possible endpoints."""
    endpoints = [
        "http://lntrt.ru/schedule/daySchedule",
        "http://lntrt.ru/fulltime/schedule/daySchedule",
        "http://lntrt.ru/fulltime/daySchedule",  # Original page URL path
        "http://lntrt.ru/fulltime/schedule",
    ]
    
    date =  "2025-12-17"
    
    print("Testing endpoints...\n")
    print("=" * 60)
    
    for url in endpoints:
        session = requests.Session()
        
        try:
            # First set the date
            save_url = "http://lntrt.ru/save"
            save_response = session.get(save_url, params={"dateSched": date, "academicYear": date}, timeout=10)
            
            # Then try the endpoint
            response = session.get(url, timeout=10)
            print(f"\n✅ {url}")
            print(f"   Status: {response.status_code}")
            print(f"   Length: {len(response.content)} bytes")
            
            # Check if response contains schedule data
            if b"group" in response.content or b"\xd0\xa0\xd0\xb0\xd1\x81\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5" in response.content:
                print("   ✅ Contains schedule data!")
            
        except requests.HTTPError as e:
            print(f"\n❌ {url}")
            print(f"   Error: {e.response.status_code}")
        except Exception as e:
            print(f"\n❌ {url}")
            print(f"   Error: {type(e).__name__}: {str(e)[:50]}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_endpoints()
