from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import time
import math

# ---------------- CONFIG ---------------- #

URL_LOGIN = "https://eserv.iau.ir/EServices/Pages/acmstd/loginPage.jsp"
URL_START = "https://eserv.iau.ir/EServices/startAction.do"

SAVE_DIR = "html-pages"

# Other group code: "2114199", "2157719", "2123818", "2125299",
#   "2110153", "2157799", "2115799", "2111399", "2155999",
#   "2110143", "2123845", "2111510180", "2123819", "2123899"

GROUP_CODES = [
    "2110130" # Computer group code 
]

OMOMI_GROUP = "2110199"

OMOMI_COURSE_CODES = [
    90763, 98961, 92381, 99073, 98841, 90610, 90029, 90755,
    99090, 99093, 99091, 99092, 99041, 90128, 90180,
    99083, 90881, 99062, 99079
]

# ---------------------------------------- #

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

options = Options()
options.add_argument("--log-level=3")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)


# ---------------- FRAME HELPERS ---------------- #

def switch_to_menu():
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "menuFrame")))


def switch_to_content():
    driver.switch_to.default_content()

    # wait a bit for page to settle
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    # try multiple iframe strategies
    iframes = driver.find_elements(By.TAG_NAME, "iframe")

    if not iframes:
        print("⚠ No iframe found. Content may already be in main page.")
        return

    for iframe in iframes:
        try:
            driver.switch_to.frame(iframe)

            # check if table or form exists inside
            if driver.find_elements(By.NAME, "parameter(f^groupCode)"):
                print("✔ Switched to correct iframe")
                return
            driver.switch_to.default_content()
        except:
            driver.switch_to.default_content()

    print("⚠ Could not find correct iframe")


# ---------------- NAVIGATION ---------------- #

def open_search_page():
    switch_to_menu()

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[text()='برنامه ريزي آموزشي نيمسال تحصيلي']/ancestor::li")
        )
    ).click()

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[text()='جستجوي كلاس درسهای ارائه شده']/ancestor::a")
        )
    ).click()

    switch_to_content()


# ---------------- SEARCH & SCRAPE ---------------- #

def apply_filters_and_search(group_code=None, course_code=None):
    """Apply search filters and click search button"""
    wait.until(
        EC.presence_of_element_located((By.NAME, "parameter(f^groupCode)"))
    )

    # Set group code
    group_field = driver.find_element(By.NAME, "parameter(f^groupCode)")
    group_field.clear()
    if group_code:
        group_field.send_keys(group_code)
    
    # Set course code
    course_field = driver.find_element(By.NAME, "parameter(f^courseCode)")
    course_field.clear()
    if course_code:
        course_field.send_keys(course_code)

    # Set rows per page = 100
    Select(driver.find_element(By.NAME, "parameter(rowCount)")).select_by_value("100")
    time.sleep(1)  # Small delay after setting dropdown

    # Click search button
    search_btn = wait.until(EC.element_to_be_clickable((By.ID, "submitBtn")))
    search_btn.click()
    
    # Wait for results to load
    wait.until(EC.presence_of_element_located((By.ID, "tableContainer")))
    time.sleep(2)  # Extra wait to ensure page fully loads


