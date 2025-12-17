import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import SCHEDULE_URL


def get_date_string(days_offset: int = 0) -> str:
    """
    Get date string in DD/MM/YYYY format.
    
    Args:
        days_offset: Number of days from today (0 = today, 1 = tomorrow)
    
    Returns:
        Date string in DD/MM/YYYY format
    """
    date = datetime.now() + timedelta(days=days_offset)
    return date.strftime("%d/%m/%Y")


def fetch_schedule(group: str, days_offset: int = 0) -> Optional[List[Dict[str, str]]]:
    """
    Fetch and parse schedule for a specific group.
    
    Args:
        group: Group name (e.g., "ИС-1-24")
        days_offset: Number of days from today (0 = today, 1 = tomorrow)
    
    Returns:
        List of lessons with details or None if error
    """
    try:
        # Calculate the target date
        target_date = datetime.now() + timedelta(days=days_offset)
        date_str = target_date.strftime("%Y-%m-%d")  # YYYY-MM-DD format for API
        
        # Create a session to maintain cookies
        session = requests.Session()
        
        # Required header for AJAX requests
        headers = {"X-Requested-With": "XMLHttpRequest"}
        
        # Step 1: Set the date in session
        save_url = "http://lntrt.ru/save"
        save_params = {
            "dateSched": date_str,
            "academicYear": date_str
        }
        save_response = session.get(save_url, params=save_params, headers=headers, timeout=10)
        save_response.raise_for_status()
        
        # Step 2: Fetch the schedule HTML  
        schedule_url = "http://lntrt.ru/schedule/daySchedule"  # Note: /schedule not /fulltime/schedule
        schedule_response = session.get(schedule_url, headers=headers, timeout=10)
        # Site returns schedule data successfully with the AJAX header
        
        # Parse HTML
        soup = BeautifulSoup(schedule_response.content, 'lxml')
        
        # Find the schedule table
        table = soup.find('table', class_='border')
        if not table:
            return None
        
        # Parse schedule for the specific group
        lessons = parse_schedule_html(table, group)
        return lessons
        
    except requests.RequestException as e:
        print(f"Error fetching schedule: {e}")
        return None
    except Exception as e:
        print(f"Error parsing schedule: {e}")
        return None


def parse_schedule_html(table, group: str) -> List[Dict[str, str]]:
    """
    Parse HTML table to extract schedule for a specific group.
    
    The schedule table has groups as column headers (<th>), 
    with lessons stored in nested tables within the <td> cells below each group header.
    
    Args:
        table: BeautifulSoup table element
        group: Group name to find
    
    Returns:
        List of lessons with number, subject, room, and teacher
    """
    lessons = []
    
    # Find all rows
    rows = table.find_all('tr')
    
    # Find the column index for our group
    group_column_index = None
    
    for row in rows:
        # Check headers in this row
        headers = row.find_all('th')
        for idx, th in enumerate(headers):
            if th.get_text(strip=True) == group:
                group_column_index = idx
                print(f"Found group '{group}' in column {idx}")
                break
        
        if group_column_index is not None:
            break
    
    if group_column_index is None:
        print(f"Group '{group}' not found in table headers")
        return []
    
    # Now find the row with lessons for this group
    # It should be the next row after the header row
    found_header_row = False
    for row in rows:
        # Check if this row has our group header
        headers = row.find_all('th')
        for th in headers:
            if th.get_text(strip=True) == group:
                found_header_row = True
                break
        
        # If we found the header row, get the next tr with td cells
        if found_header_row:
            # Get the next row's cells
            next_row = row.find_next_sibling('tr')
            if next_row:
                cells = next_row.find_all('td', recursive=False)
                if len(cells) > group_column_index:
                    # This is our group's schedule cell
                    group_cell = cells[group_column_index]
                    
                    # Parse nested tables in this cell
                    nested_tables = group_cell.find_all('table')
                    for nested_table in nested_tables:
                        lesson_info = parse_nested_lesson_table(nested_table)
                        lessons.append(lesson_info)
            break
    
    return lessons


