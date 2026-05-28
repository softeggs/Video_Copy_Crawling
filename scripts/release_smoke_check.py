from __future__ import annotations

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch(url: str) -> tuple[int, str]:
    request = Request(url, headers={"Accept": "application/json,text/html"})
    with urlopen(request, timeout=10) as response:  # noqa: S310 - 运维 smoke check 仅访问显式传入地址
        body = response.read(200).decode("utf-8", errors="replace")
        return response.status, body


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: python scripts/release_smoke_check.py <backend_health_url> <web_url> <debug_url>")
        return 2

    checks = [
        ("backend-health", sys.argv[1]),
        ("web-console", sys.argv[2]),
        ("debug-console", sys.argv[3]),
    ]

    results: list[dict[str, str | int]] = []
    failed = False

    for name, url in checks:
        try:
            status, preview = fetch(url)
            results.append({"name": name, "url": url, "status": status, "preview": preview[:120]})
            if not (200 <= status < 300):
                failed = True
        except (HTTPError, URLError, TimeoutError) as exc:
            failed = True
            results.append({"name": name, "url": url, "status": "error", "preview": str(exc)})

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
