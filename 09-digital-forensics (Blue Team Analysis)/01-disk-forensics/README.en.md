> **English** | [Italiano](README.md)

# Disk Forensics - Acquisition, Timeline and Artifact Recovery

> - **Phase:** Digital Forensics & Incident Response - Disk & Memory Analysis
> - **Category:** Analysis - post-incident reconstruction from disk evidence
> - **Prerequisites:** Access to the medium or image to analyze; write blocker (physical or software) to preserve the evidence; forensic workstation (Kali/SIFT/Autopsy); storage space for the images
> - **Output:** Finding FOR-001; verified forensic image; incident timeline; recovered artifacts (deleted files, attacker tools, execution traces); documented chain of custody

- **Operating Environment:** Forensic workstation (Kali Linux / SIFT), write blocker, medium/image to analyze
- **Role:** Reconstruct what happened after the attack occurred
- **Main tools:** dc3dd/Guymager, Sleuth Kit, Autopsy, Volatility, plaso/log2timeline

---

## Executive Summary

Disk forensics is the post-incident analysis: when a system has been compromised, the forensic analyst reconstructs what happened by examining the traces left on the disk (and in memory). It is the module where the offensive techniques of modules 01-07 are seen from the other side - not how an attack is executed, but how it is reconstructed afterwards, from the evidence it inevitably left.

The principle that governs the entire discipline is **evidence integrity**: digital evidence is fragile and alterable, and a poorly conducted analysis contaminates it, making it unusable. For this reason forensics follows a rigorous protocol: one always works on a **copy** (never on the original), acquired via a **write blocker**, verified with **cryptographic hashes** (if the image's hash matches the original's, the copy is faithful), and every step is documented in a **chain of custody** that guarantees its admissibility.

Finding FOR-001 documents the complete forensic cycle on a compromised test system: image acquisition, integrity verification, timeline construction (the temporal sequence of everything that happened on the filesystem) and recovery of the attacker's artifacts - including files deleted in an attempt to cover the tracks. It is the investigative countermeasure to the anti-forensics seen in `07-post-exploitation`: what the attacker deletes, forensics often recovers.

---

## Folder Structure

```
01-disk-forensics/
+-- README.md      # this file: acquisition, timeline, artifact recovery (FOR-001)
+-- img/           # timeline and Autopsy/Sleuth Kit analysis
```

---

## The Forensic Cycle: from Acquisition to Recovery

**Finding ID:** `FOR-001` | **Severity:** `High` (complete reconstruction of the intrusion from disk evidence, including the recovery of artifacts deleted by the attacker)

### Operational Context

The order of forensic operations is not arbitrary but follows the **order of volatility**: the most ephemeral evidence (RAM memory, network connections, processes) is acquired first, and the persistent evidence (disk) afterwards. RAM contains traces that disappear on shutdown - encryption keys, malicious processes, C2 connections - and must be captured first if the system is still on.

### PoC - Phase 1: Image acquisition (with integrity)

```Bash
# Forensic acquisition of the disk with dc3dd (computes the hash during the copy)
# The write blocker prevents any write to the original medium
sudo dc3dd if=/dev/sdb of=evidence.dd hash=sha256 log=acquisition.log
```

```
dc3dd: 500 GB copied
  [ok] sha256: 9f2a8b...c41d              <-- hash of the original
evidence.dd: 500 GB written
```

### PoC - Phase 2: Integrity verification (is the copy faithful?)

```Bash
# The image's hash must match the original's
sha256sum evidence.dd
```

```
9f2a8b...c41d  evidence.dd                <-- identical hash: valid forensic copy (FOR-001)
# match confirmed -> the image is admissible as evidence
```

### PoC - Phase 3: Memory acquisition and analysis (Volatility)

```Bash
# Analysis of a memory dump: active processes at the time of the incident
vol.py -f memory.dmp windows.pslist
vol.py -f memory.dmp windows.netscan       # network connections (C2)
```

```
PID    PPID   Name             Note
6612   4408   svch0st.exe      <-- malicious process (disguised name) (FOR-001)
                               netscan: 6612 -> 45.83.x.x:443  (active C2)
```

### PoC - Phase 4: Incident timeline

```Bash
# Construction of the super-timeline with plaso (log2timeline)
log2timeline.py --storage-file timeline.plaso evidence.dd
psort.py -o l2tcsv -w timeline.csv timeline.plaso
```

