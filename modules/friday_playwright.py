from playwright.sync_api import sync_playwright
import time

playwright_instance = None
browser_instance = None
page_instance = None

def get_page():
    global playwright_instance, browser_instance, page_instance
    
    if page_instance is not None:
        try:
            page_instance.title()
            return page_instance
        except:
            pass
    
    if playwright_instance:
        try:
            playwright_instance.stop()
        except:
            pass
    
    playwright_instance = sync_playwright().start()
    browser_instance = playwright_instance.chromium.launch(headless=False)
    page_instance = browser_instance.new_page()
    return page_instance

class FridayPlaywright:
    def open_website(self, site_name):
        page = get_page()

        if "." not in site_name:
            site_name = f"{site_name}.com"

        if not site_name.startswith("http"):
            site_name = f"https://{site_name}"

        page.goto(site_name)
        time.sleep(4)
        return f"Opening {site_name}, sir."
    
    def google_search(self, query):
        """Search directly on Google"""
        page = get_page()
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        page.goto(search_url)
        time.sleep(3)
        return f"Searching Google for '{query}', sir."
    
    def search_on_page(self, query):
        page = get_page()
        time.sleep(3)
        
        if "flipkart" in page.url:
            search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
            page.goto(search_url)
            time.sleep(3)
            return f"Searching for '{query}' on Flipkart, sir."
        
        try:
            search_box = page.locator("input[type='search'], input[name='q'], input[type='text']").first
            if search_box and search_box.is_visible():
                search_box.click()
                search_box.fill(query)
                search_box.press("Enter")
                time.sleep(3)
                return f"Searching for '{query}', sir."
        except:
            pass
        
        return "Could not find search box."
    
    def click_result(self, number):
        page = get_page()
        try:
            results = page.query_selector_all("a[href*='amazon'], a[href*='flipkart'], .s-result-item")
            if number <= len(results):
                results[number-1].click()
                time.sleep(2)
                return f"Clicked result #{number}, sir."
            else:
                return f"Only {len(results)} results found."
        except Exception as e:
            return f"Error: {e}"
    
    def read_page_text(self):
        """Read all text from current webpage"""
        page = get_page()
        try:
            # Try to get text from body
            text = page.locator("body").inner_text()
            if text and len(text) > 10:
                return text[:2000]
            else:
                return "No visible text found on this page."
        except Exception as e:
            return f"Error reading page: {e}"
    
    def scroll_down(self):
        get_page().evaluate("window.scrollBy(0, 500)")
        return "Scrolling down, sir."
    
    def scroll_up(self):
        get_page().evaluate("window.scrollBy(0, -500)")
        return "Scrolling up, sir."
    
    def go_back(self):
        get_page().go_back()
        return "Going back, sir."
    
    def refresh(self):
        get_page().reload()
        return "Refreshing page, sir."

friday_browser = FridayPlaywright()