#brand
import asyncio
import csv
from playwright.async_api import async_playwright

BRAND_URLS = [
    "https://www.myntra.com/levis",
    "https://www.myntra.com/puma",
    "https://www.myntra.com/nike",
    "https://www.myntra.com/adidas",
    "https://www.myntra.com/hrx"
]

async def scroll_page(page, scroll_delay=1.5, max_scrolls=15):
    print("Starting to scroll the page to load products...")
    for i in range(max_scrolls):
        await page.evaluate("window.scrollBy(0, window.innerHeight)")
        print(f"Scrolled {i+1}/{max_scrolls}")
        await asyncio.sleep(scroll_delay)
    print("Finished scrolling.")

async def safe_text(element_handle, selector):
    try:
        el = await element_handle.query_selector(selector)
        if el:
            text = await el.text_content()
            return text.strip() if text else ""
        else:
            return ""
    except Exception:
        return ""

async def safe_attr(element_handle, selector, attribute):
    try:
        el = await element_handle.query_selector(selector)
        if el:
            attr = await el.get_attribute(attribute)
            return attr or ""
        else:
            return ""
    except Exception:
        return ""

async def scrape_brand(url):
    async with async_playwright() as p:
        print(f"Launching browser for: {url}")
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        page = await browser.new_page()
        
        try:
            print(f"Loading page: {url}")
            await page.goto(url, timeout=30000)
        except Exception as e:
            print(f"Failed to load {url}: {e}")
            await browser.close()
            return []
        
        await scroll_page(page)

        products = await page.query_selector_all(".product-base")
        print(f"Found {len(products)} products on the page.")

        data = []

        for i, product in enumerate(products[:30], start=1):  # get first 30 products
            product_id = await product.get_attribute("data-product-id") or ""
            brand = await safe_text(product, ".product-brand")
            product_name = await safe_text(product, ".product-product")
            image_url = await safe_attr(product, "img", "src") or ""
            selling_price = await safe_text(product, ".product-discountedPrice")
            mrp_price = await safe_text(product, ".product-strike")
            discount = await safe_text(product, ".product-discount")
            rating = await safe_text(product, ".product-ratingCount")
            comment_count = ""  # Not usually available on listing page

            # Basic ad detection (can improve by inspecting actual ad labels on Myntra)
            ad_label = await product.query_selector(".product-ad-label")
            listing_type = "Advertisement" if ad_label else "Organic"

            source_page = "brand"

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
            print(f"Scraped product {i}: {brand} - {product_name}")

        await browser.close()
        print(f"Scraped {len(data)} products from {url}")
        return data

async def main():
    all_data = []
    for url in BRAND_URLS:
        brand_data = await scrape_brand(url)
        all_data.extend(brand_data)

    with open("myntra_brand_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "product_id","brand","product_name","image_url","selling_price",
            "mrp_price","discount_percent","rating","comment_count",
            "listing_type","source_page"
        ])
        writer.writeheader()
        writer.writerows(all_data)

    print(f"Scraping completed. Total products scraped: {len(all_data)}")
    print("Output saved to myntra_brand_products.csv")

if __name__ == "__main__":
    asyncio.run(main())



#keyword
import asyncio
import csv
from playwright.async_api import async_playwright

KEYWORD_URLS = [
    "https://www.myntra.com/tshirt?rawQuery=tshirt",
    "https://www.myntra.com/shoes?rawQuery=shoes",
    "https://www.myntra.com/jeans?rawQuery=jeans",
    "https://www.myntra.com/dresses?rawQuery=dresses",
    "https://www.myntra.com/jackets?rawQuery=jackets"
]

async def scroll_page(page, scroll_delay=1.5, max_scrolls=15):
    print("Scrolling page to load products...")
    for i in range(max_scrolls):
        await page.evaluate("window.scrollBy(0, window.innerHeight)")
        print(f"Scrolled {i+1}/{max_scrolls}")
        await asyncio.sleep(scroll_delay)
    print("Scrolling complete.")

async def safe_text(element_handle, selector):
    try:
        el = await element_handle.query_selector(selector)
        if el:
            text = await el.text_content()
            return text.strip() if text else ""
        else:
            return ""
    except Exception:
        return ""

async def safe_attr(element_handle, selector, attribute):
    try:
        el = await element_handle.query_selector(selector)
        if el:
            attr = await el.get_attribute(attribute)
            return attr or ""
        else:
            return ""
    except Exception:
        return ""

async def scrape_keyword(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        page = await browser.new_page()
        try:
            print(f"Loading keyword page: {url}")
            await page.goto(url, timeout=30000)
        except Exception as e:
            print(f"Failed to load {url}: {e}")
            await browser.close()
            return []
        await scroll_page(page)

        products = await page.query_selector_all(".product-base")
        print(f"Found {len(products)} products on the page.")

        data = []

        for i, product in enumerate(products[:30], start=1):
            product_id = await product.get_attribute("data-product-id") or ""
            brand = await safe_text(product, ".product-brand")
            product_name = await safe_text(product, ".product-product")
            image_url = await safe_attr(product, "img", "src") or ""
            selling_price = await safe_text(product, ".product-discountedPrice")
            mrp_price = await safe_text(product, ".product-strike")
            discount = await safe_text(product, ".product-discount")
            rating = await safe_text(product, ".product-ratingCount")
            comment_count = ""  # Not available on listing page

            # Detect ads by checking for '.product-ad-tag' span
            ad_label = await product.query_selector(".product-ad-tag")
            listing_type = "Advertisement" if ad_label else "Organic"

            source_page = "keyword"

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

        await browser.close()
        print(f"Scraped {len(data)} products from {url}")
        return data

async def main():
    all_data = []
    for url in KEYWORD_URLS:
        keyword_data = await scrape_keyword(url)
        all_data.extend(keyword_data)

    with open("myntra_keyword_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "product_id","brand","product_name","image_url","selling_price",
            "mrp_price","discount_percent","rating","comment_count",
            "listing_type","source_page"
        ])
        writer.writeheader()
        writer.writerows(all_data)

    print(f"Keyword scraping completed. Total products scraped: {len(all_data)}")
    print("Output saved to myntra_keyword_products.csv")

if __name__ == "__main__":
    asyncio.run(main())
