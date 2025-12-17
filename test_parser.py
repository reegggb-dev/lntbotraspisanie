"""
Test script for the schedule parser.
This will test fetching and parsing schedule without running the full bot.
"""

from parser import fetch_schedule, format_schedule, get_date_string


def test_parser():
    """Test the schedule parser with a sample group."""
    print("🧪 Testing Schedule Parser\n")
    print("=" * 50)
    
    # Test date string generation
    today = get_date_string(0)
    tomorrow = get_date_string(1)
    print(f"📅 Today: {today}")
    print(f"📅 Tomorrow: {tomorrow}\n")
    
    # Test fetching schedule for a group
    test_group = "ИС-1-24"
    print(f"📚 Testing schedule fetch for group: {test_group}")
    print("-" * 50)
    
    # Fetch schedule for today
    print("\n⏳ Fetching schedule for today...")
    lessons_today = fetch_schedule(test_group, days_offset=0)
    
    if lessons_today is None:
        print("❌ Failed to fetch schedule (check internet connection or site availability)")
    else:
        print(f"✅ Found {len(lessons_today)} lessons for today")
        schedule_text = format_schedule(lessons_today, test_group, 0)
        print("\n" + schedule_text)
    
    # Fetch schedule for tomorrow
    print("\n" + "=" * 50)
    print("\n⏳ Fetching schedule for tomorrow...")
    lessons_tomorrow = fetch_schedule(test_group, days_offset=1)
    
    if lessons_tomorrow is None:
        print("❌ Failed to fetch schedule")
    else:
        print(f"✅ Found {len(lessons_tomorrow)} lessons for tomorrow")
        schedule_text = format_schedule(lessons_tomorrow, test_group, 1)
        print("\n" + schedule_text)
    
    print("\n" + "=" * 50)
    print("✅ Parser test completed!")


if __name__ == "__main__":
    test_parser()
