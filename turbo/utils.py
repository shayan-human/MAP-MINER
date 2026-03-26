import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

def get_random_ua():
    return random.choice(USER_AGENTS)

def parse_proxies(proxy_string):
    """
    Parses a comma-separated string of proxies.
    Supports formats:
    - http://user:pass@host:port
    - host:port
    - host:port:user:pass
    - user:pass:host:port
    """
    if not proxy_string:
        return []
    
    # Handle both comma and newline separators
    proxy_string = proxy_string.replace("\n", ",").replace("\r", ",")
    raw_proxies = [p.strip() for p in proxy_string.split(",") if p.strip()]
    parsed = []
    
    for p in raw_proxies:
        if "://" in p:
            parsed.append(p)
            continue
            
        # Handle colon-separated formats only if no protocol is present
        parts = p.split(":")
        if len(parts) == 4:
            # user:pass:host:port
            if parts[3].isdigit():
                p = f"http://{parts[0]}:{parts[1]}@{parts[2]}:{parts[3]}"
            # host:port:user:pass
            elif parts[1].isdigit():
                p = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
            else:
                p = "http://" + p
        else:
            p = "http://" + p
            
        parsed.append(p)
    return parsed

class ProxyManager:
    def __init__(self, proxies):
        self.proxies = [p for p in proxies if self._is_valid(p)]
        self.index = 0

    def _is_valid(self, proxy_url):
        """Basic validation for proxy URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            return all([parsed.scheme, parsed.hostname])
        except:
            return False

    def get_next(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.index]
        self.index = (self.index + 1) % len(self.proxies)
        return proxy

    def get_playwright_proxy(self):
        """Returns proxy in format suitable for Playwright browser context."""
        proxy_url = self.get_next()
        if not proxy_url:
            return None
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            # Playwright expects 'server' as 'host:port' or 'scheme://host:port'
            port = parsed.port if parsed.port else (80 if parsed.scheme == 'http' else 443)
            pw_proxy = {"server": f"{parsed.scheme}://{parsed.hostname}:{port}"}
            
            if parsed.username:
                pw_proxy["username"] = parsed.username
            if parsed.password:
                pw_proxy["password"] = parsed.password
            return pw_proxy
        except Exception as e:
            print(f"Error parsing proxy for Playwright: {e}")
            return None


async def validate_proxy(proxy_url, timeout=15):
    """
    Validates a single proxy by testing HTTP connectivity and browser-level.
    Returns: {"valid": bool, "ip": str or None, "error": str or None}
    """
    import httpx
    
    http_valid = False
    browser_valid = False
    detected_ip = None
    error_msg = None
    
    # Test 1: HTTP connectivity via httpx
    try:
        async with httpx.AsyncClient(proxy=proxy_url, timeout=timeout, verify=False) as client:
            resp = await client.get("https://api.ipify.org", timeout=timeout)
            if resp.status_code == 200:
                http_valid = True
                detected_ip = resp.text.strip()
    except Exception as e:
        error_msg = f"HTTP test failed: {type(e).__name__}: {str(e)}"
    
    # Test 2: Browser-level connectivity via Playwright
    if http_valid:
        from playwright.async_api import async_playwright
        try:
            async with async_playwright() as p:
                proxy_config = _parse_proxy_for_playwright(proxy_url)
                if proxy_config:
                    browser = await p.chromium.launch(headless=True, proxy=proxy_config)
                    await browser.close()
                    browser_valid = True
                else:
                    error_msg = "Failed to parse proxy for browser"
        except Exception as e:
            error_msg = f"Browser test failed: {type(e).__name__}: {str(e)}"
    
    valid = http_valid and browser_valid
    return {"valid": valid, "ip": detected_ip, "error": error_msg if not valid else None}


def _parse_proxy_for_playwright(proxy_url):
    """Parse proxy URL into Playwright format."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(proxy_url)
        port = parsed.port if parsed.port else (80 if parsed.scheme == 'http' else 443)
        pw_proxy = {"server": f"{parsed.scheme}://{parsed.hostname}:{port}"}
        
        if parsed.username:
            pw_proxy["username"] = parsed.username
        if parsed.password:
            pw_proxy["password"] = parsed.password
        return pw_proxy
    except:
        return None


async def validate_proxies_batch(proxy_list, timeout=15):
    """
    Validates a batch of proxies.
    Returns: {"working": [...], "failed": [(proxy, error), ...]}
    """
    import asyncio
    
    working = []
    failed = []
    
    async def test_one(proxy_url):
        result = await validate_proxy(proxy_url, timeout)
        return proxy_url, result
    
    tasks = [test_one(p) for p in proxy_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for r in results:
        if isinstance(r, Exception):
            continue
        proxy_url, result = r
        if result["valid"]:
            working.append({"proxy": proxy_url, "ip": result["ip"]})
        else:
            failed.append({"proxy": proxy_url, "error": result["error"]})
    
    return {"working": working, "failed": failed}
