import os
import time
import logging
from typing import List, Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class ConfigurationManager:
    """Manages configuration for web scraping"""
    def __init__(self, 
                 group_codes: List[str] = None, 
                 organ_courses: List[str] = None, 
                 omomi_code: str = None):
        """
        Initialize configuration for course search
        
        :param group_codes: List of group codes to search
        :param organ_courses: List of organ courses to filter
        :param omomi_code: Omomi code for additional filtering
        """
        self.group_codes = group_codes or [
            "2110130", "2114199", "2157719", "2123818", 
            "2125299", "2110153", "2157799", "2115799"
        ]
        self.organ_courses = organ_courses or [
            "25", "51589", "24", "50908", "51586", 
            "51587", "1040280289", "1040280290"
        ]
        self.omomi_code = omomi_code or "2110199"

class WebDriverManager:
    """Manages WebDriver setup and configuration"""
    def __init__(self, driver_path: str = "chrome/chromedriver.exe"):
        """
        Initialize WebDriver with specified path
        
        :param driver_path: Path to ChromeDriver executable
        """
        self.driver_path = driver_path
        self.driver = None
    
    def setup_driver(self) -> webdriver.Chrome:
        """
        Setup and configure Chrome WebDriver
        
        :return: Configured Chrome WebDriver
        """
        service = Service(self.driver_path)
        options = Options()
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver
    
    def close_driver(self):
        """Close the WebDriver if it's active"""
        if self.driver:
            self.driver.quit()

