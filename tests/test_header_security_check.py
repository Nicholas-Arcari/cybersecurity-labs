"""Tests for header_security_check.py - HTTP security header analyzer."""

import pytest
from unittest.mock import patch, MagicMock

from header_security_check import analyze_headers, SECURITY_HEADERS, INFO_LEAK_HEADERS


def _mock_headers(headers_dict, status=200):
    """Create a mock response with given headers."""
    mock_resp = MagicMock()
    mock_resp.headers = headers_dict
    mock_resp.status = status
    return mock_resp


class TestAnalyzeHeaders:
    """Tests for the analyze_headers function."""

    @patch("header_security_check.fetch_headers")
    def test_all_headers_present(self, mock_fetch):
        mock_fetch.return_value = ({
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=()",
            "X-XSS-Protection": "1; mode=block",
            "Cross-Origin-Opener-Policy": "same-origin",
        }, 200)

        result = analyze_headers("https://example.com")
        assert result["score"] == 100
        assert len(result["missing"]) == 0
        assert len(result["present"]) == 8

    @patch("header_security_check.fetch_headers")
    def test_no_headers(self, mock_fetch):
        mock_fetch.return_value = ({}, 200)

        result = analyze_headers("https://example.com")
        assert result["score"] == 0
        assert len(result["missing"]) == len(SECURITY_HEADERS)
        assert len(result["present"]) == 0

    @patch("header_security_check.fetch_headers")
    def test_partial_headers(self, mock_fetch):
        mock_fetch.return_value = ({
            "Strict-Transport-Security": "max-age=31536000",
            "X-Content-Type-Options": "nosniff",
        }, 200)

        result = analyze_headers("https://example.com")
        assert result["score"] == 25  # 2/8 = 25%
        assert len(result["present"]) == 2
        assert len(result["missing"]) == 6

    @patch("header_security_check.fetch_headers")
    def test_info_leak_detection(self, mock_fetch):
        mock_fetch.return_value = ({
            "Server": "Apache/2.4.41 (Ubuntu)",
            "X-Powered-By": "PHP/5.6.40",
        }, 200)

        result = analyze_headers("https://example.com")
        assert len(result["info_leak"]) == 2
        leak_headers = [h["header"] for h in result["info_leak"]]
        assert "Server" in leak_headers
        assert "X-Powered-By" in leak_headers

    @patch("header_security_check.fetch_headers")
    def test_hsts_max_age_zero_warning(self, mock_fetch):
        mock_fetch.return_value = ({
            "Strict-Transport-Security": "max-age=0",
        }, 200)

        result = analyze_headers("https://example.com")
        assert len(result["warnings"]) >= 1
        assert any("max-age=0" in w for w in result["warnings"])

    @patch("header_security_check.fetch_headers")
    def test_xfo_allowall_warning(self, mock_fetch):
        mock_fetch.return_value = ({
            "X-Frame-Options": "ALLOWALL",
        }, 200)

        result = analyze_headers("https://example.com")
        assert any("ALLOWALL" in w for w in result["warnings"])

    @patch("header_security_check.fetch_headers")
    def test_url_preserved(self, mock_fetch):
        mock_fetch.return_value = ({}, 200)
        result = analyze_headers("https://target.local:8080")
        assert result["url"] == "https://target.local:8080"

    @patch("header_security_check.fetch_headers")
    def test_status_code_preserved(self, mock_fetch):
        mock_fetch.return_value = ({}, 301)
        result = analyze_headers("https://example.com")
        assert result["status_code"] == 301


class TestSecurityHeadersConfig:
    """Tests for the SECURITY_HEADERS configuration."""

    def test_all_headers_have_required_fields(self):
        for header, info in SECURITY_HEADERS.items():
            assert "severity" in info, f"{header} missing severity"
            assert "description" in info, f"{header} missing description"
            assert "fix" in info, f"{header} missing fix"

    def test_valid_severities(self):
        valid = {"High", "Medium", "Low"}
        for header, info in SECURITY_HEADERS.items():
            assert info["severity"] in valid, f"{header} has invalid severity: {info['severity']}"

    def test_info_leak_headers_are_strings(self):
        for header in INFO_LEAK_HEADERS:
            assert isinstance(header, str)
            assert len(header) > 0
