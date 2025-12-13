import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio
import re

BASE_URL = "https://www.moneycontrol.com"
IPO_URL = "https://www.moneycontrol.com/ipo/"
UPCOMING_IPO_URL = "https://www.moneycontrol.com/ipo/upcoming-ipos/"


def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def parse_table(section):
    """Parse IPO tables (Active or Closed) from the page section."""
    if not section:
        return []
    
    rows = section.find_all("tr")[1:]  # Skip header row
    ipo_list = []

    for row in rows:
        cols = [col.get_text(strip=True) for col in row.find_all("td")]
        if len(cols) < 5:
            continue

        ipo_list.append({
            "company": cols[0],
            "issue_date": cols[1],
            "price_band": cols[2],
            "issue_size": cols[3],
            "gmp": cols[4] if len(cols) > 4 else None
        })

    return ipo_list


def get_active_ipos():
    html = fetch_html(IPO_URL)
    soup = BeautifulSoup(html, "html.parser")

    active_section = soup.find("div", id="mc_active")
    if not active_section:
        return []

    table = active_section.find("table")
    if not table:
        return []
    return parse_table(table)


def get_closed_ipos():
    html = fetch_html(UPCOMING_IPO_URL)
    soup = BeautifulSoup(html, "html.parser")

    closed_section = soup.find("div", id="mc_recent")
    if not closed_section:
        return []

    table = closed_section.find("table")
    if not table:
        return []
    return parse_table(table)


def _clean_html_for_llm(html: str) -> str:
    """
    Reduce tokens/noise for LLMs by removing scripts/styles and trimming whitespace.
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    cleaned = str(soup)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip()


async def get_all_upcoming_ipos_with_pagination(
    return_html: bool = False,
    clean_html: bool = True,
    max_clicks: int = 50,
    debug: bool = False,
):
   
    browser = None
    try:
        async with async_playwright() as p:
            # Launch browser in headless mode
            # In Docker, Chromium needs these flags to work properly
            # We use headless=True but add anti-detection flags and JS injection
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-software-rasterizer",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",  # Hide automation
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                ],
            )
            
            # Create a context with realistic browser fingerprint
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US",
                timezone_id="America/New_York",
                permissions=["geolocation"],
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Cache-Control": "max-age=0",
                },
            )
            
            page = await context.new_page()
            
            # Inject JavaScript to hide automation indicators
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override the plugins property to use a custom getter
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override the languages property to use a custom getter
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Override the permissions property to use a custom getter
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Mock chrome object
                window.chrome = {
                    runtime: {}
                };
            """)
            
            # Add a small delay to simulate human behavior
            await asyncio.sleep(1)
            
            # Navigate to the page with realistic referrer
            await page.goto(
                UPCOMING_IPO_URL,
                wait_until="domcontentloaded",
                referer="https://www.google.com/",
            )
            
            # Wait a bit more for JavaScript to execute
            await asyncio.sleep(2)

            # Wait for the section to exist (Moneycontrol renders parts dynamically)
            try:
                await page.wait_for_selector("div#UpcomingIpo", timeout=20000)
            except Exception:
                if debug:
                    try:
                        title = await page.title()
                        url = page.url
                        content_snippet = (await page.content())[:5000]
                        print(f"[scrap] UpcomingIpo not found. title={title!r} url={url!r}")
                        print(f"[scrap] Page HTML snippet (first 5k): {content_snippet}")
                    except Exception:
                        pass
                await context.close()
                await browser.close()
                if return_html:
                    return [], ""
                return []
            
            # Find the UpcomingIpo div
            target_div = page.locator("div#UpcomingIpo")

            print("target_div", await target_div.inner_text())
            if await target_div.count() == 0:
                await context.close()
                await browser.close()
                if return_html:
                    return [], ""
                return []

            # Ensure the section is in view (some sites render on scroll)
            try:
                await target_div.scroll_into_view_if_needed()
            except Exception:
                pass
            if debug:
                try:
                    snippet = (await target_div.inner_text())[:250]
                    print(f"[scrap] Found UpcomingIpo. Text snippet: {snippet!r}")
                except Exception:
                    pass

            # Click "Load More" until content stops growing
            for i in range(max_clicks):
                # Prefer a "Load More" inside the section; fallback to anywhere on the page
                load_more = target_div.locator(
                    "button, a",
                    has_text=re.compile(r"load\s*more", re.IGNORECASE),
                ).first
                if await load_more.count() == 0:
                    load_more = page.locator(
                        "button, a",
                        has_text=re.compile(r"load\s*more", re.IGNORECASE),
                    ).first

                if await load_more.count() == 0:
                    break
                if not await load_more.is_visible():
                    break

                before_len = len(await target_div.evaluate("el => el.innerHTML || ''"))

                try:
                    await load_more.scroll_into_view_if_needed()
                    await load_more.click(timeout=5000)
                except Exception:
                    break

                # Wait for DOM/network to settle; then verify content actually changed
                try:
                    await page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                await asyncio.sleep(1)

                after_len = len(await target_div.evaluate("el => el.innerHTML || ''"))
                if debug:
                    print(f"[scrap] click={i+1} before_len={before_len} after_len={after_len}")
                if after_len <= before_len + 50:
                    # No meaningful growth → likely no more items
                    break

            # Grab final DOM HTML (outerHTML) *after* JS has appended everything
            target_div_html = await target_div.evaluate("el => el.outerHTML || ''")
            await context.close()
            await browser.close()

            if clean_html:
                target_div_html = _clean_html_for_llm(target_div_html)

            # Parse IPO data (best-effort; some pages might not use a <table>)
            soup = BeautifulSoup(target_div_html, "html.parser")
            table = soup.find("table")
            ipos = parse_table(table) if table else []

            if return_html:
                return ipos, target_div_html
            return ipos
    except Exception as e:
        if browser:
            try:
                # Try to close context if it exists
                contexts = browser.contexts
                for ctx in contexts:
                    try:
                        await ctx.close()
                    except:
                        pass
                await browser.close()
            except:
                pass
        if debug:
            print(f"[scrap] Error in get_all_upcoming_ipos_with_pagination: {e}")
        if return_html:
            return [], ""
        return []


if __name__ == "__main__":
    print("Fetching Active IPOs...")
    active = get_active_ipos()
    for a in active:
        print(a)

    print("\nFetching Closed IPOs...")
    closed = get_closed_ipos()
    for c in closed:
        print(c)