def save_all_pages_by_total(file_prefix):
    """
    Save all pages based on total record count
    This is the ORIGINAL WORKING LOGIC from your first version
    """
    # Get total records from the page
    soup = BeautifulSoup(driver.page_source, "html.parser")
    total_element = soup.find("span", {"id": "totalSearchCount"})
    
    if not total_element:
        print("⚠ No results element found")
        return
    
    total_records = int(total_element.text.strip())
    print(f"📊 Total records: {total_records}")
    
    if total_records == 0:
        # Still save the empty page
        table = soup.find("div", {"id": "tableContainer", "class": "datagrid"})
        if table:
            filename = f"{SAVE_DIR}/{file_prefix}_page_1.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(str(table))
            print(f"✅ Saved: {filename} (no results)")
        return
    
    # Calculate total pages (100 records per page)
    rows_per_page = 100
    total_pages = math.ceil(total_records / rows_per_page)
    print(f"📄 Total pages to scrape: {total_pages}")
    
    # Loop through all pages
    for page_number in range(1, total_pages + 1):
        print(f"\n📄 Scraping page {page_number}/{total_pages}...")
        
        # Add delay to avoid being blocked by server
        time.sleep(2)
        
        # Save current page HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table_container = soup.find("div", {"id": "tableContainer", "class": "datagrid"})
        
        if table_container:
            filename = f"{SAVE_DIR}/{file_prefix}_page_{page_number}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(str(table_container))
            print(f"✅ Saved: {filename}")
        else:
            print(f"⚠ No table found on page {page_number}")
        
        # If this is the last page, we're done
        if page_number >= total_pages:
            print(f"✔ Completed all {total_pages} pages")
            break
        
        # Navigate to next page
        try:
            print(f"➡️  Going to page {page_number + 1}...")
            next_button = wait.until(
                EC.element_to_be_clickable((By.ID, "nextPage"))
            )
            next_button.click()
            
            # Wait for new page to load
            time.sleep(2)
            wait.until(EC.presence_of_element_located((By.ID, "tableContainer")))
            time.sleep(1)  # Extra delay
            
        except Exception as e:
            print(f"⚠ Error clicking next button on page {page_number}: {e}")
            break


# ---------------- MAIN PROCESS ---------------- #

def process_group(group_code, course_code=None):
    """
    Process a single group or group+course combination
    """
    print(f"\n{'='*60}")
    if course_code:
        print(f"🔍 Processing: Group {group_code} - Course {course_code}")
        prefix = f"{group_code}_{course_code}"
    else:
        print(f"🔍 Processing: Group {group_code}")
        prefix = f"{group_code}"
    print(f"{'='*60}")
    
    switch_to_content()
    apply_filters_and_search(group_code=group_code, course_code=course_code)
    save_all_pages_by_total(prefix)


def process_omomi_course(course_code):
    """
    Process Omomi course - set ONLY course code, leave group BLANK
    """
    print(f"\n{'='*60}")
    print(f"🔍 Processing: Omomi Course {course_code} (no group filter)")
    print(f"{'='*60}")
    
    prefix = f"omomi_{course_code}"
    
    switch_to_content()
    apply_filters_and_search(group_code=None, course_code=course_code)  # No group code!
    save_all_pages_by_total(prefix)


def main():
    """Main execution function"""
    # Login
    driver.get(URL_LOGIN)
    input("👉 Login manually then press Enter...")
    
    print(f"\n📍 Current URL: {driver.current_url}")
    print(f"📦 Number of iframes: {len(driver.find_elements(By.TAG_NAME, 'iframe'))}")
    
    # Open search page
    open_search_page()
    
    # ---- Process Normal Groups ---- #
    print("\n" + "="*60)
    print("📚 PROCESSING NORMAL GROUPS")
    print("="*60)
    
    for code in GROUP_CODES:
        try:
            process_group(code)
            time.sleep(3)  # Delay between groups to avoid blocking
        except Exception as e:
            print(f"❌ Error processing group {code}: {e}")
            continue
    
    # ---- Process Omomi Courses ---- #
    print("\n" + "="*60)
    print("📚 PROCESSING OMOMI COURSES (NO GROUP FILTER)")
    print("="*60)
    
    for course in OMOMI_COURSE_CODES:
        try:
            process_omomi_course(course)  # Only course code, no group
            time.sleep(3)  # Delay between courses to avoid blocking
        except Exception as e:
            print(f"❌ Error processing omomi course {course}: {e}")
            continue
    
    print("\n" + "="*60)
    print("✅ ALL PROCESSING COMPLETE!")
    print("="*60)


# ---------------- RUN ---------------- #

try:
    main()
except Exception as e:
    print(f"\n❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\n🔒 Closing browser...")
    driver.quit()