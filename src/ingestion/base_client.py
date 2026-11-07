"""Resilient HTTP client with retry backoff and rate-limiting."""
import logging
import random
import time
from typing import Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
]


class BasePublicClient:
    """HTTP client wrapper configured for public financial data endpoints."""

    def __init__(
        self,
        base_url: str = "",
        timeout_seconds: int = 20,
        rate_limit_delay: float = 0.5,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()

        retries = Retry(
            total=max_retries,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def get(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint
        time.sleep(self.rate_limit_delay)
        req_headers = self._get_headers(headers)
        logger.debug("GET %s (params: %s)", url, params)
        resp = self.session.get(url, params=params, headers=req_headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp
