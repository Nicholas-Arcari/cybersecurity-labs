> **English** | [Italiano](README.md)

# 04 - CMS specific

> - **Phase:** Web Attack - CMS Fingerprinting & Targeted Exploitation
> - **Visibility:** Medium - HTTP requests with CMS-specific payloads
> - **Prerequisites:** CMS identified during the tech profiling phase (`02-web-recon/tech-profiler/`), version confirmed
> - **Output:** Finding WEB-015 (Drupal RCE), user and plugin enumeration (WordPress, Joomla), CMS-specific report

---

## Introduction

When the target runs a well-known Content Management System (CMS), the strategy changes radically compared to generic attacks: each CMS has its own vulnerability patterns, dedicated enumeration tools, and specific exploit databases.

Reasons why CMSs are priority targets in penetration tests:

- **Wide attack surface:** a CMS is a complex application with many components (core, plugins, themes, REST API). Each one is a potential entry point.
- **Outdated versions:** automatic updates are often disabled in production (fear of breaking changes). Unpatched installations remain exposed for months or years.
- **Third-party plugins:** most vulnerabilities in WordPress, for example, are not in the core but in plugins. A single installation may have dozens of unmonitored plugins.
- **Default credentials:** many CMSs have predictable default usernames (`admin`) and weak passwords that were never changed after installation.
- **Exposed files:** CMSs often leave configuration or versioning files publicly accessible (`CHANGELOG.txt`, `README.txt`, `wp-config.php.bak`).

The fingerprinting phase (identifying the CMS and its version) is the prerequisite: there is no point using WPScan on a Joomla target.

---

## Folder structure

```
04-cms-specific/
+-- drupal/      # CVE-2018-7600 Drupalgeddon2 RCE - finding WEB-015
+-- wordpress/   # WPScan: user enumeration, plugins, brute force
+-- joomla/      # JoomScan: fingerprinting, CVE-2023-23752
```

---

## Fingerprinting: how to identify the CMS

Before choosing the correct tool, it is necessary to identify the CMS. The revealing indicators:

| indicator | wordpress | joomla | drupal |
| :--- | :--- | :--- | :--- |
| resource path | `/wp-content/`, `/wp-admin/` | `/administrator/`, `/components/` | `/sites/`, `/modules/` |
| cookie | `wordpress_`, `wp-settings-` | `joomla_user_state` | `Drupal.visitor` |
| meta tag | `<meta name="generator" content="WordPress...">` | `<meta name="generator" content="Joomla!...">` | `<meta name="Generator" content="Drupal...">` |
| version file | `/readme.html`, `/wp-login.php` | `/CHANGELOG.txt` | `/CHANGELOG.txt`, `/core/CHANGELOG.txt` |
| http response | header `X-Pingback` | - | - |

Automated fingerprinting tools:
- `whatweb -v <TARGET>`: identifies the CMS and its version.
- `wappalyzer` (browser): immediate visual fingerprinting.
- `nuclei -u <TARGET> -t cms/`: CMS-specific nuclei templates.

---

## `drupal/` - Drupalgeddon2 (CVE-2018-7600)

**Finding ID:** `WEB-015` | **Severity:** `Critical` | **CVSS v3.1:** 9.8

### Operational context

Drupal is an enterprise-grade CMS used by governments, universities, and large corporations. CVE-2018-7600, nicknamed "Drupalgeddon2", is an unauthenticated Remote Code Execution in the Form API. Drupal versions 6.x, 7.x (before 7.58), and 8.x (before 8.3.9, 8.4.6, 8.5.1) are vulnerable.

The exploitation documented in `drupal/README.md` produced:
- Access to the Drupal administrative dashboard.
- Deployment of a PHP Web Shell hidden as a content page.
- Execution of Windows commands (`ipconfig`) through the Web Shell, confirming total server control.

The distinctive aspect of this test was the manual bypass of Windows Defender: automated exploits generate signatures detectable by the antivirus, making a manual approach necessary through standard PHP payloads from Drupal's "PHP Filter" module.

---

## `wordpress/` - WPScan & WordPress exploitation

