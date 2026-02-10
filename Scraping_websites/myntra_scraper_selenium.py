import time, csv, json, random, logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# ---------------- SETTINGS ----------------

BRAND_URLS = [
    "https://www.myntra.com/levis",
    "https://www.myntra.com/puma"
]

KEYWORD_URLS = [
    "https://www.myntra.com/tshirt?rawQuery=tshirt",
    "https://www.myntra.com/shoes?rawQuery=shoes"
]

MAX_PRODUCTS = 200
SCROLLS = 12

logging.basicConfig(filename="scraper.log", level=logging.INFO)

# ---------------- DRIVER ----------------

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=options)

# ---------------- HELPERS ----------------

def clean_price(text):
    return int(text.replace("₹","").replace(",","").strip()) if text else ""

def clean_rating(text):
    if text == "":
        return "0"
    return ''.join(ch for ch in text if ch.isdigit())

def safe_text(parent, by, value):
    try:
        return parent.find_element(by,value).text.strip()
    except:
        return ""

def safe_attr(parent, by, value, attr):
    try:
        return parent.find_element(by,value).get_attribute(attr)
    except:
        return ""

def scroll(driver):
    for _ in range(SCROLLS):
        driver.execute_script("window.scrollBy(0, window.innerHeight)")
        time.sleep(1.5)

# ---------------- SCRAPER ----------------

def scrape_page(url, source):

    driver = get_driver()
    driver.get(url)

    wait = WebDriverWait(driver,10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME,"product-base")))

    results = []

    while len(results) < MAX_PRODUCTS:

        scroll(driver)

        products = driver.find_elements(By.CLASS_NAME,"product-base")

        for p in products:
            if len(results) >= MAX_PRODUCTS:
                break

            try:
                pid = p.get_attribute("data-product-id") or ""

                brand = safe_text(p,By.CLASS_NAME,"product-brand")
                name = safe_text(p,By.CLASS_NAME,"product-product")
                img = safe_attr(p,By.TAG_NAME,"img","src")
                link = safe_attr(p,By.TAG_NAME,"a","href")

                sp = clean_price(safe_text(p,By.CLASS_NAME,"product-discountedPrice"))
                mrp = clean_price(safe_text(p,By.CLASS_NAME,"product-strike"))
                disc = safe_text(p,By.CLASS_NAME,"product-discount")

                rating = clean_rating(safe_text(p,By.CLASS_NAME,"product-ratingCount"))
                reviews = clean_rating(safe_text(p, By.CLASS_NAME, "product-ratingsCount"))
                if pid == "" and link != "":
                    pid = link.split("/")[-2]
                try:
                    p.find_element(By.CLASS_NAME,"product-ad-label")
                    listing="Advertisement"
                except:
                    listing="Organic"

                results.append({
                    "product_id":pid,
                    "brand":brand,
                    "product_name":name,
                    "selling_price":sp,
                    "mrp_price":mrp,
                    "discount":disc,
                    "rating":rating,
                    "image_url":img,
                    "product_url":link,
                    "listing_type":listing,
                    "source_page":source
                })

            except Exception as e:
                logging.error(str(e))

        try:
            next_btn = driver.find_element(By.XPATH,"//a[contains(text(),'Next')]")
            next_btn.click()
            time.sleep(3)
        except:
            break

    driver.quit()
    return results

# ---------------- MAIN ----------------

def main():

    all_data=[]

    for u in BRAND_URLS:
        all_data.extend(scrape_page(u,"brand"))

    for u in KEYWORD_URLS:
        all_data.extend(scrape_page(u,"keyword"))

    # CSV
    with open("myntra.csv","w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=all_data[0].keys())
        writer.writeheader()
        writer.writerows(all_data)

    # JSON
    with open("myntra.json","w",encoding="utf-8") as f:
        json.dump(all_data,f,indent=4)

    print("TOTAL PRODUCTS:",len(all_data))

if __name__=="__main__":
    main()
