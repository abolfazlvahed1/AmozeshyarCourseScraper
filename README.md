# AmozeshyarCourseScraper

## Requirements
- Python 3.x
- Selenium
- BeautifulSoup
- ChromeDriver (compatible version)
- Google Chrome (compatible version)

## Prerequisites
1. Clone this repository:
 ```sh
git clone https://github.com/abolfazlvahed1/AmozeshyarCourseScraper.git
```
2. Install the required Python packages:
To install BeautifulSoup and Selenium, you need pip. If you don't have pip installed, you can install it using:
```sh
python -m ensurepip --upgrade
```

Once pip is installed, you can install the required packages:
```sh
pip install beautifulsoup4 selenium
```

3. ChromeDriver:
This repository includes the compatible ChromeDriver version for Google Chrome (v114). No additional setup is required for ChromeDriver. Simply ensure that the `chrome/chromedriver.exe` is in the same directory as the script.

If you need a different version of ChromeDriver, you can download it from the official website:
[Download ChromeDriver](https://sites.google.com/chromium.org/driver/downloads)

Make sure the version of ChromeDriver matches the version of Chrome installed on your system.

4. Google Chrome:
For this script to work, you need a version of Google Chrome that is compatible with the included ChromeDriver. 
If you want to use the included ChromeDriver (v114), please ensure you install Google Chrome v114. You can download it from the following link:
[Download Google Chrome v114](https://www.filepuma.com/download/google_chrome_64bit_114.0.5735.199-35569/)
Make sure to match the version of Google Chrome with the version of ChromeDriver provided in the repository for optimal compatibility.

## Usage
1. Update the login credentials (username, password) in the script:
```python
# Enter credentials
    username_field.send_keys("username")  # Replace with your username
    password_field.send_keys("password")  # Replace with your password
```
2. Run the script:
```sh
python /path/to/script.py
```

During the process, Google Chrome will open, and you'll be asked to enter the CAPTCHA. After solving it, you'll be prompted for the IGAP code. Once completed, the script will download all the offered course data.

## Notes
- Ensure you manually solve the CAPTCHA during the login process.
- This script uses a basic retry mechanism for failed page loads (max 3 retries per page).
- To prevent your IP from being blocked, I have added delays between requests for security purposes.