```
# Extract of the timeline (chronological order of the events)
2026-06-14 03:08  FILE  /tmp/linpeas.sh          created    <-- enum tool (04)
2026-06-14 03:11  FILE  /root/.ssh/authorized_keys modified <-- persistence (07)
2026-06-14 03:14  LOG   /var/log/auth.log        truncated  <-- anti-forensics (07)
2026-06-14 03:15  FILE  /tmp/exfil.tar.gz        created    <-- exfiltration staging
```

### PoC - Phase 5: Recovery of deleted files (carving)

```Bash
# Recovery of files deleted by the attacker (foremost/photorec)
foremost -i evidence.dd -o recovered/
```

```
Processing: evidence.dd
  sh: 1 file (deleted /tmp/exfil.tar.gz recovered)   <-- artifact recovered (FOR-001)
# what the attacker deleted to cover the tracks was recovered
```

### Methodology and Chain of Custody

- **Never on the original:** every analysis is conducted on the image, never on the original medium; the write blocker guarantees that the acquisition does not alter the evidence
- **Verifiable integrity:** the hash acquired at the time of the copy must be re-verified before and after the analysis; a discrepancy invalidates the evidence
- **Chain of custody:** every step (who, what, when, where) must be documented; evidence whose custody is not traceable is inadmissible in a proceeding
- **Order of volatility:** RAM and network state before the disk, if the system is on; shutting down a system destroys the volatile evidence

---

## Lab Experience

The most important lesson was the discipline of integrity, not the technique. Acquiring an image with `dd` is trivial; doing it in a forensically valid way - write blocker, hash computed during the copy, subsequent verification - is what distinguishes an admissible analysis from a contaminated one. The first time I carelessly mounted the image in read-write and altered the timestamps: a lesson learned at my expense on why every step of the protocol exists. Digital evidence does not forgive sloppiness.

The timeline reconstruction was the most powerful experience. Seeing plaso's super-timeline chronologically align every event - the creation of `linpeas.sh` (the enumeration of module 04), the modification of `authorized_keys` (the persistence of module 07), the truncation of `auth.log` (the anti-forensics) - turned a collection of files into a narrative of the attack. The timeline does not show files, it shows the story of what the attacker did, minute by minute.

The most instructive moment was the recovery of the deleted exfiltration archive. In module 07 I had documented how an attacker deletes the traces; here, with `foremost`, I recovered from the unallocated space exactly the `.tar.gz` that the attacker-me had deleted. This made concrete the limit of anti-forensics: deleting a file removes the reference, not the data, which remains recoverable until overwritten. What the attacker believes deleted, forensics often reconstructs.

---

## Theoretical Analysis: Digital Evidence as Reconstruction of the Past

Forensics is archaeology of the recent: reconstructing a past event (the attack) from the material traces it left. Every action on a computer system leaves residues - created files, modified timestamps, log entries, unallocated blocks containing deleted data - and the analyst interprets them to recompose the sequence of events. The foundation is that activity is never without a trace: even the most careful attacker alters the state of the system, and every alteration is potentially a piece of evidence.

The key concept is the order of volatility, which derives from the physics of information: some traces are ephemeral (RAM is erased on shutdown), others persistent (the disk survives). The analyst must capture the former before they vanish, inverting the instinctive priority (shutting down the compromised system is the mistake that destroys the volatile evidence). This temporal hierarchy of fragility governs the entire acquisition protocol.

The principle of integrity, finally, places forensics at the intersection of technique and law. Digital evidence has value only if its authenticity and non-alteration can be demonstrated: the cryptographic hash is the mathematical tool that guarantees it (if the hash has not changed, the data has not changed), and the chain of custody is the procedural tool that traces its history. This makes forensics a discipline where methodological rigor is not pedantry but the very condition of validity of the result. It links directly to the anti-forensics of `07-post-exploitation`: the attacker tries to destroy or alter the traces, the analyst to preserve and recover them - two faces of the same struggle over the integrity of the evidence.

---

## Real-World Scenario: The Reconstruction of the Incident

> This section describes how forensic analysis would operate in a real incident, reconstructing the attack for the response and possible attribution.

### The context (what happened)

An endpoint generated an alert (SIEM/Wazuh, module 08) and is isolated for forensic analysis. The attacker, before being detected, executed enumeration, established persistence, attempted to delete their tracks and exfiltrated data.

