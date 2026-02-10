from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import json
import random

def findtext(element, by, selector):
    try:
        return element.find_element(by, selector).text.strip()
    except NoSuchElementException:
        return ""

def find(element, by, selector, attr):
    try:
        return element.find_element(by, selector).get_attribute(attr) or ""
    except NoSuchElementException:
        return ""

def scroll(driver, max_scrolls=5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0

    while scroll_count < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 2))  # wait for content to load

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # No more content loaded after scroll
            break
        last_height = new_height
        scroll_count += 1

def scrape(URL, max_scrolls=5):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0")
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.get(URL)

    # Close login popup if present
    try:
        close_btn = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
        close_btn.click()
    except Exception:
        pass

    # Scroll the page fully before scraping
    scroll(driver, max_scrolls=max_scrolls)

    # After scrolling, get all products
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sc-evWYkj")))
    products = driver.find_elements(By.CLASS_NAME, "sc-evWYkj")

    all_data = []

    for product in products:
        restuarant_name = findtext(product, By.CLASS_NAME, "sc-1hp8d8a-0")
        if restuarant_name == "":
            continue

        cuisine = findtext(product, By.CLASS_NAME, "sc-1hez2tp-0")
        rating = findtext(product, By.CLASS_NAME, "sc-1q7bklc-1")
        delivery_time = findtext(product, By.CLASS_NAME, "min-basic-info-right")
        cost = findtext(product, By.CLASS_NAME, "fIHvpg")
        restuarant_link = find(product, By.TAG_NAME, "a", "href")
        image_url = find(product, By.TAG_NAME, "img", "src")
        location = "chennai"

        all_data.append({
            "restuarant_name": restuarant_name,
            "cuisine": cuisine,
            "rating": rating,
            "delivery_time": delivery_time,
            "cost": cost,
            "restuarant_link": restuarant_link,
            "image_url": image_url,
            "location": location
        })

    driver.quit()
    return all_data

def main():
    URL = "https://www.zomato.com/chennai/delivery"
    data = scrape(URL, max_scrolls=10)

    if not data:
        print("No data scraped. Exiting without saving files.")
        return

    with open("zomato_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    with open("zomato_products.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("✅ Data saved to CSV and JSON")

if __name__ == "__main__":
    main()


