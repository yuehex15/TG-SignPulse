from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlparse

# IPv6 literal inside brackets, e.g. [::1]:8080 or socks5://[::1]:1080
_IPV6_BRACKETED = re.compile(r"^\[([0-9a-fA-F:.]+)\](?::(\d+))?$")


def normalize_proxy_url(raw: str) -> str:
    value = raw.strip()
    if not value:
        return value
    if "://" in value:
        return value
    if "@" in value:
        return f"socks5://{value}"
    # Bracketed IPv6 literal, e.g. [::1]:8080
    ipv6_match = _IPV6_BRACKETED.match(value)
    if ipv6_match:
        host, port = ipv6_match.groups()
        suffix = f":{port}" if port else ""
        return f"socks5://[{host}]{suffix}"
    # Bare IPv6 literal without brackets and without port, e.g. ::1
    if value.count(":") > 1 and "]" not in value:
        return f"socks5://[{value}]"
    parts = value.split(":")
    if len(parts) == 2:
        host, port = parts
        return f"socks5://{host}:{port}"
    if len(parts) == 4:
        host, port, user, password = parts
        return f"socks5://{user}:{password}@{host}:{port}"
    return f"socks5://{value}"


def build_proxy_dict(raw: str) -> Optional[dict]:
    value = normalize_proxy_url(raw)
    if not value:
        return None
    parsed = urlparse(value)
    if not (parsed.scheme and parsed.hostname and parsed.port):
        return None
    proxy = {
        "scheme": parsed.scheme,
        "hostname": parsed.hostname,
        "port": parsed.port,
    }
    if parsed.username:
        proxy["username"] = parsed.username
    if parsed.password:
        proxy["password"] = parsed.password
    return proxy
