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

async def scroll_page(page, scroll_delay=1.0, max_scrolls=10):
    for _ in range(max_scrolls):
        await page.evaluate("""() => {
            window.scrollBy(0, window.innerHeight);
        }""")
        await asyncio.sleep(scroll_delay)

async def scrape_brand(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await scroll_page(page, scroll_delay=1.5, max_scrolls=15)

        products = await page.query_selector_all(".product-base")

        data = []

        for product in products[:30]:  # limit to 30 products
            # Extract fields safely
            try:
                product_id = await product.get_attribute("data-product-id")
                brand = await product.query_selector_eval(".product-brand", "el => el.textContent.trim()") or ""
                product_name = await product.query_selector_eval(".product-product", "el => el.textContent.trim()") or ""
                image_url = await product.query_selector_eval("img", "el => el.getAttribute('src')") or ""
                selling_price = await product.query_selector_eval(".product-discountedPrice", "el => el.textContent.trim()") or ""
                mrp_price = await product.query_selector_eval(".product-strike", "el => el.textContent.trim()") or ""
                discount = await product.query_selector_eval(".product-discount", "el => el.textContent.trim()") or ""
                rating = await product.query_selector_eval(".product-ratingCount", "el => el.textContent.trim()") or ""
                comment_count = ""  # Myntra may not show comment counts on listing pages

                # Determine listing type
                ad_label = await product.query_selector(".product-ad-label")  # Example class, needs verifying
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
            except Exception as e:
                print(f"Error extracting product: {e}")

        await browser.close()
        return data

async def main():
    all_data = []
    for url in BRAND_URLS:
        print(f"Scraping brand URL: {url}")
        brand_data = await scrape_brand(url)
        all_data.extend(brand_data)

    # Write CSV
    with open("myntra_brand_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "product_id","brand","product_name","image_url","selling_price",
            "mrp_price","discount_percent","rating","comment_count",
            "listing_type","source_page"
        ])
        writer.writeheader()
        writer.writerows(all_data)

    print(f"Scraped {len(all_data)} products from brand pages.")

if __name__ == "__main__":
    asyncio.run(main())
