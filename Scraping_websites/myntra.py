import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException



BRAND_URLS = [
    "https://www.myntra.com/levis",
    "https://www.myntra.com/puma",
    "https://www.myntra.com/nike",
    "https://www.myntra.com/adidas",
    "https://www.myntra.com/hrx"
]

KEYWORD_URLS = [
    "https://www.myntra.com/tshirt?rawQuery=tshirt",
    "https://www.myntra.com/shoes?rawQuery=shoes",
    "https://www.myntra.com/jeans?rawQuery=jeans",
    "https://www.myntra.com/dresses?rawQuery=dresses",
    "https://www.myntra.com/jackets?rawQuery=jackets"
]

def scroll_page(driver, scroll_pause=1.5, max_scrolls=15):
    print("Scrolling page to load products...")
    for i in range(max_scrolls):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        print(f"Scrolled {i+1}/{max_scrolls}")
        time.sleep(scroll_pause)
    print("Scrolling complete.")

def safe_find_text(element, by, selector):
    try:
        el = element.find_element(by, selector)
        return el.text.strip()
    except NoSuchElementException:
        return ""

def safe_find_attr(element, by, selector, attr):
    try:
        el = element.find_element(by, selector)
        return el.get_attribute(attr) or ""
    except NoSuchElementException:
        return ""

def scrape_page(url, source_page):
    print(f"Opening browser for: {url}")
    driver = webdriver.Chrome()
    driver.get(url)

    scroll_page(driver)

    products = driver.find_elements(By.CLASS_NAME, "product-base")
    print(f"Found {len(products)} products on the page.")

    data = []
    for i, product in enumerate(products[:30], start=1):
        product_id = product.get_attribute("data-product-id") or ""
        brand = safe_find_text(product, By.CLASS_NAME, "product-brand")
        product_name = safe_find_text(product, By.CLASS_NAME, "product-product")
        image_url = safe_find_attr(product, By.TAG_NAME, "img", "src") or ""
        selling_price = safe_find_text(product, By.CLASS_NAME, "product-discountedPrice")
        mrp_price = safe_find_text(product, By.CLASS_NAME, "product-strike")
        discount = safe_find_text(product, By.CLASS_NAME, "product-discount")
        rating = safe_find_text(product, By.CLASS_NAME, "product-ratingCount")
        comment_count = ""  # Not available on listing pages

        # Detect ads differently depending on page type
        if source_page == "brand":  
            try:
                ad_label = product.find_element(By.CLASS_NAME, "product-ad-label")
                listing_type = "Advertisement" if ad_label else "Organic"
            except NoSuchElementException:
                listing_type = "Organic"
        else:  # keyword page
            try:
                ad_label = product.find_element(By.CLASS_NAME, "product-ad-tag")
                listing_type = "Advertisement" if ad_label else "Organic"
            except NoSuchElementException:
                listing_type = "Organic"

        data.append({
            "product_id": product_id,
            "brand": brand,
            "product_name": product_name,
            "image_url": image_url,
            "selling_price": selling_price,
            "mrp_price": mrp_price,
            "discount_percent": discount,
            "rating": rating,
            "comment_count": comment_count,
            "listing_type": listing_type,
            "source_page": source_page,
        })

        print(f"Scraped product {i}: {brand} - {product_name} ({listing_type})")

    driver.quit()
    print(f"Scraped {len(data)} products from {url}")
    return data

def main():
    all_data = []

    print("Starting brand pages scraping...")
    for url in BRAND_URLS:
        brand_data = scrape_page(url, source_page="brand")
        all_data.extend(brand_data)

    print("Starting keyword pages scraping...")
    for url in KEYWORD_URLS:
        keyword_data = scrape_page(url, source_page="keyword")
        all_data.extend(keyword_data)

    with open("myntra_products_selenium.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "product_id","brand","product_name","image_url","selling_price",
            "mrp_price","discount_percent","rating","comment_count",
            "listing_type","source_page"
        ])
        writer.writeheader()
        writer.writerows(all_data)

    print(f"Scraping completed. Total products scraped: {len(all_data)}")
    print("Output saved to myntra_products_selenium.csv")

if __name__ == "__main__":
    main()
