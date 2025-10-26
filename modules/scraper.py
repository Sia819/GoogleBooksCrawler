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
    def __init__(self, download_path=None, use_profile=True):
        self.driver = None
        self.book_list = []
        self.force_startnum = -1
        self.is_running = False
        self.use_profile = use_profile

        if download_path is None:
            self.download_path = os.path.join(os.getcwd(), 'Downloads')
        else:
            self.download_path = download_path

        # Create download directory if it doesn't exist
        os.makedirs(self.download_path, exist_ok=True)

        # Set up Chrome profile directory
        self.profile_dir = os.path.join(os.getcwd(), 'chrome_profile')
        if self.use_profile:
            os.makedirs(self.profile_dir, exist_ok=True)

    def init_driver(self, use_existing_profile=True):
        """Initialize Chrome driver with undetected-chromedriver"""
        chrome_options = uc.ChromeOptions()

        # Use persistent profile to maintain login sessions
        if self.use_profile and use_existing_profile:
            chrome_options.add_argument(f'--user-data-dir={self.profile_dir}')
            chrome_options.add_argument('--profile-directory=Default')
            print(f"Using Chrome profile from: {self.profile_dir}")

        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.popups": 1,
            "profile.default_content_setting_values.notifications": 1,
            "download.default_directory": self.download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        })

        # Additional options for better stability
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        try:
            self.driver = uc.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"Error initializing driver: {e}")
            return False

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

    def set_zoom(self, zoom_level):
        """Set browser zoom level (percentage)"""
        if self.driver:
            try:
                # Execute JavaScript to set zoom level
                script = f"document.body.style.zoom = '{zoom_level}%'"
                self.driver.execute_script(script)
                return True
            except Exception as e:
                print(f"Error setting zoom: {e}")
                return False
        return False

    def zoom_in(self, step=10):
        """Zoom in by step percentage"""
        if self.driver:
            try:
                # Get current zoom level
                current = self.driver.execute_script("return document.body.style.zoom || '100%'")
                current_value = int(current.replace('%', ''))
                new_value = min(current_value + step, 300)  # Max 300%
                return self.set_zoom(new_value)
            except Exception as e:
                print(f"Error zooming in: {e}")
                return False
        return False

    def zoom_out(self, step=10):
        """Zoom out by step percentage"""
        if self.driver:
            try:
                # Get current zoom level
                current = self.driver.execute_script("return document.body.style.zoom || '100%'")
                current_value = int(current.replace('%', ''))
                new_value = max(current_value - step, 25)  # Min 25%
                return self.set_zoom(new_value)
            except Exception as e:
                print(f"Error zooming out: {e}")
                return False
        return False

    def reset_zoom(self):
        """Reset zoom to 100%"""
        return self.set_zoom(100)

    def close(self):
        """Close driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None