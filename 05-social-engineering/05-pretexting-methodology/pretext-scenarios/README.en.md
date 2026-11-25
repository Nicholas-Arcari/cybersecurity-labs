> **English** | [Italiano](README.md)

# Pretext scenarios - social engineering scenario templates

> - **Phase:** Social Engineering - Pretexting Design
> - **Visibility:** N/A - this section documents pretext design, not execution
> - **Prerequisites:** Completed target dossier (from `target-profiling/`); knowledge of Cialdini's principles; familiarity with phishing frameworks (GoPhish, SET)
> - **Output:** Ready-to-use scenario templates, calibrated by corporate role and context

- **Documented Techniques:** Pretexting Templates, Cialdini-Based Scenario Design, Role-Specific Calibration

---

## Executive summary

This section provides ready-to-use pretexting scenario templates for social engineering campaigns. Each template is calibrated for a specific corporate role, exploits one or more of Cialdini's principles, and includes the variables to customize with target profiling data. Templates should never be used "as-is": contextual customization is what distinguishes generic phishing (easily recognizable) from targeted phishing (nearly indistinguishable from legitimate communication).

---

## Template 1: IT department - password reset (authority + urgency)

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

## Template 2: CEO fraud - business email compromise (authority + reciprocity)

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

## Template 3: Vendor/Supplier - invoice update (reciprocity + consistency)

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

## Template 4: HR - confidential document (curiosity + social proof)

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

## Template 5: SharePoint/OneDrive - document sharing (familiarity)

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

## Scenario matrix by role

| target role | primary scenario | secondary scenario | dominant principle |
| :--- | :--- | :--- | :--- |
| c-level (ceo, cfo) | confidential board document | vendor invoice update | authority + exclusivity |
| finance / accounting | ceo fraud (bec) | vendor invoice update | authority + urgency |
| hr | application to review | confidential bonus plan | reciprocity + curiosity |
| it / development | security update | github/jira notification | authority + familiarity |
| sales / marketing | lead shared by manager | event/webinar invitation | reciprocity + social proof |
| operations / production | corporate communication | policy update | authority + consistency |

---

## Anti-Patterns to avoid in pretexts

| anti-pattern | problem | correction |
| :--- | :--- | :--- |
| "you won a prize!" | too generic, nobody believes it | use specific corporate context |
| intentional grammatical errors | modern filters detect them | write in correct language |
| extreme urgency ("5 minutes!") | triggers suspicion rather than compliance | moderate urgency (24-48 hours) |
| long and suspicious link | visually recognizable | url shortener or typosquatting domain |
| external sender for internal communication | immediate inconsistency | use spoofed or typosquatting domain |
| .exe attachment | blocked by all gateways | use .html (smuggling), .iso, or link |

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| resource development | develop capabilities: malware | `T1587.001` | development of email templates and landing pages for campaign |
| resource development | establish accounts: social media accounts | `T1585.001` | creation of fake profiles for impersonation (ceo fraud) |
| initial access | phishing: spearphishing link | `T1566.002` | email template with link to customized landing page |
| initial access | phishing: spearphishing attachment | `T1566.001` | email template with disguised payload attachment |

---

> **Note:** The templates are provided for educational purposes and for authorized security awareness campaigns. The use of social engineering techniques without explicit authorization is illegal.
