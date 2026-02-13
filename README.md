# AmozeshyarCourseScraper

A Python web scraper for extracting course data from the Islamic Azad University (IAU) e-services portal (Amozeshyar). This tool automatically navigates through course listings, handles pagination, and saves course data for multiple academic groups and general education courses.

## Features

- ✅ Automated login and navigation through IAU e-services
- ✅ Scrapes course data for multiple academic groups
- ✅ Handles general education (Omomi) courses separately
- ✅ Automatic pagination handling (up to 100 records per page)
- ✅ Built-in delays to prevent IP blocking
- ✅ Robust error handling and retry mechanisms
- ✅ Progress tracking with detailed console output
- ✅ Saves results as HTML files for later processing

## Requirements

- Python 3.x
- Selenium
- BeautifulSoup4
- ChromeDriver (automatically managed by Selenium 4.6+)
- Google Chrome browser

## Installation

### 1. Clone the Repository

```sh
git clone https://github.com/abolfazlvahed1/AmozeshyarCourseScraper.git
cd AmozeshyarCourseScraper
```

### 2. Install Python Dependencies

First, ensure you have pip installed:

```sh
python -m ensurepip --upgrade
```

Then install the required packages:

```sh
pip install beautifulsoup4 selenium
```

**Note:** If you're using Selenium 4.6 or later, ChromeDriver will be automatically managed. No manual ChromeDriver installation is needed!

### 3. Browser Setup

#### Option 1: Automatic ChromeDriver Management (Recommended)

If you're using **Selenium 4.6+**, ChromeDriver will be downloaded and managed automatically. Just ensure you have Google Chrome installed:

- Download the latest Google Chrome from: https://www.google.com/chrome/

#### Option 2: Manual ChromeDriver Setup (Legacy)

If you're using an older version of Selenium or prefer manual setup:

1. Download ChromeDriver matching your Chrome version: https://sites.google.com/chromium.org/driver/downloads
2. Place `chromedriver.exe` in the `chrome/` directory
3. Ensure ChromeDriver version matches your installed Chrome version

**For Chrome v114 users:** Download from https://www.filepuma.com/download/google_chrome_64bit_114.0.5735.199-35569/

## Configuration

Edit the script to configure which groups and courses to scrape:

```python
# Normal academic groups to scrape
GROUP_CODES = [
    "2110130", "2114199", "2157719", "2123818", "2125299",
    "2110153", "2157799", "2115799", "2111399", "2155999",
    "2110143", "2123845", "2111510180", "2123819", "2123899"
]

# General education (Omomi) course codes
OMOMI_COURSE_CODES = [
    90763, 98961, 92381, 99073, 98841, 90610, 90029, 90755,
    99090, 99093, 99091, 99092, 99041, 90128, 90180,
    99083, 90881, 99062, 99079
]
```

## Usage

### Basic Usage

Run the script:

```sh
python scraper_final.py
```

### Step-by-Step Process

1. **Script starts** - Chrome browser will open automatically
2. **Manual login required** - Log into your Amozeshyar portal
3. **Solve CAPTCHA** - Complete the CAPTCHA challenge
4. **Press Enter** - Return to the console and press Enter to continue
5. **Automated scraping** - The script will automatically:
   - Navigate to the course search page
   - Process all configured academic groups
   - Process all general education courses
   - Save HTML files for each page of results

### Output

All scraped data is saved in the `html-pages/` directory:

```
html-pages/
├── 2110130_page_1.html
├── 2110130_page_2.html
├── 2110130_page_3.html
├── omomi_90763_page_1.html
├── omomi_98961_page_1.html
└── ...
```

**File naming convention:**
- Normal groups: `{GROUP_CODE}_page_{PAGE_NUMBER}.html`
- Omomi courses: `omomi_{COURSE_CODE}_page_{PAGE_NUMBER}.html`

## How It Works

### 1. Normal Academic Groups
For each group code in `GROUP_CODES`:
- Filters by group code only
- Searches for all courses in that group
- Saves all paginated results

### 2. General Education (Omomi) Courses
For each course code in `OMOMI_COURSE_CODES`:
- Filters by course code only (no group filter)
- Searches across all groups offering that course
- Saves all paginated results

### 3. Pagination Handling
- Detects total number of records
- Calculates total pages (100 records per page)
- Automatically navigates through all pages
- Saves each page as separate HTML file

## Performance & Safety

### Built-in Delays
To prevent IP blocking and ensure reliable scraping:
- **2 seconds** after clicking search
- **2 seconds** before scraping each page
- **2 seconds** after clicking next page
- **3 seconds** between processing groups/courses

The script may take some time to complete. Please be patient and let it run without interruption.

## Troubleshooting

### "Could not find correct iframe"
This warning is normal and doesn't affect functionality. The script successfully navigates despite this message.

### Script only saves page 1
Ensure you're running the latest version (`scraper_final.py`). The older versions had pagination bugs.

### ChromeDriver version mismatch
```
SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version X
```

**Solution:** 
- Update to Selenium 4.6+ for automatic driver management, OR
- Download matching ChromeDriver from https://chromedriver.chromium.org/

### Connection timeout
If the script times out:
- Check your internet connection
- Verify IAU e-services is accessible
- Try increasing wait times in the script

### IP blocked / Rate limited
If you suspect you've been rate-limited:
- Wait 30-60 minutes before retrying
- Increase delay values in the script
- Reduce the number of groups/courses being scraped

## Technical Details

### Technologies Used
- **Selenium WebDriver**: Browser automation
- **BeautifulSoup4**: HTML parsing
- **Python time/math**: Delay and calculation utilities

### Key Functions
- `switch_to_content()`: Handles iframe navigation
- `apply_filters_and_search()`: Applies search filters and submits
- `save_all_pages_by_total()`: Pagination and data saving logic
- `process_group()`: Processes normal academic groups
- `process_omomi_course()`: Processes general education courses

## Notes & Best Practices

- ✅ **Manual login required**: The script cannot automate the CAPTCHA, you must log in manually
- ✅ **Don't interrupt**: Let the script complete without interruption for best results
- ✅ **Monitor console output**: Check for errors or warnings during execution
- ✅ **Delays are intentional**: Built-in delays prevent IP blocking - don't remove them
- ✅ **Check output files**: Verify HTML files are being created in `html-pages/` directory
- ⚠️ **Respect the server**: Don't modify delays to be more aggressive
- ⚠️ **Keep Chrome updated**: Use a recent version of Chrome for best compatibility

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is intended for educational and personal use only. Please respect the Islamic Azad University's terms of service and use this tool responsibly. The authors are not responsible for any misuse of this software.

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Ensure all requirements are properly installed
3. Verify your Chrome and ChromeDriver versions match
4. Open an issue on GitHub with detailed error messages

---

**Last Updated:** February 2026
**Maintained by:** Abolfazl Vahed