### Operational context

WordPress holds approximately 43% of the global CMS market share, making it the most common target in web application pentesting. WPScan is the dedicated tool: a black-box security scanner specifically designed for WordPress.

The main phases of a WordPress test:

1. **Fingerprinting:** confirm the WordPress version and the active theme.
2. **Plugin enumeration:** identify all installed plugins and their versions (`--enumerate p`).
3. **User enumeration:** retrieve user usernames (`--enumerate u`).
4. **CVE verification:** check whether the plugins/themes/core version have known CVEs.
5. **Brute Force:** if the `/wp-login.php` page is accessible and not protected by CAPTCHA/2FA, perform password guessing.

See `wordpress/README.md` for the complete technical guide with commands and output.

---

## `joomla/` - JoomScan & joomla exploitation

### Operational context

Joomla is the second most widespread CMS, with a significant presence in institutional and governmental environments. JoomScan (OWASP) is the dedicated scanner for enumerating components, plugins, and known vulnerabilities.

CVE-2023-23752 is an unauthenticated information disclosure vulnerability that allows access to database configurations (host, username, password) through Joomla's REST API. The vulnerable endpoint is `/api/index.php/v1/config/application?public=true`.

See `joomla/README.md` for the complete technical guide with commands and output.

---

## Recommended operational flow

```
[1] CMS Fingerprinting (02-web-recon/tech-profiler/)
     +-- whatweb -v <TARGET> -> identifies CMS and version
     +-- nuclei -u <TARGET> -t cms/ -> checks for specific CVEs
              |
              v
[2] WordPress?
     +-- wpscan --url <TARGET> --enumerate vp,vt,u
     +-- wpscan --url <TARGET> -U users.txt -P rockyou.txt
              |
       Joomla?
     +-- joomscan -u <TARGET>
     +-- curl /api/index.php/v1/config/application?public=true (CVE-2023-23752)
              |
       Drupal?
     +-- check version via /CHANGELOG.txt
     +-- if 7.x < 7.58 -> CVE-2018-7600 Drupalgeddon2
              |
              v
[3] Post-Exploitation
     +-- admin access -> upload Web Shell
     +-- database credential dump
     +-- lateral movement
```

---

## Reference tools

| tool | type | technique/access | primary use case |
| :--- | :--- | :--- | :--- |
| `wpscan` | wordpress scanner | cli - active | wordpress plugin, user, and cve enumeration |
| `joomscan` | joomla scanner | cli - active | joomla fingerprinting and cve detection |
| `droopescan` | cms scanner | cli - active | drupal, silverstripe, wordpress scanning |
| `cmsmap` | multi-cms scanner | cli - active | general-purpose scanner for wordpress, joomla, drupal |
| `nuclei` | template-based | cli - active | community-maintained cms-specific templates |
| `metasploit` | exploitation framework | cli/gui - active | automated exploits for known cms cves |
| `curl` | http client | cli - active | manual cms api endpoint testing (CVE-2023-23752) |

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning: vulnerability scanning | `T1595.002` | drupal version fingerprinting via `CHANGELOG.txt` and identification of CVE-2018-7600 |
| initial access | exploit public-facing application | `T1190` | exploitation of CVE-2018-7600 (drupalgeddon2) on the form api to achieve unauthenticated rce (WEB-015) |
| persistence | server software component: web shell | `T1505.003` | php web shell deployment through drupal's "php filter" module in a content node (WEB-015) |
| discovery | file and directory discovery | `T1083` | windows server file system enumeration through commands injected via the web shell |
| credential access | brute force: password guessing | `T1110.001` | brute force on `/wp-login.php` with wpscan (wordpress) |
| discovery | account discovery | `T1087` | wordpress user enumeration with `--enumerate u` (wpscan) |

---

> **Note:** The CVE-2018-7600 test (WEB-015) was conducted on a Drupal 7.54 instance installed
> locally on a Windows 10 virtual machine specifically configured for educational purposes.
> WPScan and JoomScan activities were conducted in authorized lab environments.
> Exploiting known CVEs on production instances without authorization is a criminal offense.
