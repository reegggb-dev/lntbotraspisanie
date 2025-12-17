def parse_nested_lesson_table(nested_table):
    """
    Parse a nested lesson table to extract lesson information.
    
    Each nested table represents one lesson period and contains:
    - Roman numeral in <th> (I, II, III, etc.)
    - Subject name, room number, and teacher in <td>
    
    Args:
        nested_table: BeautifulSoup table element
    
    Returns:
        Dict with lesson details or None
    """
    import re
    
    # Extract lesson number from th
    th = nested_table.find('th')
    lesson_number = th.get_text(strip=True) if th else ""
    
    # Extract full text from the table
    full_text = nested_table.get_text(' ', strip=True)
    
    # Skip empty/"no lesson" entries
    if 'нет (нет) нет' in full_text or 'нет нет нет' in full_text:
        return None
    
    # Extract subject, room, teacher
    # Pattern: Subject (Room) Teacher or Subject (№Room) Teacher
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
    
    # Clean up HTML tags if any
    from bs4 import BeautifulSoup
    if '\u003c' in subject:
        subject = BeautifulSoup(subject, 'lxml').get_text()
    if '\u003c' in teacher:
        teacher = BeautifulSoup(teacher, 'lxml').get_text()
    
    return {
        "number": lesson_number,
        "subject": subject,
        "room": room,
        "teacher": teacher
    }
