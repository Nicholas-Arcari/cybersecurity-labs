> [English](README.en.md) | **Italiano**

# Email Generator - Permutazioni Email Aziendali

> - **Fase:** Social Engineering - Target Enumeration
> - **Visibilita:** Zero - lo script opera completamente offline, genera permutazioni senza interazione con il target
> - **Prerequisiti:** Python 3.x; nomi e cognomi dei target (da LinkedIn, sito aziendale, theHarvester); dominio email dell'organizzazione target
> - **Output:** Lista di email candidate per ogni combinazione nome/cognome; input per verifica SMTP o targeting diretto

- **Ambiente Operativo:** Kali Linux Purple
- **Framework:** Python 3.11 (libreria standard, nessuna dipendenza esterna)
- **Tecniche Documentate:** Email Permutation, Pattern Detection, Batch Generation

---

## Executive Summary

Quando il formato email aziendale non e noto con certezza, lo script genera tutte le permutazioni standard (mario.rossi, m.rossi, rossi.mario, mrossi, ecc.) per ogni combinazione nome/cognome. La lista prodotta viene poi utilizzata per due scopi: verifica dell'esistenza degli indirizzi (SMTP VRFY/RCPT TO, o timing attack su pagine di login) e targeting diretto nelle campagne di phishing. Lo script supporta input da file CSV per generazione batch su liste di dipendenti.

---

## Utilizzo

### Generazione Singola

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

### Generazione Batch da CSV

```Bash
# Input: employees.csv
# Mario,Rossi
# Luca,Bianchi
# Anna,Verdi

python3 email_gen.py --csv employees.csv --domain target-lab.com --output emails.txt
```

```
[*] Generazione permutazioni per 3 dipendenti
[*] 17 permutazioni x 3 dipendenti = 51 email candidate
[*] Output salvato in: emails.txt
```

### Codice Sorgente

```python
#!/usr/bin/env python3
"""Email Permutation Generator per Social Engineering Recon."""
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
    parser.add_argument('first', nargs='?', help='Nome')
    parser.add_argument('last', nargs='?', help='Cognome')
    parser.add_argument('domain', nargs='?', help='Dominio')
    parser.add_argument('--csv', help='File CSV (nome,cognome)')
    parser.add_argument('--domain', dest='csv_domain', help='Dominio per CSV')
    parser.add_argument('--output', '-o', help='File output')
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
        print(f"[*] {len(results)} email salvate in {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
```

---

## Verifica Email Generate

```Bash
# Verifica esistenza via SMTP RCPT TO (richiede SMTP che non blocchi VRFY)
smtp-user-enum -M RCPT -U emails.txt -t mail.target-lab.com

# Alternativa: timing attack su pagina di login
# (pagine che mostrano "utente non trovato" vs "password errata"
#  hanno tempi di risposta diversi)
```

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Information: Email Addresses | `T1589.002` | Generazione permutazioni email per enumerazione target |

---

> **Nota:** Lo script e stato utilizzato su nomi fittizi. Nessuna email reale e stata enumerata o verificata senza autorizzazione.