class CourseSearchScraper:
    """Main class for course search and data extraction"""
    def __init__(self, 
                 config: ConfigurationManager, 
                 driver_manager: WebDriverManager,
                 output_directory: str = "html-pages"):
        """
        Initialize CourseSearchScraper
        
        :param config: Configuration manager
        :param driver_manager: WebDriver manager
        :param output_directory: Directory to save extracted HTML files
        """
        self.config = config
        self.driver_manager = driver_manager
        self.driver = driver_manager.setup_driver()
        self.output_directory = output_directory
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if not exists
        os.makedirs(output_directory, exist_ok=True)
    
    def login(self, login_url: str = "https://eserv.iau.ir/EServices/Pages/acmstd/loginPage.jsp"):
        """
        Navigate to login page and wait for manual login
        
        :param login_url: URL of the login page
        """
        self.driver.get(login_url)
        input("Please login at Amozeshyar portal in the opened Chrome window, then press Enter to continue...")
    
    def apply_search_parameters(self, group_code: Optional[str] = None, organ_course: Optional[str] = None):
        """
        Apply search parameters to the form
        
        :param group_code: Group code to search
        :param organ_course: Organ course to filter
        """
        try:
            # Group Code
            if group_code:
                group_code_input = self.driver.find_element(By.NAME, "parameter(f^groupCode)")
                group_code_input.clear()
                group_code_input.send_keys(group_code)
            
            # Organ Course
            if organ_course:
                ed_level_select = Select(
                    self.driver.find_element(By.NAME, "parameter(f^presentCourse.organCourse.course.typeRef)")
                )
                ed_level_select.select_by_value(str(organ_course))
            
            self.logger.info(f"Search parameters applied: Group Code={group_code}, Organ Course={organ_course}")
        
        except Exception as e:
            self.logger.error(f"Error applying search parameters: {e}")
            raise
    
    def execute_search(self):
        """Execute comprehensive course search with multiple filters"""
        try:
            # Navigate to course search page
            self._navigate_to_search_page()
            
            # Search by Group Codes
            for group_code in self.config.group_codes:
                self._search_and_extract(group_code=group_code)
            
            # Search by Organ Courses with Omomi Code
            for organ_course in self.config.organ_courses:
                self._search_and_extract(
                    group_code=self.config.omomi_code, 
                    organ_course=organ_course
                )
        
        except Exception as e:
            self.logger.error(f"Search execution failed: {e}")
            raise
    
    def _navigate_to_search_page(self):
        """Navigate to the course search page"""
        WebDriverWait(self.driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "menuFrame"))
        )
        
        class_search_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='برنامه ريزي آموزشي نيمسال تحصيلي']/ancestor::li"))
        )
        class_search_link.click()
        
        class_search_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='جستجوي كلاس درسهای ارائه شده']/ancestor::a"))
        )
        class_search_link.click()
    
    def _search_and_extract(self, group_code: str = None, organ_course: str = None):
        """
        Perform search for given parameters and extract data
        
        :param group_code: Group code to search
        :param organ_course: Organ course to filter
        """
        try:
            # Apply search parameters
            self.apply_search_parameters(group_code, organ_course)
            
            # Set rows per page
            row_count_dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "parameter(rowCount)"))
            )
            Select(row_count_dropdown).select_by_value("100")
            
            # Click search button
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "submitBtn"))
            )
            search_button.click()
            
            # Extract total records
            total_records = self._get_total_records()
            
            # Pagination and extraction
            self._paginate_and_extract(
                total_records, 
                group_code, 
                organ_course
            )
        
        except Exception as e:
            self.logger.error(f"Search and extract failed: {e}")
            raise
    
    def _get_total_records(self) -> int:
        """
        Get total number of records from search results
        
        :return: Total number of records
        """
        page_html = self.driver.page_source
        soup = BeautifulSoup(page_html, 'html.parser')
        
        total_records_element = soup.find('span', {'id': 'totalSearchCount'})
        if total_records_element:
            return int(total_records_element.text.strip())
        
        raise ValueError("Total records not found")
    
    def _paginate_and_extract(self, 
                               total_records: int, 
                               group_code: str = None, 
                               organ_course: str = None):
        """
        Paginate through search results and extract data
        
        :param total_records: Total number of records
        :param group_code: Group code for file naming
        :param organ_course: Organ course for file naming
        """
        current_start = 0
        records_per_page = 100
        page_number = 1
        
        while current_start < total_records:
            try:
                time.sleep(2)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                table_container = soup.find('div', {
                    'id': 'tableContainer',
                    'class': 'datagrid'
                })
                
                if table_container:
                    filename = self._generate_filename(
                        group_code, 
                        organ_course, 
                        page_number
                    )
                    self._save_html(table_container, filename)
                
                current_start = page_number * records_per_page
                
                if current_start >= total_records:
                    break
                
                # Navigate to next page
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "nextPage"))
                )
                next_button.click()
                
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'نتايج جستجو')]"))
                )
                
                page_number += 1
            
            except Exception as e:
                self.logger.error(f"Pagination error on page {page_number}: {e}")
                break
    
    def _generate_filename(self, 
                            group_code: str = None, 
                            organ_course: str = None, 
                            page_number: int = 1) -> str:
        """
        Generate filename for extracted HTML
        
        :param group_code: Group code for filename
        :param organ_course: Organ course for filename
        :param page_number: Current page number
        :return: Generated filename
        """
        if group_code and organ_course:
            return os.path.join(
                self.output_directory, 
                f"{group_code}_{organ_course}_offered_courses_page_{page_number}.html"
            )
        elif group_code:
            return os.path.join(
                self.output_directory, 
                f"{group_code}_offered_courses_page_{page_number}.html"
            )
        else:
            return os.path.join(
                self.output_directory, 
                f"offered_courses_page_{page_number}.html"
            )
    
    def _save_html(self, content, filename):
        """
        Save HTML content to file
        
        :param content: HTML content to save
        :param filename: File to save content
        """
        with open(filename, "w", encoding="utf-8") as file:
            file.write(str(content))
        self.logger.info(f"Saved extracted table: {filename}")
    
    def run(self):
        """
        Execute the entire scraping process
        """
        try:
            self.login()
            self.execute_search()
        except Exception as e:
            self.logger.error(f"Scraping process failed: {e}")
        finally:
            self.driver_manager.close_driver()

def main():
    """Main entry point for the script"""
    config = ConfigurationManager()
    driver_manager = WebDriverManager()
    
    scraper = CourseSearchScraper(config, driver_manager)
    scraper.run()

if __name__ == "__main__":
    main()