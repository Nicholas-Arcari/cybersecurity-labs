#!/usr/bin/env python3
"""
HTTP Security Header Analyzer - Cybersecurity Labs
Checks a target URL for missing or misconfigured security headers.
Useful during web recon (Module 03) to quickly assess a target's security posture.

Usage:
    python header_security_check.py https://target.com
    python header_security_check.py https://target.com --json
    python header_security_check.py -f urls.txt
"""

import sys
import json
import argparse
import urllib.request
import ssl
from urllib.error import URLError

SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "severity": "High",
        "description": "Enforces HTTPS connections (HSTS) - prevents SSL stripping attacks",
        "fix": "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
    },
    "Content-Security-Policy": {
        "severity": "High",
        "description": "Prevents XSS, clickjacking, and code injection attacks",
        "fix": "Content-Security-Policy: default-src 'self'; script-src 'self'",
    },
    "X-Content-Type-Options": {
        "severity": "Medium",
        "description": "Prevents MIME type sniffing - blocks polyglot attacks",
        "fix": "X-Content-Type-Options: nosniff",
    },
    "X-Frame-Options": {
        "severity": "Medium",
        "description": "Prevents clickjacking via iframe embedding",
        "fix": "X-Frame-Options: DENY",
    },
    "Referrer-Policy": {
        "severity": "Medium",
        "description": "Controls referrer information leakage to third parties",
        "fix": "Referrer-Policy: strict-origin-when-cross-origin",
    },
    "Permissions-Policy": {
        "severity": "Low",
        "description": "Restricts browser feature access (camera, microphone, geolocation)",
        "fix": "Permissions-Policy: camera=(), microphone=(), geolocation=()",
    },
    "X-XSS-Protection": {
        "severity": "Low",
        "description": "Legacy XSS filter - deprecated but still useful for older browsers",
        "fix": "X-XSS-Protection: 1; mode=block",
    },
    "Cross-Origin-Opener-Policy": {
        "severity": "Low",
        "description": "Isolates browsing context to prevent Spectre-type attacks",
        "fix": "Cross-Origin-Opener-Policy: same-origin",
    },
}

# Headers that leak server information
INFO_LEAK_HEADERS = [
    "Server",
    "X-Powered-By",
    "X-AspNet-Version",
    "X-AspNetMvc-Version",
    "X-Generator",
    "X-Drupal-Cache",
    "X-Varnish",
]

# Color codes
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
DIM = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"


def fetch_headers(url, timeout=10):
    """Fetch HTTP response headers from a URL."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "SecurityHeaderCheck/1.0"})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=timeout)
        return dict(resp.headers), resp.status
    except URLError:
        # Fallback to GET if HEAD is not allowed
        req = urllib.request.Request(url,
                                     headers={"User-Agent": "SecurityHeaderCheck/1.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=timeout)
        return dict(resp.headers), resp.status


def analyze_headers(url):
    """Analyze security headers for a given URL."""
    headers, status = fetch_headers(url)
    headers_lower = {k.lower(): (k, v) for k, v in headers.items()}

    result = {
        "url": url,
        "status_code": status,
        "missing": [],
        "present": [],
        "info_leak": [],
        "warnings": [],
    }

    # Check security headers
    for header, info in SECURITY_HEADERS.items():
        if header.lower() in headers_lower:
            orig_name, value = headers_lower[header.lower()]
            entry = {"header": orig_name, "value": value, **info}

            # Check for weak configurations
            if header == "Strict-Transport-Security":
                if "max-age=0" in value:
                    result["warnings"].append(f"HSTS max-age=0 disables protection")
            if header == "X-Frame-Options" and value.upper() == "ALLOWALL":
                result["warnings"].append(f"X-Frame-Options: ALLOWALL provides no protection")

            result["present"].append(entry)
        else:
            result["missing"].append({"header": header, **info})

    # Check information disclosure
    for leak_header in INFO_LEAK_HEADERS:
        if leak_header.lower() in headers_lower:
            orig_name, value = headers_lower[leak_header.lower()]
            result["info_leak"].append({"header": orig_name, "value": value})

    # Calculate score
    total = len(SECURITY_HEADERS)
    present = len(result["present"])
    result["score"] = int((present / total) * 100) if total > 0 else 0

    return result


def print_report(result):
    """Print a formatted terminal report."""
    score = result["score"]
    score_color = GREEN if score >= 75 else YELLOW if score >= 50 else RED

    print(f"\n{BOLD}{'='*65}{RESET}")
    print(f"  {BOLD}Security Header Analysis{RESET}: {result['url']}")
    print(f"  HTTP Status: {result['status_code']} | "
          f"Score: {score_color}{score}%{RESET} ({len(result['present'])}/{len(SECURITY_HEADERS)})")
    print(f"{BOLD}{'='*65}{RESET}\n")

    # Missing headers (sorted by severity)
    if result["missing"]:
        sev_order = {"High": 0, "Medium": 1, "Low": 2}
        missing_sorted = sorted(result["missing"], key=lambda x: sev_order.get(x["severity"], 3))
        print(f"  {RED}{BOLD}MISSING HEADERS:{RESET}\n")
        for m in missing_sorted:
            sev_color = RED if m["severity"] == "High" else YELLOW if m["severity"] == "Medium" else DIM
            print(f"  {sev_color}[{m['severity']}]{RESET} {m['header']}")
            print(f"    {DIM}{m['description']}{RESET}")
            print(f"    {CYAN}Fix: {m['fix']}{RESET}\n")

    # Information disclosure
    if result["info_leak"]:
        print(f"  {YELLOW}{BOLD}INFORMATION DISCLOSURE:{RESET}\n")
        for h in result["info_leak"]:
            print(f"  {YELLOW}[-]{RESET} {h['header']}: {h['value']}")
        print(f"  {DIM}Recommendation: remove or obfuscate these headers in production{RESET}\n")

    # Warnings
    if result["warnings"]:
        print(f"  {YELLOW}{BOLD}WARNINGS:{RESET}\n")
        for w in result["warnings"]:
            print(f"  {YELLOW}[!]{RESET} {w}")
        print()

    # Present headers
    if result["present"]:
        print(f"  {GREEN}{BOLD}PRESENT HEADERS:{RESET}\n")
        for p in result["present"]:
            print(f"  {GREEN}[OK]{RESET} {p['header']}: {p['value'][:80]}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="HTTP Security Header Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s https://example.com\n"
               "  %(prog)s https://example.com --json\n"
               "  %(prog)s -f targets.txt\n"
    )
    parser.add_argument("url", nargs="?", help="Target URL to analyze")
    parser.add_argument("-f", "--file", help="File with URLs (one per line)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    args = parser.parse_args()

    urls = []
    if args.file:
        with open(args.file) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    elif args.url:
        urls = [args.url]
    else:
        parser.print_help()
        sys.exit(1)

    all_results = []
    for url in urls:
        try:
            result = analyze_headers(url)
            all_results.append(result)
            if not args.json:
                print_report(result)
        except Exception as e:
            if args.json:
                all_results.append({"url": url, "error": str(e)})
            else:
                print(f"\n  {RED}[ERROR]{RESET} {url}: {e}\n")

    if args.json:
        output = all_results[0] if len(all_results) == 1 else all_results
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
