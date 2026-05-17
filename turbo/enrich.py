import asyncio
import random
import re
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_random_ua():
    return random.choice(USER_AGENTS)

_JUNK_PATTERNS = [
    'example@', '@example.', 'your@email', 'info@example',
    'team@latofonts', 'filler@godaddy', 'impallari@gmail',
    'sentry', 'wixpress', 'noreply', 'no-reply', '@domain.com',
    '@sentry.', '@wix.', 'webpack', 'cloudflare', '@test.',
    'username@', 'user@', 'email@email', 'name@', 'sample@',
]

_EXCLUDED_EXTS = (
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',
    '.pdf', '.zip', '.css', '.js', '.woff', '.woff2',
    '.ttf', '.eot', '.ico', '.mp4', '.mp3',
)


def _deobfuscate_text(text):
    text = re.sub(r'\s*[\[\(\{]\s*at\s*[\]\)\}]\s*', '@', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*[\[\(\{]\s*dot\s*[\]\)\}]\s*', '.', text, flags=re.IGNORECASE)
    return text


def extract_emails_from_html(html):
    """Extract emails from HTML using multiple methods."""
    emails = set()
    if not html:
        return emails
    
    text = _deobfuscate_text(html)
    email_pattern = r'[a-zA-Z0-9._%+\-]+@(?![a-zA-Z0-9.\-]*\.(?:png|jpg|jpeg|gif|svg|webp|pdf|zip|gz|tar|mp4|mp3|exe|dll|bin|iso|css|js|woff|woff2|ttf|eot|ico))[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    
    for e in re.findall(email_pattern, text):
        e_low = e.lower().strip('.')
        if any(e_low.endswith(ext) for ext in _EXCLUDED_EXTS):
            continue
        if any(junk in e_low for junk in _JUNK_PATTERNS):
            continue
        parts = e_low.split('@')
        if len(parts) != 2:
            continue
        domain = parts[1]
        if '.' not in domain or len(domain) < 4:
            continue
        emails.add(e_low)
    
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href'].strip().lower()
        if href.startswith('mailto:'):
            raw = href[7:].split('?')[0].strip()
            if raw and '@' in raw:
                emails.add(raw.lower())
    
    for tag in soup.find_all(attrs={'data-email': True}):
        found = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', tag['data-email'])
        emails.update(e.lower() for e in found)
    
    return emails


def find_contact_links(html, base_url):
    """Find contact and social links from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    contact_links = set()
    social_links = set()
    
    noise_keywords = ['privacy', 'terms', 'legal', 'policy', 'tos', 'disclaimer', 'cookies', 'login', 'signup', 'cart', 'checkout']
    contact_keywords = ['contact', 'about', 'team', 'staff', 'reach', 'info', 'support', 'connect', 'get-in-touch', 'enquiry', 'inquiry']
    social_platforms = ['facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com', 'x.com', 'youtube.com', 'tiktok.com']
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text().lower().strip()
        href_low = href.lower()
        
        if href_low.startswith(('mailto:', 'tel:', 'javascript:', '#')):
            continue
        
        if any(platform in href_low for platform in social_platforms):
            social_links.add(href)
            continue
        
        if any(nk in href_low or nk in text for nk in noise_keywords):
            continue
        
        if any(kw in text for kw in contact_keywords) or any(kw in href_low for kw in contact_keywords):
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                contact_links.add(full_url)
    
    return list(contact_links), list(social_links)


COMMON_CONTACT_PATHS = [
    '/contact', '/contact-us', '/contactus', '/contact.html', '/contact.htm', '/contact.php', '/contact/index', '/contact-us/',
    '/about', '/about-us', '/aboutus', '/about.html', '/about.htm', '/about-us.html', '/aboutus.html',
    '/team', '/our-team', '/staff', '/our-team.html',
    '/support', '/help', '/help-center',
    '/get-in-touch', '/contact-us.html', '/contact-us.htm', '/get-in-touch.html',
    '/contact-us/', '/contact/index.html', '/contactus.html', '/contact.php',
    '/about-us/', '/about.html', '/about-us.htm', '/about/index',
    '/team.html', '/team.htm', '/staff.html', '/staff.htm',
]


async def fetch_page_content(page, url):
    """Fetch page content using Playwright with JS rendering."""
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        if response and response.status == 200:
            await asyncio.sleep(0.5)
            return await page.content()
    except Exception:
        pass
    return None


async def enrich_with_playwright(browser, business_data, limit=0):
    """Enrich business data using Playwright for JS rendering."""
    website = business_data.get('website')
    if not website or not isinstance(website, str):
        # Preserve Maps email if no website
        if business_data.get('emails'):
            return business_data
        if 'emails' not in business_data:
            business_data['emails'] = []
        return business_data
    
    if not website.startswith(('http://', 'https://')):
        website = 'https://' + website
    
    emails = set()
    socials = set()
    
    # Include email from Maps listing if available
    if business_data.get('email'):
        emails.add(business_data['email'].lower())
    
    context = await browser.new_context(user_agent=get_random_ua())
    page = await context.new_page()
    page.set_default_timeout(20000)
    
    await page.route("**/*.{png,jpg,jpeg,svg,webp,gif,css,woff,woff2,ttf,pdf,js}", lambda route: route.abort())
    
    try:
        html = await fetch_page_content(page, website)
        if html:
            page_emails = extract_emails_from_html(html)
            emails.update(page_emails)
            
            contact_links, social_links = find_contact_links(html, website)
            socials.update(social_links)
            
            for link in list(set(contact_links))[:4]:
                if len(emails) >= limit > 0:
                    break
                await asyncio.sleep(random.uniform(0.2, 0.4))
                sub_html = await fetch_page_content(page, link)
                if sub_html:
                    sub_emails = extract_emails_from_html(sub_html)
                    emails.update(sub_emails)
        
        if not html:
            base_domain = f"{urlparse(website).scheme}://{urlparse(website).netloc}"
            for path in COMMON_CONTACT_PATHS[:4]:
                if len(emails) >= limit > 0:
                    break
                await asyncio.sleep(random.uniform(0.3, 0.6))
                fb_html = await fetch_page_content(page, base_domain + path)
                if fb_html:
                    fb_emails = extract_emails_from_html(fb_html)
                    emails.update(fb_emails)
                    if fb_emails:
                        break
    except Exception:
        pass
    finally:
        await page.close()
        await context.close()
    
    clean_emails = [e for e in emails if not any(junk in e for junk in _JUNK_PATTERNS)]
    final_emails = list(set(clean_emails))[:limit] if limit > 0 else list(set(clean_emails))
    
    business_data['emails'] = final_emails
    business_data['socials'] = "; ".join(list(socials))
    return business_data


async def enrich_business(business_data, proxies=None, limit=0, strict_mode=False, shared_browser=None):
    """Main enrichment function using Playwright.
    
    Args:
        shared_browser: Optional pre-launched browser instance to reuse.
                       When provided, the browser will NOT be closed after enrichment.
                       This dramatically reduces memory usage for batch operations.
    """
    if shared_browser:
        return await enrich_with_playwright(shared_browser, business_data, limit)
    
    # Standalone mode: launch and close our own browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        result = await enrich_with_playwright(browser, business_data, limit)
        await browser.close()
        return result


async def create_shared_browser():
    """Create a shared browser instance for batch enrichment.
    
    Usage:
        pw, browser = await create_shared_browser()
        try:
            # ... enrich multiple businesses with shared_browser=browser
        finally:
            await browser.close()
            await pw.stop()
    """
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    )
    return pw, browser


if __name__ == "__main__":
    test_data = {"name": "Test Business", "website": "https://example.com"}
    result = asyncio.run(enrich_business(test_data))
    print(result)