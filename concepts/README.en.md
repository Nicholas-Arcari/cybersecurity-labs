> **English** | [Italiano](README.md)

# Concepts and background knowledge

> - **Nature:** background-knowledge pages, not techniques tied to a penetration-test phase.
> - **Angle:** conceptual and educational, with emphasis on classification, mechanism and defense (detection/mitigation).
> - **Purpose:** provide the theoretical context that the operational modules (00-11) take for granted.

## Introduction

The numbered modules (`00`-`11`) document the penetration test by phase, with techniques, commands and findings.
This area instead collects the **cross-cutting concepts** those modules presuppose: what the malware categories
are, how a denial-of-service attack works, and the like. They are textbook pages, not lab pages: they serve to
frame the terminology and the mechanism, with attention to the defensive side (how it is detected and mitigated),
consistently with the repository's dual (offensive + defensive) nature.

## Folder structure

| subfolder | theme | angle |
| :--- | :--- | :--- |
| `malware-taxonomy/` | malware taxonomy: virus, worm, trojan, rat, botnet, ransomware, rootkit, wiper, loader, spyware/keylogger | classification + mitre + detection |
| `ddos/` | denial of service and ddos: volumetric, protocol, application; amplification/reflection; botnets | mechanism + mitigation (conceptual) |

## Scope note

These pages are **explanatory**: they describe categories and mechanisms and how to defend. They do not contain
functional malware or ready-to-use DoS attack tools; where useful they point to the repository's operational
modules (e.g., [07-post-exploitation](<../07-post-exploitation/README.en.md>) for credential dumping,
[08-defense-hardenings](<../08-defense-hardenings (Blue Team Prevention)/README.en.md>) for detection and defense).

---

> **Note:** Educational and background-knowledge content. No offensive payloads: these are conceptual pages.
