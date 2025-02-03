from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re

# ---------------------------------------------------------------
# Helper function to remove parentheses and everything inside them
# ---------------------------------------------------------------
def remove_parentheses_content(text):
    """
    Removes any parentheses and the text inside them from the given string.
    Example: "John Doe(ABC)" -> "John Doe".
    """
    return re.sub(r"\(.*?\)", "", text).strip()

# ---------------------------------------------------------------
# Helper function to parse and standardize the date/time string
# ---------------------------------------------------------------
def format_date(date_str):
    """
    Attempts to parse the date string from Indico and returns
    a standardized format: 'YYYY-MM-DD HH:MM'.
    If parsing fails, returns the whitespace-trimmed string.
    """
    # Remove extra tabs/spaces
    date_str_cleaned = " ".join(date_str.split())
    
    # Possible date/time formats to try
    date_formats = [
        "%A %b %d, %Y, %I:%M %p",  # e.g. "Thursday Sep 26, 2024, 2:00 PM"
        "%b %d, %Y, %I:%M %p"      # e.g. "Sep 19, 2024, 10:30 AM"
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str_cleaned, fmt)
            return dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            pass
    
    # If no format matches, return the cleaned version
    return date_str_cleaned

# ---------------------------------------------------------------
# Main function to parse the events and contributions
# ---------------------------------------------------------------
def parse_events_and_contributions(driver):
    """
    Navigates through the current event and any 'older event' links,
    extracting all contributions and returning them in a list.
    """
    all_contributions = []
    
    while True:
        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract the page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Current event URL
        current_event_url = driver.current_url
        
        # Extract event title (if missing, set to empty or placeholder)
        title_element = soup.find('h1', itemprop='name')
        if title_element:
            event_title = title_element.get_text(strip=True)
        else:
            event_title = ""
        
        # Extract event date (if missing, set to empty)
        date_element = soup.find('time', itemprop='startDate')
        if date_element:
            event_date = format_date(date_element.get_text(strip=True))
        else:
            event_date = ""
        
        # Find all timetable items (contributions)
        timetable_entries = soup.find_all('li', class_='timetable-item timetable-contrib')
        
        # If there are no contributions, still store the event info with blank fields
        if not timetable_entries:
            all_contributions.append((
                event_title,
                current_event_url,
                event_date,
                "",  # Contribution
                "",  # Speaker
                "",  # Institution
                ""   # PDF
            ))
        else:
            # Parse each timetable entry
            for entry in timetable_entries:
                # Contribution title
                ctitle_elt = entry.find('span', class_='timetable-title')
                if ctitle_elt:
                    contribution_title = ctitle_elt.get_text(strip=True).replace("¶", "")
                else:
                    contribution_title = ""
                
                # Extract speaker and institution
                speaker_element = entry.find('div', class_='speaker-list')
                speaker = "N/A"
                institution = "N/A"
                
                if speaker_element:
                    # Typically the second span has the speaker's name
                    speaker_spans = speaker_element.find_all('span')
                    if len(speaker_spans) > 1:
                        raw_speaker = speaker_spans[1].get_text(strip=True)
                        # Remove parentheses text from speaker name
                        speaker = remove_parentheses_content(raw_speaker)
                    
                    # Extract the institution from <span class="affiliation"> if available
                    institution_element = speaker_element.find('span', class_='affiliation')
                    if institution_element:
                        raw_institution = institution_element.get_text(strip=True)
                        # Remove parentheses around the institution
                        institution = raw_institution.replace("(", "").replace(")", "")
                
                # Check for a PDF link
                pdf_element = entry.find('div', class_='js-attachment-container')
                pdf_link = "no PDF"
                if pdf_element:
                    pdf_anchor = pdf_element.find('a', href=True)
                    if pdf_anchor and pdf_anchor['href'].endswith('.pdf'):
                        pdf_link = 'https://agenda.infn.it' + pdf_anchor['href']
                
                # Append to the master list
                # Order: Meeting, Agenda, Date, Contribution, Speaker, Institution, PDF
                all_contributions.append((
                    event_title,
                    current_event_url,
                    event_date,
                    contribution_title,
                    speaker,
                    institution,
                    pdf_link
                ))
        
        # Find the "older event" link
        older_event_link = soup.find('a', class_='icon-prev', href=True)
        if older_event_link:
            next_event_url = 'https://agenda.infn.it' + older_event_link['href']
            driver.get(next_event_url)
        else:
            # No older events found, break the loop
            break
    
    return all_contributions

# ---------------------------------------------------------------
# Function to save data to CSV with the new header
# ---------------------------------------------------------------
def save_to_csv(contributions, filename="events_contributions.csv"):
    """
    Saves the list of contributions into a CSV file.
    """
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write the new header
        writer.writerow(["Meeting", "Agenda", "Date", "Contribution", "Speaker", "Institution", "PDF"])
        
        for contrib in contributions:
            writer.writerow(contrib)
    
    print(f"\nData successfully saved to file: {filename}")

# ---------------------------------------------------------------
# Main script execution
# ---------------------------------------------------------------
if __name__ == "__main__":
    # Starting URL
    start_url = "https://agenda.infn.it/event/44949/"
    
    # Set up Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        # Go to the initial event
        driver.get(start_url)
        
        # Parse all events (the current one and any older ones)
        contributions_list = parse_events_and_contributions(driver)
        
        # Save the results to CSV
        save_to_csv(contributions_list, "events_contributions.csv")
    
    except Exception as e:
        print("An error occurred during extraction:", e)
    finally:
        driver.quit()
