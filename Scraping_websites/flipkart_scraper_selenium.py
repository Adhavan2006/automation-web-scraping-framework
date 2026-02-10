from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
        time.sleep(random.uniform(1,2))

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

    # Close login popup
    try:
        close_btn = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
        close_btn.click()
    except:
        pass

    all_data = []

    while True:
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "lvJbLV")))
            scroll(driver)

            products = driver.find_elements(By.CLASS_NAME, "lvJbLV")

            for product in products:

                productname = findtext(product, By.CLASS_NAME, "RG5Slk")
                if productname == "":
                    continue

                price = findtext(product, By.CLASS_NAME, "DeU9vF")
                rating = findtext(product, By.CLASS_NAME, "PvbNMB")
                image_url = find(product, By.TAG_NAME, "img", "src")
                link = find(product, By.TAG_NAME, "a", "href")
                pid = product.find_element(By.XPATH, ".//div[@data-id]").get_attribute("data-id")

                all_data.append({
                    "product_id": pid,
                    "product_name": productname,
                    "price": price,
                    "rating": rating,
                    "image_url": image_url,
                    "product_link": link
                })

            print(f"Scraped {len(all_data)} products so far...")

            # Click Next Page
            try:
                next_btn = driver.find_element(By.XPATH, "//a[contains(text(),'Next')]")
                next_btn.click()
                time.sleep(random.uniform(2,3))
            except:
                break   # No more pages

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

    URL = "https://www.flipkart.com/search?q=laptops"
    data = scrape(URL)

    # Save CSV
    with open("flipkart_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=data[0].keys()
        )
        writer.writeheader()
        writer.writerows(data)

    # Save JSON
    with open("flipkart_products.json","w",encoding="utf-8") as f:
        json.dump(data,f,indent=4)

    print("✅ Data saved to CSV and JSON")

# -------------------------------
if __name__ == "__main__":
    main()



