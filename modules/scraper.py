"""
Google Books scraper module
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import os


class GoogleBooksScraper:
    def __init__(self, download_path=None):
        self.driver = None
        self.book_list = []
        self.force_startnum = -1
        self.is_running = False

        if download_path is None:
            self.download_path = os.path.join(os.getcwd(), 'Downloads')
        else:
            self.download_path = download_path

        # Create download directory if it doesn't exist
        os.makedirs(self.download_path, exist_ok=True)

    def init_driver(self):
        """Initialize Chrome driver with undetected-chromedriver"""
        chrome_options = uc.ChromeOptions()
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.popups": 1,
            "profile.default_content_setting_values.notifications": 1,
            "download.default_directory": self.download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        })

        self.driver = uc.Chrome(options=chrome_options)
        return True

    def navigate_to_book(self, book_url):
        """Navigate to Google Books URL"""
        if not self.driver:
            return False
        self.driver.get(book_url)
        return True

    def download_image(self, image_url, file_name):
        """Download image using JavaScript injection"""
        javascript = f"""(function() {{
        var blobUrl = "{image_url}";

        function downloadBlob(blobUrl, fileName) {{
            fetch(blobUrl)
                .then(response => response.blob())
                .then(blob => {{
                    var url = window.URL.createObjectURL(blob);
                    var a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = fileName;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                }})
                .catch(error => console.error('Image download failed:', error));
        }}

        downloadBlob(blobUrl, '{file_name}.png');
        }})();"""

        self.driver.execute_script(javascript)

    def scrape_current_page(self):
        """Scrape images from current page"""
        try:
            # Switch to main window
            self.driver.switch_to.window(self.driver.window_handles[0])

            # Find and switch to iframe
            iframe = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.-gb-display"))
            )
            self.driver.switch_to.frame(iframe)

            # Find wrapper element
            wrapper = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cdk-virtual-scroll-content-wrapper"))
            )

            # Find all images
            ol_element = wrapper.find_element(By.TAG_NAME, "ol")
            li_elements = ol_element.find_elements(By.TAG_NAME, "li")

            new_images = []
            for li in li_elements:
                try:
                    render = li.find_element(By.TAG_NAME, "reader-rendered-page")
                    img = render.find_element(By.TAG_NAME, "img")
                    src_value = img.get_attribute('src')

                    if src_value and src_value not in self.book_list:
                        self.book_list.append(src_value)
                        last_index = len(self.book_list) - 1 + self.force_startnum
                        self.download_image(src_value, last_index)
                        new_images.append((src_value, last_index))
                except:
                    continue

            # Scroll to load more
            if li_elements:
                self.driver.execute_script("arguments[0].scrollIntoView();", li_elements[-1])

            return wrapper, new_images

        except Exception as e:
            print(f"Error scraping page: {e}")
            return None, []

    def start_scraping(self, callback=None):
        """Start continuous scraping"""
        self.is_running = True

        while self.is_running:
            wrapper, new_images = self.scrape_current_page()

            if callback and new_images:
                callback(new_images)

            time.sleep(2)

    def stop_scraping(self):
        """Stop scraping"""
        self.is_running = False

    def close(self):
        """Close driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None