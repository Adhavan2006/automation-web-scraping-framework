from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import json
import random

# -------------------------------
# SAFE FIND FUNCTIONS
# -------------------------------

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

# -------------------------------
# AUTO SCROLL
# -------------------------------

def scroll(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 2))

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height

# -------------------------------
# SCRAPER FUNCTION
# -------------------------------

def scrape(URL):

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.get(URL)
    time.sleep(3)

    # Close login popup
    try:
        driver.find_element(By.XPATH, "//button[contains(text(),'✕')]").click()
    except:
        pass

    all_data = []
    seen_names = set()

    while True:
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sc-evWYkj")))

            scroll(driver)
            time.sleep(2)

            restaurants = driver.find_elements(By.CLASS_NAME, "sc-evWYkj")

            for r in restaurants:

                name = findtext(r, By.CLASS_NAME, "sc-1hp8d8a-0")
                if name == "":
                    continue

                if name in seen_names:
                    continue

                seen_names.add(name)

                cuisine = findtext(r, By.CLASS_NAME, "sc-1hez2tp-0")
                rating = findtext(r, By.CLASS_NAME, "sc-1q7bklc-1")
                delivery_time = findtext(r, By.CLASS_NAME, "min-basic-info-right")
                cost = findtext(r, By.CLASS_NAME, "fIHvpg")
                link = find(r, By.TAG_NAME, "a", "href")
                image = find(r, By.TAG_NAME, "img", "src")

                all_data.append({
                    "restaurant_name": name,
                    "cuisine": cuisine,
                    "rating": rating,
                    "delivery_time": delivery_time,
                    "cost": cost,
                    "restaurant_link": link,
                    "image_url": image,
                    "location": "Chennai"
                })

            print(f"Scraped {len(all_data)} restaurants so far...")

            break   # Zomato loads everything via scroll only (no next page)

        except Exception as e:
            driver.save_screenshot("error.png")
            print("Error:", e)
            break

    driver.quit()
    return all_data

# -------------------------------
# MAIN FUNCTION
# -------------------------------

def main():

    URL = "https://www.zomato.com/chennai/delivery"
    data = scrape(URL)

    if not data:
        print("No data scraped.")
        return

    # Save CSV
    with open("zomato_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=data[0].keys()
        )
        writer.writeheader()
        writer.writerows(data)

    # Save JSON
    with open("zomato_products.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("✅ Data saved to CSV and JSON")

# -------------------------------
if __name__ == "__main__":
    main()
