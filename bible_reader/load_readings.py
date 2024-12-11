""" This is used to transfer the reading_plan.yaml contents from to app.db/McheynePlan"""
import yaml
import sqlite3
from datetime import datetime

# Connect to the database
conn = sqlite3.connect("app.db")
cursor = conn.cursor()


# Function to process chapters and verses
def parse_chapters(chapters):
    processed_chapters = []
    for chapter_info in chapters:
        try:
            # Handle chapter range (e.g., "3-4")
            if '-' in chapter_info:
                start_chapter, end_chapter = chapter_info.split('-')
                start_chapter_num = int(start_chapter.split(':')[0])
            else:
                chapter_num, verse_info = chapter_info.split(':')
                start_chapter_num = int(chapter_num)
                verse_parts = verse_info.split('-')
                start_verse = int(verse_parts[0])
                end_verse = int(verse_parts[1]) if len(verse_parts) > 1 else start_verse

                # Handle the case where only one verse is provided
                if len(verse_parts) == 1:
                    start_verse = int(verse_parts[0])
                    end_verse = start_verse  # Single verse (same start and end)
                elif len(verse_parts) == 2:
                    start_verse = int(verse_parts[0])
                    end_verse = int(verse_parts[1])
                else:
                    # Invalid verse range, mark as "AMEND"
                    start_verse = "CHECK"
                    end_verse = "CHECK"
        except (ValueError, IndexError) as e:
            # If there is an error (e.g., invalid chapter or verse format), mark as "AMEND"
            print(f"Error processing chapter/verse: {chapter_info} - {e}")
            start_chapter_num = "CHECK"
            start_verse = "CHECK"
            end_verse = "CHECK"

        # Append the processed chapter to the list
        processed_chapters.append({
            'chapter': start_chapter_num,
            'start_verse': start_verse,
            'end_verse': end_verse
        })
    return processed_chapters

# Load YAML data
with open("reading_plan.yaml", "r") as file:
    reading_data = yaml.safe_load(file)

# Insert data into the database
for entry in reading_data:
    # Ensure the 'chapters' key exists
    if 'chapters' in entry:
        chapters_1 = parse_chapters([entry['chapters'][0]])
        chapters_2 = parse_chapters([entry['chapters'][1]])
        chapters_3 = parse_chapters([entry['chapters'][2]])
        chapters_4 = parse_chapters([entry['chapters'][3]])
    else:
        print(f"Missing chapters data for entry: {entry}")
        continue

    # Ensure the date is parsed correctly
    try:
        day = int(entry['day'])
        date_str = f"{day} {entry['month']} {datetime.now().year}"
        date = datetime.strptime(date_str, "%d %B %Y").date()  # Use .date() to avoid time component
    except ValueError as e:
        print(f"Error parsing date for entry {entry['day']} {entry['month']}: {e}")
        continue  # Skip this entry if the date format is incorrect

    # Insert into the database
    cursor.execute("""
        INSERT INTO McheynePlan (day, month, book_1, chapter_1, start_verse_1, end_verse_1,
            book_2, chapter_2, start_verse_2, end_verse_2,
            book_3, chapter_3, start_verse_3, end_verse_3,
            book_4, chapter_4, start_verse_4, end_verse_4, translation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(entry['day']), # Convert day to string
        entry['month'],
        chapters_1[0]['chapter'], chapters_1[0]['start_verse'], chapters_1[0]['end_verse'],
        chapters_2[0]['chapter'], chapters_2[0]['start_verse'], chapters_2[0]['end_verse'],
        chapters_3[0]['chapter'], chapters_3[0]['start_verse'], chapters_3[0]['end_verse'],
        chapters_4[0]['chapter'], chapters_4[0]['start_verse'], chapters_4[0]['end_verse'],
        'KJV'  # Default translation
    ))

# Commit the changes and close the connection
conn.commit()
conn.close()