### The forensic reconstruction (what the analysis reveals)

```
[FOR-001] Image + memory acquisition -> integrity verified (hash)
        |
        v
Timeline (plaso): complete sequence of the intrusion reconstructed
        |
        +-- 03:08 enumeration tool dropped (initial access confirmed)
        +-- 03:11 persistence established (authorized_keys)
        +-- 03:14 anti-forensics attempt (auth.log truncated)
        +-- 03:15 exfiltration staging (exfil.tar.gz)
        |
        v
Memory analysis (Volatility): active C2 process -> IP of the attacker infrastructure
        |
        v
Carving (foremost): deleted exfiltration archive recovered -> data scope
        |
        v
Report: timeline + IOC + scope of the compromise -> response and defensive lessons
```

**Investigative value:** forensic analysis answers the questions that detection alone cannot: what exactly the attacker did, which data they touched, from where they operated, when they entered. The timeline provides the "what and when", the memory analysis the "who" (the C2 IP as an IOC), the carving the "scope" (the recovered data reveals what was about to be exfiltrated).

**Extracted indicators (IOC):** hashes of the attacker's tools, C2 IPs/domains from the connections in memory, timestamps of the intrusion, persistence artifacts. These IOCs feed the detection (SIEM rules, blocklists) to detect the same threat elsewhere.

**Defensive lesson:** forensics closes the incident response cycle. Detection (module 08) says "something happened"; forensics says "here is exactly what, how and with what impact". Without this reconstruction, the response is blind: one cannot contain what one does not know the extent of, nor prevent the recurrence of an attack one has not understood.

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `dc3dd` / `Guymager` | Imager | Acquisition | Forensic copy with integrated hashing |
| `Sleuth Kit` (TSK) | Forensic toolkit | CLI | Filesystem analysis, recovery, timeline (fls/mactime) |
| `Autopsy` | Forensic platform | GUI | Front-end of TSK: visual analysis, keyword search, artifacts |
| `Volatility 3` | Memory forensics | CLI | Analysis of RAM dumps (processes, network, injection) |
| `plaso` / `log2timeline` | Timeline | CLI | Correlated super-timeline from all sources |
| `foremost` / `photorec` | File carving | CLI | Recovery of deleted files from unallocated space |
| `write blocker` | Hardware/software | Preservation | Prevents writing to the original medium |

> **Recommended modern tool:** for a complete flow, `Autopsy` (front-end of Sleuth Kit) covers filesystem analysis, timeline and keyword search in a single interface. `Volatility 3` is the standard for memory. `plaso` for the super-timelines. The `SIFT Workstation` distribution (SANS) integrates the entire forensic arsenal ready to use.

---

## MITRE ATT&CK Mapping

> The table maps the attack techniques that forensic analysis **reconstructs/detects** after the fact.

| Tactic (reconstructed) | Technique | MITRE ID | Role of the analysis |
| :--- | :--- | :--- | :--- |
| Defense Evasion | Indicator Removal: File Deletion | `T1070.004` | Carving recovers the files deleted by the attacker (FOR-001) |
| Defense Evasion | Indicator Removal: Clear Linux Logs | `T1070.002` | The timeline highlights the truncation of the logs |
| Persistence | Account Manipulation: SSH Authorized Keys | `T1098.004` | The timeline reveals the modification of authorized_keys |
| Command and Control | Application Layer Protocol | `T1071` | Memory analysis reveals the active C2 connections |
| Exfiltration | Data Staged | `T1074` | Carving recovers the exfiltration staging archive |

| Defensive countermeasure (D3FEND) | D3FEND ID | Application |
| :--- | :--- | :--- |
| System Call Analysis | `D3-SCA` | Analysis of the execution artifacts on disk |
| Memory Boundary Tracking | `D3-MBT` | Forensic analysis of memory for processes/injection |
| File Analysis | `D3-FA` | Recovery and analysis of filesystem artifacts |

---

> **Note:** All documented activities were conducted on lab images and systems owned by the author. Disk forensics on third-party media requires legal authorization (warrant, owner's consent) and rigorous compliance with the chain of custody, which determines its admissibility. Forensic analysis may expose personal data: it must be conducted in compliance with privacy and data-processing regulations. Techniques are documented for educational and defensive/investigative purposes in an authorized context.
