from playwright.sync_api import sync_playwright
import time

class FridayFood:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
    
    def start_browser(self):
        if self.browser is None:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)
            self.page = self.browser.new_page()
        return self.page
    
    # ==================== SWIGGY ====================
    def swiggy_search(self, query):
        page = self.start_browser()
        page.goto("https://www.swiggy.com")
        time.sleep(5)
        
        # Click on search box
        try:
            # Try different selectors for Swiggy search
            selectors = ["input[type='text']", "input[placeholder*='Search']", ".SearchBar"]
            for selector in selectors:
                try:
                    search_box = page.wait_for_selector(selector, timeout=3000)
                    if search_box:
                        search_box.click()
                        search_box.fill(query)
                        search_box.press("Enter")
                        time.sleep(3)
                        return f"Searching Swiggy for '{query}', sir."
                except:
                    continue
            return "Could not find search box on Swiggy"
        except Exception as e:
            return f"Swiggy error: {e}"
    
    def swiggy_add_to_cart(self, item_number=1):
        page = self.start_browser()
        try:
            # Click on first restaurant result
            restaurants = page.query_selector_all("[data-testid='restaurant-card']")
            if restaurants and len(restaurants) >= item_number:
                restaurants[item_number-1].click()
                time.sleep(3)
                
                # Find add button (simplified - Swiggy layout varies)
                add_buttons = page.query_selector_all("button:has-text('ADD')")
                if add_buttons:
                    add_buttons[0].click()
                    return f"Added item #{item_number} to cart, sir."
            return "Could not add to cart"
        except Exception as e:
            return f"Error: {e}"
    
    # ==================== ZOMATO ====================
    def zomato_search(self, query):
        page = self.start_browser()
        page.goto("https://www.zomato.com")
        time.sleep(5)
        
        try:
            search_box = page.wait_for_selector("input[placeholder*='Search']", timeout=5000)
            if search_box:
                search_box.click()
                search_box.fill(query)
                search_box.press("Enter")
                time.sleep(3)
                return f"Searching Zomato for '{query}', sir."
            return "Could not find search box on Zomato"
        except Exception as e:
            return f"Zomato error: {e}"
    
    def zomato_add_to_cart(self):
        page = self.start_browser()
        try:
            # Click first restaurant
            restaurants = page.query_selector_all("[data-testid='restaurant-card']")
            if restaurants:
                restaurants[0].click()
                time.sleep(3)
                return "Opened restaurant, sir. Please add to cart manually."
            return "Could not find restaurant"
        except Exception as e:
            return f"Error: {e}"
    
    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

friday_food = FridayFood()