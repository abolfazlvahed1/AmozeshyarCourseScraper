from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os



# Initialize WebDriver
driver_path = "chrome/chromedriver.exe"  # Replace with your chromedriver path
service = Service(driver_path)
options = Options()
options.add_argument("--log-level=3")  # Suppress most logs
options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppress USB errors
driver = webdriver.Chrome(service=service, options=options)
directory = "html-pages"

# Create the directory if it does not exist
if not os.path.exists(directory):
    os.makedirs(directory)

def start_after_login():
    try:
        time.sleep(10)
        # Step 1: Navigate to the "جستجوي كلاس درسهای ارائه شده" page
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "menuFrame"))
        )
        class_search_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='برنامه ريزي آموزشي نيمسال تحصيلي']/ancestor::li"))
        )
        class_search_link.click()

        class_search_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='جستجوي كلاس درسهای ارائه شده']/ancestor::a"))
        )
        class_search_link.click()

        print("Clicked on 'جستجوي كلاس درسهای ارائه شده'.")

        # Step 2: Wait for the next page to load (dropdown for row count)
        row_count_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "parameter(rowCount)"))
        )

        # Step 3: Set the number of rows to 100
        select = Select(row_count_dropdown)
        select.select_by_value("100")
        print("Set the number of search results to 100.")

        # Step 4: Click the search button
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submitBtn"))
        )
        search_button.click()
        print("Search button clicked. Waiting for results...")

        # Step 5: Parse the page and extract total records using BeautifulSoup
        page_html = driver.page_source
        soup = BeautifulSoup(page_html, 'html.parser')

        # Find the total records count
        total_records_element = soup.find('span', {'id': 'totalSearchCount'})
        if total_records_element:
            total_records = int(total_records_element.text.strip())
            print(f"Total records: {total_records}")
        else:
            print("Could not find total records. Restarting...")
            raise Exception("Total records not found.")

        # Initialize current page variables
        current_start = 0
        records_per_page = 100
        page_number = 1
        retry_count = 0
        max_retries = 3

        while current_start < total_records:
            try:
                time.sleep(10)
                # Save the current page HTML
                page_html = driver.page_source
                file_name = f"{directory}//offered_courses_page_{page_number}.html"
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(page_html)
                print(f"Saved HTML for page {page_number} as {file_name}")

                # Calculate the next range start
                current_start = page_number * records_per_page
                print(f"Processed records up to: {current_start}")

                # Check if it's the final page
                if current_start >= total_records:
                    print("Reached the final page.")
                    break

                # Click on the "Next" button
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "nextPage"))
                )
                next_button.click()
                print("Clicked 'Next Page' button. Loading next page...")

                # Wait for the next page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'نتايج جستجو')]"))
                )
                page_number += 1
                retry_count = 0  # Reset retry count after a successful iteration

            except Exception as e:
                print(f"An error occurred on page {page_number}: {e}")
                retry_count += 1

                if retry_count <= max_retries:
                    print(f"Retrying page {page_number} ({retry_count}/{max_retries})...")
                    driver.refresh()  # Refresh the page
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'نتايج جستجو')]"))
                    )
                    continue  # Retry the current iteration
                else:
                    print(f"Max retries reached for page {page_number}. Moving to the next page.")
                    retry_count = 0
                    break

    except Exception as e:
        print(f"An error occurred: {e}")
        # Navigate to the main page and restart the process
        print("Navigating to the main page to restart...")
        driver.get("https://eserv.iau.ir/EServices/startAction.do")
        start_after_login()  # Restart the process

try:
    # Step 1: Navigate to the login page
    driver.get("https://eserv.iau.ir/EServices/Pages/acmstd/loginPage.jsp")
    time.sleep(5)

    # Step 2: Perform login
    username_field = driver.find_element(By.ID, "user")
    password_field = driver.find_element(By.ID, "pass")
    captcha_field = driver.find_element(By.NAME, "jcaptcha")
    submit_button = driver.find_element(By.NAME, "B1")

    # Enter credentials
    username_field.send_keys("username")  # Replace with your username
    password_field.send_keys("password")  # Replace with your password
    captcha_value = input("Enter the CAPTCHA value displayed in the browser: ")  # Manually solve CAPTCHA
    captcha_field.send_keys(captcha_value)
    submit_button.click()

    # Step 3: Wait for the confirmation button and click it
    confirm_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "dijit_form_Button_0_label"))
    )
    confirm_button.click()

    # Step 4: Wait for OTP input and submission
    otp_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "OTP"))
    )
    otp_value = input("Enter the OTP received on your phone: ")
    otp_input.send_keys(otp_value)
    submit_otp_button = driver.find_element(By.CSS_SELECTOR, 'input[name="B1"][value^="تایید"]')
    submit_otp_button.click()

    print("Login successful. Starting process after login.")
    start_after_login()

except Exception as e:
    print(f"An error occurred during login: {e}")

finally:
    driver.quit()
