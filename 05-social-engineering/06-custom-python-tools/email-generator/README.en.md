> **English** | [Italiano](README.md)

# Email Generator - Corporate Email Permutations

> - **Phase:** Social Engineering - Target Enumeration
> - **Visibility:** Zero - the script operates completely offline, generates permutations without interacting with the target
> - **Prerequisites:** Python 3.x; target first and last names (from LinkedIn, company website, theHarvester); target organization email domain
> - **Output:** List of candidate emails for each first/last name combination; input for SMTP verification or direct targeting

- **Operating Environment:** Kali Linux Purple
- **Framework:** Python 3.11 (standard library, no external dependencies)
- **Documented Techniques:** Email Permutation, Pattern Detection, Batch Generation

---

## Executive Summary

When the corporate email format is not known with certainty, the script generates all standard permutations (mario.rossi, m.rossi, rossi.mario, mrossi, etc.) for each first/last name combination. The produced list is then used for two purposes: address existence verification (SMTP VRFY/RCPT TO, or timing attack on login pages) and direct targeting in phishing campaigns. The script supports CSV file input for batch generation on employee lists.

---

## Usage

### Single Generation

```Bash
python3 email_gen.py Mario Rossi target-lab.com
```

```
mario.rossi@target-lab.com
rossi.mario@target-lab.com
mariorossi@target-lab.com
rossimario@target-lab.com
m.rossi@target-lab.com
mrossi@target-lab.com
rossim@target-lab.com
mario.r@target-lab.com
marior@target-lab.com
mr@target-lab.com
rossi.m@target-lab.com
mario_rossi@target-lab.com
rossi_mario@target-lab.com
mario-rossi@target-lab.com
rossi-mario@target-lab.com
mario@target-lab.com
rossi@target-lab.com
```

### Batch Generation from CSV

```Bash
# Input: employees.csv
# Mario,Rossi
# Luca,Bianchi
# Anna,Verdi

python3 email_gen.py --csv employees.csv --domain target-lab.com --output emails.txt
```

```
[*] Generating permutations for 3 employees
[*] 17 permutations x 3 employees = 51 candidate emails
[*] Output saved to: emails.txt
```

### Source Code

```python
#!/usr/bin/env python3
"""Email Permutation Generator for Social Engineering Recon."""
import sys, csv, argparse

def generate_emails(first, last, domain):
    f, l = first.lower().strip(), last.lower().strip()
    patterns = [
        f"{f}.{l}", f"{l}.{f}", f"{f}{l}", f"{l}{f}",
        f"{f[0]}.{l}", f"{f[0]}{l}", f"{l}{f[0]}",
        f"{f}.{l[0]}", f"{f}{l[0]}", f"{f[0]}{l[0]}",
        f"{l}.{f[0]}", f"{f}_{l}", f"{l}_{f}",
        f"{f}-{l}", f"{l}-{f}", f"{f}", f"{l}"
    ]
    return [f"{p}@{domain}" for p in dict.fromkeys(patterns)]

def main():
    parser = argparse.ArgumentParser(description='Email permutation generator')
    parser.add_argument('first', nargs='?', help='First name')
    parser.add_argument('last', nargs='?', help='Last name')
    parser.add_argument('domain', nargs='?', help='Domain')
    parser.add_argument('--csv', help='CSV file (first,last)')
    parser.add_argument('--domain', dest='csv_domain', help='Domain for CSV')
    parser.add_argument('--output', '-o', help='Output file')
    args = parser.parse_args()

    results = []
    if args.csv:
        domain = args.csv_domain or args.domain
        with open(args.csv) as f:
            for row in csv.reader(f):
                if len(row) >= 2:
                    results.extend(generate_emails(row[0], row[1], domain))
    elif args.first and args.last and args.domain:
        results = generate_emails(args.first, args.last, args.domain)
    else:
        parser.print_help()
        sys.exit(1)

    output = '\n'.join(results)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output + '\n')
        print(f"[*] {len(results)} emails saved to {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
```

---

## Verifying Generated Emails

```Bash
# Existence verification via SMTP RCPT TO (requires SMTP that doesn't block VRFY)
smtp-user-enum -M RCPT -U emails.txt -t mail.target-lab.com

# Alternative: timing attack on login page
# (pages that show "user not found" vs "wrong password"
#  have different response times)
```

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Information: Email Addresses | `T1589.002` | Email permutation generation for target enumeration |

---

> **Note:** The script was used on fictitious names. No real emails were enumerated or verified without authorization.
