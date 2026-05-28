from __future__ import annotations

import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/http_healthcheck.py <url>")
        return 2

    request = Request(sys.argv[1], headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:  # noqa: S310 - 部署健康检查只访问显式传入地址
            return 0 if 200 <= response.status < 300 else 1
    except (HTTPError, URLError):
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
