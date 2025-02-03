# indico2csv

This script is designed to extract event and contribution details from conference agendas hosted on platforms like **INFN's Indico agenda** and save them into a structured CSV file.

## Features
- Automatically navigates through the current event and linked older events.
- Extracts:
  - Event title
  - Agenda URL
  - Event date
  - Contribution titles
  - Speaker names
  - Institutions
  - Associated PDF attachments (if available)
- Saves the extracted information to a CSV file for further analysis.

---

## Requirements
To run this script, you need:

1. **Python 3.7 or higher**
2. **Dependencies**:
    - `selenium`
    - `webdriver-manager`
    - `beautifulsoup4`

### Install dependencies:
```bash
pip install selenium webdriver-manager beautifulsoup4
```

---

## How It Works

1. **Starting URL:** The script begins by accessing the initial event page provided by the `start_url` variable.
2. **Data Extraction:** It extracts event and contribution details using Selenium to dynamically load pages and BeautifulSoup to parse the content.
3. **Recursive Navigation:** If "older event" links are found, it automatically navigates and scrapes details from them.
4. **Data Storage:** All data is saved into a CSV file named `events_contributions.csv`.

---

## File Structure of Output CSV
The CSV contains the following columns:
| Meeting Title | Agenda URL | Date       | Contribution Title | Speaker | Institution | PDF Link |
| ------------- | ---------- | ---------- | ------------------ | ------- | ----------- | -------- |
| Event name    | Event link | Date/time  | Contribution name  | Speaker | Institution | PDF link |

---

## Script Execution
To run the script, execute the following command:
```bash
python indico2csv.py
```

The script will automatically open a browser, extract the data, and save it to the file.

---

## Customization Options
- **Change Start URL:** Update the `start_url` variable with the URL of the event you want to scrape.
- **Output File:** Change the filename in the `save_to_csv()` function if a different CSV name is desired.

---

## Error Handling
- The script includes basic error handling to catch any issues during scraping. If an error occurs, it will print the error message and close the browser.

---

## Example Output
| Meeting Title                  | Agenda URL                                         | Date       | Contribution Title                 | Speaker      | Institution                           | PDF Link                                                                                          |
| ------------------------------ | ------------------------------------------------- | ---------- | ---------------------------------- | -------------| ------------------------------------- | ----------------------------------------------------------------------------------------------- |
| CYGNO Collaboration Meeting 2024 | https://agenda.infn.it/event/43515/                | 2024-11-27 | Detector simulation and digitization | Pietro Meloni | Istituto Nazionale di Fisica Nucleare | https://agenda.infn.it/event/43515/contributions/249944/attachments/128808/191057/Detector%20Simulation%20-%20Digitization%20-%202.pdf |

---

## Notes
- The script is specifically designed for websites with a structure similar to INFN's Indico agenda system. If needed for other sites, minor adjustments to the selectors may be required.
