"""Polite HTTP helper: identifies itself, retries gently, pauses between calls."""
import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PublicSectorRoleScanner/1.0; weekly digest)",
    "Accept-Language": "en-GB,en;q=0.9",
}
_session = requests.Session()
_session.headers.update(HEADERS)


def get(url, params=None, timeout=30, pause=1.0, retries=3):
    last = None
    for attempt in range(retries):
        try:
            r = _session.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                time.sleep(pause)
                return r
            last = RuntimeError(f"HTTP {r.status_code} for {r.url}")
            if r.status_code in (403, 404):
                break
        except requests.RequestException as e:
            last = e
        time.sleep(2 * (attempt + 1))
    raise last
