"""Tests for proxy URL normalization and parsing."""
from __future__ import annotations

from backend.utils.proxy import build_proxy_dict, normalize_proxy_url


class TestNormalizeProxyUrl:
    """normalize_proxy_url removes whitespace, infers socks5://, handles IPv6."""

    def test_empty_string(self):
        assert normalize_proxy_url("") == ""
        assert normalize_proxy_url("  ") == ""

    def test_already_full_url(self):
        assert normalize_proxy_url("socks5://127.0.0.1:1080") == "socks5://127.0.0.1:1080"
        assert normalize_proxy_url("http://127.0.0.1:7890") == "http://127.0.0.1:7890"
        assert normalize_proxy_url("socks5://user:pass@192.168.1.1:9050") == "socks5://user:pass@192.168.1.1:9050"

    def test_bare_host_port(self):
        result = normalize_proxy_url("127.0.0.1:1080")
        assert result == "socks5://127.0.0.1:1080"

    def test_host_port_credentials(self):
        """user:pass@host:port format (no scheme) → socks5://user:pass@host:port."""
        result = normalize_proxy_url("user:pass@127.0.0.1:1080")
        assert result == "socks5://user:pass@127.0.0.1:1080"

    def test_bracketed_ipv6_with_port(self):
        result = normalize_proxy_url("[::1]:1080")
        assert result == "socks5://[::1]:1080"

    def test_bare_ipv6_no_port(self):
        result = normalize_proxy_url("::1")
        assert result == "socks5://[::1]"

    def test_bracketed_ipv6_no_port(self):
        result = normalize_proxy_url("[::1]")
        assert result == "socks5://[::1]"

    def test_long_ipv6_with_port(self):
        result = normalize_proxy_url("[2001:db8::1]:9050")
        assert result == "socks5://[2001:db8::1]:9050"

    def test_whitespace_trimmed(self):
        result = normalize_proxy_url("  socks5://10.0.0.1:3128  ")
        assert result == "socks5://10.0.0.1:3128"


class TestBuildProxyDict:
    """build_proxy_dict returns None for invalid / empty and a dict for valid."""

    def test_empty_returns_none(self):
        assert build_proxy_dict("") is None
        assert build_proxy_dict("  ") is None

    def test_valid_socks5(self):
        result = build_proxy_dict("127.0.0.1:1080")
        assert result == {
            "scheme": "socks5",
            "hostname": "127.0.0.1",
            "port": 1080,
        }

    def test_with_credentials(self):
        result = build_proxy_dict("user:pass@proxy.example.com:9050")
        assert result == {
            "scheme": "socks5",
            "hostname": "proxy.example.com",
            "port": 9050,
            "username": "user",
            "password": "pass",
        }

    def test_ipv6(self):
        result = build_proxy_dict("[::1]:1080")
        assert result == {
            "scheme": "socks5",
            "hostname": "::1",
            "port": 1080,
        }

    def test_http_proxy(self):
        result = build_proxy_dict("http://10.0.0.1:8080")
        assert result == {
            "scheme": "http",
            "hostname": "10.0.0.1",
            "port": 8080,
        }