def parse_nested_lesson_table(nested_table):
    """
    Parse a nested lesson table to extract lesson information.
    
    Each nested table represents one lesson period and contains:
    - Roman numeral in <th> (I, II, III, etc.)
    - Subject name, room number, and teacher in <td>
    
    Args:
        nested_table: BeautifulSoup table element
    
    Returns:
        Dict with lesson details (never None, returns 'Пары нет' for empty lessons)
    """
    import re
    
    # Extract lesson number from th
    th = nested_table.find('th')
    lesson_number = th.get_text(strip=True) if th else ""
    
    # Extract full text from the table
    full_text = nested_table.get_text(' ', strip=True)
    
    # Check if this is an empty/"no lesson" entry
    if 'нет (нет) нет' in full_text or 'нет нет нет' in full_text:
        return {
            "number": lesson_number,
            "subject": "Пары нет",
            "room": "",
            "teacher": ""
        }
    
    # Extract subject, room, teacher
    subject = ""
    room = ""
    teacher = ""
    
    # Find all td cells
    tds = nested_table.find_all('td')
    for td in tds:
        text = td.get_text(' ', strip=True)
        
        # Skip "1п/гр" and "2п/гр" cells
        if 'п/гр' in text or not text:
            continue
        
        # Try to parse: Subject (Room) Teacher
        room_match = re.search(r'\((.*?)\)', text)
        if room_match:
            room = room_match.group(1)
            # Split by parentheses to get subject and teacher
            parts = re.split(r'\([^)]+\)', text)
            if len(parts) >= 1:
                subject = parts[0].strip()
            if len(parts) >= 2:
                teacher = parts[1].strip()
        else:
            # No room found, might be just subject or subject+teacher
            subject = text
            teacher = ""
    
    return {
        "number": lesson_number,
        "subject": subject if subject else "Пары нет",
        "room": room,
        "teacher": teacher
    }


def parse_lesson_entry(text: str) -> Optional[Dict[str, str]]:
    """
    Parse a single lesson entry.
    
    Args:
        text: Lesson text (e.g., "I История (№22) Сафиюллина Г.М.")
    
    Returns:
        Dict with lesson details or None
    """
    text = text.strip()
    if not text or text == "нет (нет) нет":
        return None
    
    # Try to extract components
    import re
    
    # Pattern: Roman numeral, subject, (room), teacher
    # Example: "I История (№22) Сафиюллина Г.М."
    
    # Roman numerals at the start
    roman_pattern = r'^(I{1,3}|IV|V|VI{0,3}|IX|X)\s+'
    match = re.match(roman_pattern, text)
    
    lesson_number = ""
    remaining = text
    
    if match:
        lesson_number = match.group(1)
        remaining = text[match.end():]
    
    # Try to find room in parentheses
    room_pattern = r'\((.*?)\)'
    room_match = re.search(room_pattern, remaining)
    
    room = ""
    if room_match:
        room = room_match.group(1)
        # Split by room to get subject and teacher
        parts = remaining.split(f'({room})')
        subject = parts[0].strip() if len(parts) > 0 else ""
        teacher = parts[1].strip() if len(parts) > 1 else ""
    else:
        # No room found, just split by newlines or spaces
        subject = remaining
        teacher = ""
    
    return {
        "number": lesson_number,
        "subject": subject,
        "room": room,
        "teacher": teacher,
        "raw": text
    }


def format_schedule(lessons: List[Dict[str, str]], group: str, days_offset: int = 0) -> str:
    """
    Format schedule into a readable message.
    
    Args:
        lessons: List of lesson dictionaries
        group: Group name
        days_offset: 0 for today, 1 for tomorrow
    
    Returns:
        Formatted schedule string
    """
    date_str = get_date_string(days_offset)
    day_name = "сегодня" if days_offset == 0 else "завтра"
    
    if not lessons:
        return f"📅 Расписание для группы {group} на {day_name} ({date_str}):\n\n❌ Занятий нет"
    
    message = f"📅 Расписание для группы {group} на {day_name} ({date_str}):\n\n"
    
    for i, lesson in enumerate(lessons, 1):
        number = lesson.get('number', str(i))
        subject = lesson.get('subject', 'Не указано')
        room = lesson.get('room', '')
        teacher = lesson.get('teacher', '')
        
        if subject == "Пары нет":
            # For empty lessons, just show the number and "Пары нет"
            message += f"{number}. ❌ Пары нет\n\n"
        else:
            # For regular lessons, show full info
            message += f"{number}. {subject}\n"
            if room:
                message += f"   🚪 Аудитория: {room}\n"
            if teacher:
                message += f"   👨‍🏫 Преподаватель: {teacher}\n"
            message += "\n"
    
    return message.strip()
