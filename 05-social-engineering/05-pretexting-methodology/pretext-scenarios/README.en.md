> **English** | [Italiano](README.md)

# Pretext Scenarios - Social Engineering Scenario Templates

> - **Phase:** Social Engineering - Pretexting Design
> - **Visibility:** N/A - this section documents pretext design, not execution
> - **Prerequisites:** Completed target dossier (from `target-profiling/`); knowledge of Cialdini's principles; familiarity with phishing frameworks (GoPhish, SET)
> - **Output:** Ready-to-use scenario templates, calibrated by corporate role and context

- **Documented Techniques:** Pretexting Templates, Cialdini-Based Scenario Design, Role-Specific Calibration

---

## Executive Summary

This section provides ready-to-use pretexting scenario templates for social engineering campaigns. Each template is calibrated for a specific corporate role, exploits one or more of Cialdini's principles, and includes the variables to customize with target profiling data. Templates should never be used "as-is": contextual customization is what distinguishes generic phishing (easily recognizable) from targeted phishing (nearly indistinguishable from legitimate communication).

---

## Template 1: IT Department - Password Reset (Authority + Urgency)

**Ideal target:** any employee
**Principle:** Authority (IT department) + Urgency (time deadline)
**Expected click rate:** 25-35% (without training), 5-10% (post-training)

```
Subject: [ACTION REQUIRED] Mandatory password reset - Deadline {{SCADENZA}}

Dear {{NOME}},

Following the scheduled security update by the IT team,
you need to reset your corporate account password by
{{SCADENZA}}.

Click the following link to proceed:
{{URL}}

If you do not complete this operation, your account will be
temporarily suspended until manual verification.

IT Security Team
{{AZIENDA}}
```

**Variables from profiling:** `{{NOME}}`, `{{AZIENDA}}`, `{{SCADENZA}}` (24-48 hours)
**Landing page:** clone of the corporate authentication portal

---

## Template 2: CEO Fraud - Business Email Compromise (Authority + Reciprocity)

**Ideal target:** CFO, Finance department, Executive Assistant
**Principle:** Authority (CEO) + Reciprocity (personal request)
**Expected click rate:** 15-25% (the absence of links reduces suspicion)

```
Subject: Confidential request

{{NOME}},

I need an urgent and confidential favor. I'm in a meeting
and can't call.

Can you check if the wire transfer to {{FORNITORE}} has been
processed? The document with the details is here:
{{URL}}

Don't involve anyone else for now, I'll tell you about it after the meeting.

{{NOME_CEO}}
Sent from iPhone
```

**Variables from profiling:** `{{NOME_CEO}}` (from LinkedIn), `{{FORNITORE}}` (from company website/invoices)
**Note:** the "Sent from iPhone" signature justifies the informal tone and absence of corporate signature

---

## Template 3: Vendor/Supplier - Invoice Update (Reciprocity + Consistency)

**Ideal target:** Accounting, Procurement, Operations
**Principle:** Reciprocity (service already used) + Consistency (known process)
**Expected click rate:** 20-30%

```
Subject: Bank details update - {{FORNITORE}}

Dear {{NOME}},

We hereby inform you of the update to our bank details
for upcoming payments.

Please download the updated document at the following link
and proceed with the update in your system:
{{URL}}

For any clarification, please do not hesitate to contact us.

Administration
{{FORNITORE}}
```

**Variables:** `{{FORNITORE}}` (real company vendor, from LinkedIn/website/public invoices)

---

## Template 4: HR - Confidential Document (Curiosity + Social Proof)

**Ideal target:** all employees
**Principle:** Curiosity (confidential document) + Social Proof (already shared)
**Expected click rate:** 30-40% (curiosity is a powerful trigger)

```
Subject: 2026 bonus plan - Confidential document for your team

{{NOME}},

Attached you will find the Q2 2026 bonus plan for the
{{DIPARTIMENTO}} department. The document has already been
shared with area managers.

{{URL}}

Please do not share it outside the team until
the official announcement.

{{NOME_HR}}
Human Resources
{{AZIENDA}}
```

**Note:** "Do not share it" exploits the Streisand effect (prohibition increases curiosity)

---

## Template 5: SharePoint/OneDrive - Document Sharing (Familiarity)

**Ideal target:** any Microsoft 365 user
**Principle:** Familiarity (standard Microsoft notification)
**Expected click rate:** 35-45% (exact replica of legitimate notification)

```
Subject: {{NOME_COLLEGA}} shared "{{NOME_DOCUMENTO}}" with you

{{NOME_COLLEGA}} shared a file with you.

{{NOME_DOCUMENTO}}
"I need your feedback on this by Friday."

Open in SharePoint
{{URL}}

Microsoft SharePoint
```

**Variables:** `{{NOME_COLLEGA}}` (real colleague of the target, from LinkedIn)
**Landing page:** clone of the Microsoft 365 login page

---

## Scenario Matrix by Role

| Target Role | Primary Scenario | Secondary Scenario | Dominant Principle |
| :--- | :--- | :--- | :--- |
| C-Level (CEO, CFO) | Confidential board document | Vendor invoice update | Authority + Exclusivity |
| Finance / Accounting | CEO fraud (BEC) | Vendor invoice update | Authority + Urgency |
| HR | Application to review | Confidential bonus plan | Reciprocity + Curiosity |
| IT / Development | Security update | GitHub/Jira notification | Authority + Familiarity |
| Sales / Marketing | Lead shared by manager | Event/webinar invitation | Reciprocity + Social Proof |
| Operations / Production | Corporate communication | Policy update | Authority + Consistency |

---

## Anti-Patterns to Avoid in Pretexts

| Anti-Pattern | Problem | Correction |
| :--- | :--- | :--- |
| "You won a prize!" | Too generic, nobody believes it | Use specific corporate context |
| Intentional grammatical errors | Modern filters detect them | Write in correct language |
| Extreme urgency ("5 minutes!") | Triggers suspicion rather than compliance | Moderate urgency (24-48 hours) |
| Long and suspicious link | Visually recognizable | URL shortener or typosquatting domain |
| External sender for internal communication | Immediate inconsistency | Use spoofed or typosquatting domain |
| .exe attachment | Blocked by all gateways | Use .html (smuggling), .iso, or link |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | Development of email templates and landing pages for campaign |
| Resource Development | Establish Accounts: Social Media Accounts | `T1585.001` | Creation of fake profiles for impersonation (CEO fraud) |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Email template with link to customized landing page |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | Email template with disguised payload attachment |

---

> **Note:** The templates are provided for educational purposes and for authorized security awareness campaigns. The use of social engineering techniques without explicit authorization is illegal.
