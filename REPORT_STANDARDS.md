# Standard di Redazione dei Report - Cybersecurity Labs

> Documento di riferimento per la scrittura professionale dei README tecnici in questa repository.
> Obbligatorio rispettare queste regole per mantenere coerenza, qualita e leggibilita professionale
> in tutti i moduli. Aggiornare questo file ogni volta che si definisce una nuova convenzione.

---

## Indice

1. [Stato di avanzamento lavori](#1-stato-di-avanzamento-lavori)
2. [Lingua e stile](#2-lingua-e-stile)
3. [Struttura obbligatoria di ogni README](#3-struttura-obbligatoria-di-ogni-readme)
4. [Sistema di Finding ID](#4-sistema-di-finding-id)
5. [Scala di Severity](#5-scala-di-severity)
6. [Formato MITRE ATT&CK](#6-formato-mitre-attck)
7. [Documentazione degli strumenti](#7-documentazione-degli-strumenti)
8. [Output testuali e blocchi di codice](#8-output-testuali-e-blocchi-di-codice)
9. [Diagrammi e flussi operativi](#9-diagrammi-e-flussi-operativi)
10. [Sezione Remediation (Blue Team)](#10-sezione-remediation-blue-team)
11. [Cross-referencing tra sezioni](#11-cross-referencing-tra-sezioni)
12. [Caratteri e formattazione vietati](#12-caratteri-e-formattazione-vietati)
13. [Anti-pattern da evitare](#13-anti-pattern-da-evitare)
14. [Checklist pre-pubblicazione](#14-checklist-pre-pubblicazione)
15. [Le Tre Dimensioni del Report](#15-le-tre-dimensioni-del-report)
16. [Proiezione verso lo Scenario Reale](#16-proiezione-verso-lo-scenario-reale)

---

## 1. Stato di Avanzamento Lavori

### README completati e conformi agli standard

| Modulo | File | Stato | Note |
| :--- | :--- | :---: | :--- |
| 00-setup | tutti (21 file) | Completo | Hardening guide: no finding ID, no MITRE (setup/config) |
| Root | `README.md` | Completo | Struttura aggiornata, finding table e MITRE aggregato |
| 01-recon | `README.md` | Completo | Finding registry + MITRE ATT&CK master table |
| 01-recon | `01-osint-passive/README.md` | Completo | Finding ID, severity, output testuali, MITRE |
| 01-recon | `02-network-scanning-active/README.md` | Completo | Finding ID, severity, output testuali, MITRE |
| 01-recon | `03-dns-enumeration/README.md` | Completo | Finding ID, severity, output testuali, MITRE |
| 01-recon | `04-infrastructure-intel/README.md` | Completo | Finding ID, severity, output testuali, MITRE |
| 02-vulnerability-assessment | `README.md` | Completo | Registro finding + MITRE ATT&CK aggregato |
| 02-vulnerability-assessment | `01-general-scanners/README.md` | Completo | Panoramica 3 scanner |
| 02-vulnerability-assessment | `01-general-scanners/nessus/README.md` | Completo | VULN-001, VULN-002, credentialed scan |
| 02-vulnerability-assessment | `01-general-scanners/nmap-nse-vuln/README.md` | Completo | NSE scripts, categorie, workflow |
| 02-vulnerability-assessment | `01-general-scanners/open-vas-gvm/README.md` | Completo | Setup GVM, troubleshooting PostgreSQL |
| 02-vulnerability-assessment | `02-protocol-specific-audit/README.md` | Completo | Panoramica audit per protocollo |
| 02-vulnerability-assessment | `02-protocol-specific-audit/smb-net-bios/README.md` | Completo | VULN-003, VULN-004, accesso C$ |
| 02-vulnerability-assessment | `02-protocol-specific-audit/smtp/README.md` | Completo | VULN-005, porta filtrata |
| 02-vulnerability-assessment | `02-protocol-specific-audit/snmp/README.md` | Completo | VULN-006, SNMP assente |
| 02-vulnerability-assessment | `02-protocol-specific-audit/ssl-tls/README.md` | Completo | Metodologia testssl.sh/sslscan, lab da completare |
| 02-vulnerability-assessment | `03-cve-analysis/README.md` | Completo | Panoramica CVE analysis |
| 02-vulnerability-assessment | `03-cve-analysis/cvss-calculator/README.md` | Completo | CVSS v3.1, Python, scoring contestuale |
| 02-vulnerability-assessment | `03-cve-analysis/searchsploit-manual-lookup/README.md` | Completo | Searchsploit, msfvenom, analisi codice |
| 02-vulnerability-assessment | `03-cve-analysis/vulnerability-databases/README.md` | Completo | CVE/NVD/Exploit-DB cross-referencing |
| 02-vulnerability-assessment | `04-reporting-templates/README.md` | Completo | Panoramica reporting templates |
| 02-vulnerability-assessment | `04-reporting-templates/executive-summary-template/README.md` | Completo | Template + esempio compilato |
| 02-vulnerability-assessment | `04-reporting-templates/technical-findings-template/README.md` | Completo | Template + 3 esempi compilati |
| 03-web-attacks | tutti | Completo | WEB-001..015, 34 README scritti |
| 04-system-exploitation | `01-frameworks/README.md` | Completo | Registro finding EXPLOIT-001..004, MITRE aggregato |
| 04-system-exploitation | `01-frameworks/empire/README.md` | Completo | EXPLOIT-001, EXPLOIT-002, Scenario Reale |
| 04-system-exploitation | `01-frameworks/metasploit/README.md` | Completo | EXPLOIT-003, EXPLOIT-004, pivoting SOCKS |
| 04-system-exploitation | `02-exploit-database/README.md` | Completo | Registro finding EXPLOIT-005..007, MITRE aggregato |
| 04-system-exploitation | `02-exploit-database/compiled-exploits/README.md` | Completo | EXPLOIT-005, EXPLOIT-006, cross-compilation MinGW |
| 04-system-exploitation | `02-exploit-database/searchsploit/README.md` | Completo | EXPLOIT-007, exploit research offline |
| 04-system-exploitation | `03-privilege-escalation/README.md` | Completo | Registro finding EXPLOIT-008..019, MITRE aggregato |
| 04-system-exploitation | `03-privilege-escalation/linux-priv-esc/README.md` | Completo | Registro finding EXPLOIT-008..012, MITRE Linux |
| 04-system-exploitation | `03-privilege-escalation/linux-priv-esc/gtfo-bins-notes/README.md` | Completo | EXPLOIT-008, EXPLOIT-009, LotL sudo/SUID |
| 04-system-exploitation | `03-privilege-escalation/linux-priv-esc/linpeas/README.md` | Completo | EXPLOIT-010, EXPLOIT-011, EXPLOIT-012 |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/README.md` | Completo | Registro finding EXPLOIT-013..019, MITRE Windows |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/juicypotato-printnightmare/README.md` | Completo | EXPLOIT-013, EXPLOIT-014, PrintSpoofer SYSTEM |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/sherlock/README.md` | Completo | EXPLOIT-015, kernel patch audit |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/winpeas/README.md` | Completo | EXPLOIT-016..019, Unattend.xml + XAMPP ACL |
| 04-system-exploitation | `04-binary-exploitation/README.md` | Completo | Registro finding EXPLOIT-020..021, MITRE aggregato |
| 04-system-exploitation | `04-binary-exploitation/buffer-overflow-prep/README.md` | Completo | EXPLOIT-020, stack overflow classico, Immunity + Mona.py |
| 04-system-exploitation | `04-binary-exploitation/pwntools-scripts/README.md` | Completo | EXPLOIT-021, ROP chain, ASLR/DEP bypass, Ret2Libc |
| 04-system-exploitation | `05-password-cracking/README.md` | Completo | Registro finding EXPLOIT-022..025, MITRE aggregato |
| 04-system-exploitation | `05-password-cracking/hashcat/README.md` | Completo | EXPLOIT-022, EXPLOIT-023, Mask + Rule-based Attack NTLM |
| 04-system-exploitation | `05-password-cracking/john-the-ripper/README.md` | Completo | EXPLOIT-024, EXPLOIT-025, ZIP cracking + Linux unshadowing |
| 04-system-exploitation | `05-password-cracking/wordlists/README.md` | Completo | Guida wordlist: RockYou, SecLists, CeWL, CUPP |
| 05-social-engineering | tutti | Da fare | - |
| 06-wireless-security | tutti | Da fare | - |
| 07-post-exploitation | tutti | Da fare | - |
| 08-defense-hardenings | tutti | Da fare | - |
| 09-digital-forensics | tutti | Da fare | - |
| 10-cloud-security | tutti | Da fare | - |

### Finding ID sequenza globale

| Prefisso | Modulo | Prossimo ID disponibile |
| :--- | :--- | :--- |
| `OSINT-` | 01-recon/01-osint-passive | `OSINT-005` |
| `SCAN-` | 01-recon/02-network-scanning | `SCAN-004` |
| `DNS-` | 01-recon/03-dns-enumeration | `DNS-004` |
| `INTEL-` | 01-recon/04-infrastructure-intel | `INTEL-005` |
| `VULN-` | 02-vulnerability-assessment | `VULN-007` |
| `WEB-` | 03-web-attacks | `WEB-016` |
| `EXPLOIT-` | 04-system-exploitation | `EXPLOIT-026` |
| `SE-` | 05-social-engineering | `SE-001` |
| `WIFI-` | 06-wireless-security | `WIFI-001` |
| `POST-` | 07-post-exploitation | `POST-001` |
| `DEF-` | 08-defense-hardenings | `DEF-001` |
| `FOR-` | 09-digital-forensics | `FOR-001` |
| `CLOUD-` | 10-cloud-security | `CLOUD-001` |

---

## 2. Lingua e Stile

### Lingua

- **Lingua principale: Italiano.** Tutto il testo narrativo, le spiegazioni, i titoli delle sezioni e le
  note operative sono scritti in italiano.
- **Eccezioni in inglese accettate:** nomi propri di tool (`Nmap`, `Sherlock`, `Masscan`), nomi tecnici
  standard (`payload`, `exploit`, `banner`, `finding`, `scope`, `engagement`, `shellcode`), ID MITRE
  (`T1046`), nomi di tecnologie (`SMB`, `RDP`, `TLS`), output di tool (sempre in lingua originale).
- **Non tradurre** termini tecnici consolidati nel settore: usare `finding` non `risultato`,
  `misconfiguration` non `configurazione errata`, `payload` non `carico utile`.

### Stile narrativo

- Scrivere in **terza persona impersonale** o prima persona plurale: "si esegue", "si analizza",
  "l'analisi ha evidenziato", non "ho fatto", "ho trovato".
- **Spiegare sempre il PERCHE prima del COME.** Prima il contesto operativo e l'impatto,
  poi i comandi. Un recruiter o un cliente legge prima perche quella tecnica e rilevante, poi
  come si esegue.
- **Voce attiva** e frasi brevi. Evitare subordinate inutili.
- Non usare toni informali ("facile", "semplice", "basta fare"). Il documento deve sembrare
  scritto da un professionista senior per un cliente o per un collega di pari livello.

---

## 3. Struttura Obbligatoria di ogni README

Ogni README di sottocartella (tecnica specifica) deve seguire questo template nell'ordine indicato.
Le sezioni obbligatorie sono marcate con [O], le opzionali con [F] (facoltative se non applicabili).

```
# [Numero] - [Titolo Descrittivo]                              [O]

> - **Fase:** [nome fase] -> [nome sottofase]                  [O]
> - **Visibilita:** [Zero / Bassa / Alta] - [spiegazione]      [O]
> - **Prerequisiti:** [cosa serve prima]                       [O]
> - **Output:** [cosa produce questa fase]                     [O]

---

## Introduzione                                                [O]
[Paragrafo che spiega il PERCHE di questa fase/tecnica,
 il suo posizionamento nella kill chain e il valore operativo]

---

## Struttura della cartella                                    [O se ha sottocartelle]
[Blocco di codice con albero directory e commenti]

---

## `nome-sottocartella/` - Titolo Tecnica                     [O per ogni sottocartella]

**ID Finding:** `XXX-NNN` | **Severity:** `[livello]`         [O se la tecnica produce un finding]

### Cosa si trova                                              [O]
### Contesto operativo                                         [O]
### Esecuzione / Comandi                                       [O]
[blocco bash con comandi]
[blocco output strutturato esempio]                            [F se non applicabile]
### Analisi dei risultati / Finding documentato                [O]
### Remediation                                                [O - sempre, anche breve]

---

## Flusso operativo consigliato                               [O]
[diagramma ASCII con sequenza e decisioni]

---

## Tool di riferimento                                        [O]
[tabella Tool | Tipo | Comando/Accesso | Caso d'uso]

---

## Mappatura MITRE ATT&CK                                     [O]
[tabella Tattica | Tecnica | ID MITRE | Descrizione dell'Azione]

---

> **Nota:** [disclaimer su target autorizzati / laboratorio]   [O]
```

### README di sezione padre (es. `01-recon/README.md`)

I README padre hanno struttura diversa: sono documenti di navigazione e sintesi, non guide tecniche.
Devono contenere:

1. Header metadata (uguale ai figli)
2. Introduzione alla fase (posizionamento nella kill chain)
3. Struttura della cartella con descrizione di ogni sottocartella
4. Flusso operativo dell'intera fase
5. **Registro Finding** (tabella ID | Descrizione | Severity | Sottocartella)
6. **Mappatura MITRE ATT&CK aggregata** (tutte le tecniche della sezione)
7. Nota disclaimer

---

## 4. Sistema di Finding ID

### Formato

```
[PREFISSO]-[NNN]
```

- `[PREFISSO]`: abbreviazione maiuscola del modulo (vedi tabella sezione 1)
- `[NNN]`: numero sequenziale a tre cifre, partendo da `001`
- Esempi: `OSINT-001`, `SCAN-003`, `DNS-001`, `EXPLOIT-005`

### Regole di assegnazione

- Gli ID sono **sequenziali e mai riutilizzati**, anche se un finding viene rimosso.
- Gli ID sono **univoci a livello globale** nella repository: non esistono due finding con lo
  stesso ID in moduli diversi.
- La sequenza riparte da `001` per ogni prefisso/modulo ma non per ogni file: `OSINT-001`
  e assegnato in `breach-data/` e `OSINT-004` e assegnato in `user-enumeration/`, tutti
  appartengono alla stessa sequenza OSINT.
- Aggiornare sempre la tabella "Finding ID sequenza globale" in questo file quando si
  aggiungono nuovi finding.

### Posizionamento nel testo

Il badge finding ID si posiziona **immediatamente dopo il titolo della sezione** che introduce
il finding, prima del testo descrittivo, su una riga dedicata:

```markdown
## `nome-sezione/` - Titolo Tecnica

**ID Finding:** `OSINT-001` | **Severity:** `Alto`

### Cosa si trova
```

Per finding annidati all'interno di una sezione piu grande (es. due finding nella stessa
sottocartella), il badge si posiziona dopo il titolo del sotto-paragrafo:

```markdown
#### Finding 1 - Information Disclosure (NetBIOS)

**ID Finding:** `SCAN-002` | **Severity:** `Basso`
```

---

## 5. Scala di Severity

Usare esclusivamente i cinque livelli seguenti, scritti in italiano, in backtick nel testo:

| Livello | Backtick | Criteri di assegnazione |
| :--- | :--- | :--- |
| Critico | `Critico` | Compromissione immediata e totale del sistema o dell'infrastruttura. Esempio: Zone Transfer riuscito, RCE non autenticata, credenziali admin in chiaro. |
| Alto | `Alto` | Accesso non autorizzato a dati sensibili o escalation di privilegi probabile con effort basso. Esempio: SMB Signing non obbligatorio (vettore SMB Relay), credenziali in breach attivi. |
| Medio | `Medio` | Vulnerabilita sfruttabile con effort moderato o condizioni specifiche. Esempio: Virtual Host nascosto accessibile, certificati self-signed, informazioni che facilitano attacchi successivi. |
| Basso | `Basso` | Informazione utile per ulteriori attacchi ma non direttamente sfruttabile. Esempio: NetBIOS name disclosure, username su social network. |
| Informativo | `Informativo` | Dato rilevante per la mappatura della superficie d'attacco, nessun rischio diretto. Esempio: host attivi identificati, WAF/CDN rilevato, stack tecnologico confermato. |

### Severity variabile

Se la severity dipende dal contenuto trovato (es. Google Dorks che puo trovare nulla o trovare
credenziali), usare il formato:

```markdown
**Severity:** `Variabile (Medio / Alto)`
```

Spiegare nel corpo del testo cosa determina la severity effettiva.

---

## 6. Formato MITRE ATT&CK

### Tabella standard

La tabella MITRE ATT&CK e **obbligatoria** in ogni README tecnico. Si posiziona sempre
**alla fine del documento**, prima della nota disclaimer finale, separata da `---`.

```markdown
---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| [Tattica] | [Nome Tecnica Esteso] | `T1234.001` | [Cosa e stato fatto concretamente, con riferimento al finding ID se applicabile.] |
```

### Regole di compilazione

- **Tattica:** usare il nome ufficiale della tattica MITRE in inglese
  (es. `Reconnaissance`, `Discovery`, `Credential Access`, `Privilege Escalation`).
- **Tecnica:** usare il nome esteso ufficiale in inglese, incluso il sotto-nome dopo i due punti
  se applicabile (es. `Gather Victim Identity Info: Credentials`).
- **ID MITRE:** sempre in backtick, formato `T` maiuscola + numero + eventuale sub-tecnica
  (es. `T1589.001`). Verificare sempre l'ID sulla piattaforma ufficiale attack.mitre.org.
- **Descrizione dell'Azione:** in italiano, descrivere cosa e stato fatto concretamente nel lab,
  non cosa dice la teoria MITRE. Includere il Finding ID correlato tra parentesi se esiste.

### Tabella aggregata nel README padre

Il README padre di ogni modulo deve contenere una tabella MITRE aggregata con una colonna
aggiuntiva "Finding Correlato":

```markdown
| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Credentials | `T1589.001` | OSINT-001 |
```

### Dove trovare gli ID MITRE corretti

- Sito ufficiale: `https://attack.mitre.org/techniques/`
- Ricerca per tecnica: `https://attack.mitre.org/techniques/T1589/`
- Non inventare ID. Se non si trova la tecnica esatta, usare la tecnica padre senza sub-tecnica.

---

## 7. Documentazione degli Strumenti

### Tabella tool di riferimento

Ogni README deve chiudersi (prima della sezione MITRE) con una tabella degli strumenti
che comprende **anche i tool moderni equivalenti o alternativi**, non solo quelli usati
nell'esercizio documentato:

```markdown
| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `nome-tool` | [categoria] | [passiva/attiva/CLI/Web] | [quando e perche usarlo] |
```

### Categorie di tool accettate

- `Email/Subdomain harvesting`
- `Username enumeration`
- `Breach data`
- `DNS query`
- `Port scanner`
- `Service enumerator`
- `Vulnerability scanner`
- `Tech fingerprint`
- `Exploitation framework`
- `Post-exploitation`
- `Password cracking`
- `Network sniffer`
- `Traffic analyzer`
- `SIEM/Log analysis`

### Nota sui tool moderni

Quando esiste un tool piu moderno e mantenuto rispetto a quello usato nell'esercizio, aggiungerlo
alla tabella e aggiungere un blocco citazione con spiegazione:

```markdown
> **Tool moderno consigliato:** `nome` - spiegazione del vantaggio rispetto al tool precedente
> e comando di esempio.
```

Tool moderni da preferire (aggiornati al 2025-2026):

| Tool classico | Alternativa moderna | Motivo |
| :--- | :--- | :--- |
| `Sublist3r` | `amass` (OWASP) | Piu potente, attivamente mantenuto, piu fonti |
| `httprobe` | `httpx` (ProjectDiscovery) | Piu veloce, da status code + titolo + tech |
| `Masscan` (su VM) | `RustScan` | Compatibile con NAT virtualizzati, piu stabile |
| `theHarvester` base | `theHarvester` + API Hunter.io | Senza API key i risultati sono molto ridotti |
| Scanner manuale | `nuclei` (ProjectDiscovery) | Template-based, migliaia di CVE pre-scritti |
| `enum4linux` | `enum4linux-ng` | Riscrittura moderna, piu stabile su ambienti recenti |
| `CrackMapExec` | `NetExec` (nxc) | Fork attivo dopo il repo originale abbandonato |

---

## 8. Output Testuali e Blocchi di Codice

### Quando includere output testuali

Includere un blocco di output strutturato (anche sintetico/esempio) ogni volta che:
- Il comando e mostrato per la prima volta in quel contesto
- L'output contiene finding rilevanti che si vuole evidenziare
- L'output dimostra una misconfiguration o un dato critico

Non e necessario mostrare output completi e lunghi: usare output **sintetici ma realistici**
che mostrano le righe rilevanti. Annotare con `<--` le righe piu importanti.

### Formato blocchi di codice

```markdown
Blocco comando:
    ```Bash
    sudo nmap -p 445 -sC 10.0.2.3
    ```

Blocco output strutturato (esempio):
    ```
    PORT    STATE SERVICE
    445/tcp open  microsoft-ds
    | smb2-security-mode:
    |_    Message signing enabled but not required    <-- SCAN-003
    | nbstat: NetBIOS name: WINDOWS-TEST              <-- SCAN-002
    ```
```

### Regole per i blocchi di codice

- I comandi sono **sempre** in blocchi ` ```Bash ` con specificazione del linguaggio.
- Gli output sono in blocchi ` ``` ` senza specificazione del linguaggio.
- I file di configurazione sono in blocchi ` ```plaintext ` o con il linguaggio specifico
  (` ```xml `, ` ```json `, ecc.).
- Le annotazioni inline dell'output usano `<--` con spazio prima e descrizione breve.
- Non incollare output enormi: tagliare con `[... output troncato ...]` se necessario.
- I comandi con placeholder usano `<PLACEHOLDER>` in maiuscolo con angolari.

### Output da screenshot vs output testuale

- **Preferire sempre l'output testuale** quando disponibile: e verificabile, copiabile, cercabile.
- Gli screenshot sono accettati solo quando l'output e grafico (GUI, browser, dashboard).
- Se si ha solo uno screenshot ma non il testo, indicare:
  `[Output disponibile in ./img/Screenshot_YYYY-MM-DD.jpg]`
- **Non sostituire mai un output testuale con uno screenshot** di un terminale.

---

## 9. Diagrammi e Flussi Operativi

### Quando includere un flusso operativo

Obbligatorio nei README padre di ogni modulo. Facoltativo (ma consigliato) nei README
tecnici complessi con piu step sequenziali o decisioni condizionali.

### Formato ASCII obbligatorio

Usare esclusivamente ASCII puro nei diagrammi, compatibile con qualsiasi visualizzatore Markdown.

**Caratteri permessi per i diagrammi:**

```
Linee orizzontali:    ---
Linee verticali:      |
Frecce:               -> (destra), <- (sinistra), v (basso), ^ (alto)
Branch:               +-- (ramo da linea verticale)
Connettori:           +   (incrocio)
Box semplici:         [testo]  (testo)
Commenti inline:      # commento
```

**Caratteri VIETATI nei diagrammi** (causano problemi su alcuni visualizzatori):
```
- Frecce unicode:  -->, -->, <=>, =>
- Box unicode:     +--+, |  |
- Simboli speciali: ►, ◄, ●, ○
```

Esempio di flusso corretto:

```markdown
    ```
    [1] Live Host Discovery
         +-- arp-scan -l  ->  lista IP attivi nella LAN
                  |
                  v
    [2] Port Discovery
         +-- masscan -p1-65535 <IP> --rate=1000
                  |
                  v
    [3] Deep Enumeration
         +-- nmap -sC -p<porte> <IP>
                  |
                  v
         [Output] -> attack surface map
    ```
```

---

## 10. Sezione Remediation (Blue Team)

### Obbligatorieta

La sezione Remediation e **obbligatoria per ogni finding con severity Critico, Alto o Medio**.
Per finding Basso e Informativo e facoltativa ma consigliata.

### Posizionamento

Immediatamente dopo la descrizione del finding e la sua analisi, prima della sezione successiva.

### Struttura minima

```markdown
### Remediation

- **Azione immediata:** [cosa fare subito per mitigare]
- **Azione strutturale:** [come risolvere la causa radice]
- **Verifica:** [come confermare che la remediation ha funzionato]
```

### Tono

La remediation e scritta dalla prospettiva del **Blue Team / Difensore**, non dell'attaccante.
Usare un tono tecnico ma orientato all'azione. Specificare sempre il componente da configurare
(es. "GPO: `Microsoft network server: Digitally sign communications`") non solo la categoria
generica ("abilitare la firma SMB").

---

## 11. Cross-referencing tra Sezioni

### Come referenziare altri moduli

Quando una tecnica o un finding in una sezione si collega direttamente a un'altra sezione
della repository, indicarlo esplicitamente:

```markdown
La lista di sottodomini prodotta diventa input diretto per
`03-web-attacks/02-web-recon/`.

La misconfiguration SMB Signing (SCAN-003) e sfruttata nella fase
`07-post-exploitation/04-pivoting-tunneling/`.
```

### Come referenziare finding

Nel testo corrente, referenziare finding precedenti o correlati con il loro ID in backtick:

```markdown
Questo finding conferma quanto gia rilevato in `DNS-001`: la superficie
di attacco DNS del target e completamente esposta.
```

### Come referenziare tool in altri moduli

```markdown
Per la scansione di vulnerabilita sui sottodomini trovati, vedere
`02-vulnerability-assessment/01-general-scanners/nmap-nse-vuln/`.
```

---

## 12. Caratteri e Formattazione Vietati

### Carattere em dash (VIETATO)

Il carattere `—` (U+2014, em dash) e **assolutamente vietato** in tutta la repository.

- SBAGLIATO: `Questo tool - usato nel Red Team — e molto potente`
- CORRETTO: `Questo tool - usato nel Red Team - e molto potente`

Per verificare la presenza di em dash in un file:
```Bash
grep -P "\xe2\x80\x94" file.md
```

Per sostituire tutti gli em dash in un file:
```Bash
python3 -c "
content = open('file.md').read()
open('file.md', 'w').write(content.replace('\u2014', '-'))
"
```

### Frecce unicode nei testi (VIETATO fuori dai blocchi di codice)

- VIETATE nei testi narrativi: `->`, `=>`, `-->`, e qualsiasi freccia unicode
- PERMESSE solo all'interno di blocchi di codice ` ``` ` per diagrammi ASCII

### Intestazioni con blocchi citazione nel metadata

L'header metadata usa **trattino semplice + spazio** come separatore, non frecce o em dash:

```markdown
# Corretto:
> - **Fase:** Reconnaissance - Passive Information Gathering
> - **Visibilita:** Zero - nessun pacchetto inviato

# SBAGLIATO:
> **Fase:** Reconnaissance -> Passive Information Gathering
> **Visibilita:** Zero — nessun pacchetto inviato
```

### Accenti e caratteri speciali nel testo

Le vocali accentate (`a`, `e`, `i`, `o`, `u`) sono permesse nel testo narrativo italiano.
Nei blocchi di codice e nei comandi, usare esclusivamente ASCII puro (no accenti).

---

## 13. Anti-pattern da Evitare

### Anti-pattern di contenuto

| Anti-pattern | Problema | Correzione |
| :--- | :--- | :--- |
| "Basta eseguire `nmap`" | Tono informale, non spiega il perche | Spiegare sempre contesto e motivazione prima del comando |
| Lista di comandi senza spiegazione | Non dimostra comprensione | Ogni comando deve avere una riga di contesto operativo |
| "Come si vede dallo screenshot" | Non verificabile, non cercabile | Affiancare sempre output testuale quando possibile |
| Severity non assegnata | Finding non classificato | Ogni finding deve avere ID e severity |
| Finding senza remediation | Documento incompleto | Aggiungere sempre almeno una riga di remediation |
| Tool senza versione | Non riproducibile | Specificare versione quando critica (es. "Nmap 7.94") |
| Target non autorizzato usato senza nota | Rischio legale/reputazionale | Sempre dichiarare il perimetro di autorizzazione |
| Sezione MITRE mancante | Non professionale | Obbligatoria in ogni README tecnico |
| Em dash nel testo | Inconsistenza, violazione standard | Sostituire con trattino semplice `-` |
| Testo in inglese dove non necessario | Incoerenza linguistica | Usare italiano per tutta la narrativa |

### Anti-pattern strutturali

- **Non creare un README che e solo una lista di comandi:** ogni documento deve avere
  introduzione, contesto operativo, analisi e conclusioni.
- **Non duplicare contenuto tra README padre e README figlio:** il padre fa sintesi e navigazione,
  il figlio entra nel dettaglio tecnico.
- **Non omettere il flusso operativo:** il reader deve capire in quale ordine eseguire le attivita.
- **Non usare titoli generici:** invece di `## Analisi`, usare `## Analisi critica: falsi negativi
  in ambiente virtualizzato`.

---

## 14. Checklist Pre-pubblicazione

Prima di considerare un README completato, verificare tutti i punti:

### Struttura

- [ ] Header metadata presente con Fase, Visibilita, Prerequisiti, Output
- [ ] Introduzione con posizionamento nella kill chain
- [ ] Struttura cartella documentata (se applicabile)
- [ ] Ogni sottocartella ha la propria sezione

### Finding

- [ ] Ogni finding ha un ID univoco nel formato `PREFISSO-NNN`
- [ ] Ogni finding ha una severity assegnata dalla scala standard
- [ ] La sequenza ID e aggiornata in `REPORT_STANDARDS.md` (tabella sezione 1)
- [ ] I finding critici e alti hanno sezione remediation completa

### Contenuto tecnico

- [ ] Ogni tecnica ha il contesto operativo (perche prima del come)
- [ ] I comandi principali hanno un blocco output di esempio
- [ ] Le annotazioni `<--` evidenziano le righe piu importanti degli output
- [ ] Il flusso operativo e presente e usa solo ASCII permesso

### Tool

- [ ] Tabella tool di riferimento presente
- [ ] Tool moderni equivalenti inclusi quando esistono
- [ ] Nota `> **Tool moderno consigliato:**` presente se applicabile

### MITRE ATT&CK

- [ ] Sezione MITRE presente alla fine del documento
- [ ] Ogni tecnica ha ID verificato su attack.mitre.org
- [ ] La descrizione dell'azione e in italiano e riferisce all'attivita concreta del lab
- [ ] I Finding ID sono citati nella colonna descrizione

### Formattazione

- [ ] Nessun em dash `—` nel documento (verificare con grep)
- [ ] Lingua italiana per tutto il testo narrativo
- [ ] Blocchi codice con specificazione linguaggio (`bash`, `plaintext`, ecc.)
- [ ] Nota disclaimer finale presente con riferimento ai target autorizzati

### README padre (se si sta aggiornando un README di modulo)

- [ ] Registro Finding aggiornato con tutti i nuovi finding
- [ ] Tabella MITRE aggregata aggiornata
- [ ] Descrizione della sottocartella aggiornata nel README padre

### Tre dimensioni del report (Sezione 15)

- [ ] Dimensione TECNICA: output reali, CVSS score, finding ID, MITRE ID verificati
- [ ] Dimensione DESCRITTIVA: narrazione in prima persona (plurale) degli step eseguiti, problemi
  incontrati, decisioni prese nel vivo dell'esercizio
- [ ] Dimensione TEORICA: spiegazione del principio dietro la tecnica, motivazione della scelta
  metodologica, interpretazione del risultato nel contesto della kill chain
- [ ] Sezione "Scenario Reale" presente per i finding con severity Alto o Critico (Sezione 16)

---

## 15. Le Tre Dimensioni del Report

Ogni README tecnico di qualita deve bilanciare tre dimensioni distinte. Un documento che ne
manca anche solo una risulta incompleto agli occhi di un recruiter senior o di un cliente.

---

### Dimensione 1 - TECNICA

**Cosa e:** la documentazione precisa e riproducibile di quanto eseguito.

**Come si manifesta:**

- Comandi esatti con tutti i flag, in blocchi `bash`
- Output reali (o sintetici realistici) con annotazioni `<--`
- Finding ID nel formato standard, severity da scala CVSS v3.1
- ID MITRE ATT&CK verificati su attack.mitre.org
- Versioni degli strumenti quando rilevanti per la riproducibilita

**Template:**

```markdown
### Esecuzione del Test

Il tool e stato configurato con i parametri seguenti per massimizzare la copertura
mantenendo un rate basso che non triggerasse l'IDS del target.

```Bash
sudo nmap -sV -sC -p 80,443,8080 --script http-methods 10.0.2.3
```

```
PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache 2.4.41          <-- VULN-002: versione EOL
| http-methods:
|   Supported Methods: GET HEAD POST OPTIONS TRACE
|_  Potentially risky methods: TRACE             <-- XST possibile
```

**ID Finding:** `WEB-005` | **Severity:** `Medio` | **CVSS v3.1:** 6.1
```

---

### Dimensione 2 - DESCRITTIVA

**Cosa e:** la narrazione dell'esperienza vissuta durante il laboratorio. Trasforma un elenco
di comandi in una storia professionale che dimostra capacita di problem-solving e metodo.

**Come si manifesta:**

- Racconto in prima persona plurale ("si e osservato", "il test ha restituito", "ci si e trovati
  di fronte a") delle fasi eseguite in sequenza
- Documentazione dei problemi incontrati e di come sono stati risolti (troubleshooting)
- Descrizione dei momenti di decisione: perche si e scelto un tool invece di un altro, perche
  si e cambiato approccio a meta esercizio
- Risultati specifici ottenuti in questo laboratorio, non risultati generici della tecnica
- Note sulle differenze rispetto al comportamento atteso (ambiente virtualizzato, target
  hardened, risposta inaspettata)

**Template:**

```markdown
### Esperienza di Laboratorio

Il primo tentativo di enumerazione anonima e stato respinto dal target con il messaggio
`[E] Server doesn't allow session using username '', password ''`. Questo comportamento,
corretto dal punto di vista della difesa, ha richiesto un cambio di approccio: il test
e stato ripetuto fornendo credenziali utente standard per simulare uno scenario di
"Compromised Credentials" piu realistico.

Durante la fase di enumerazione autenticata si e osservato un dato inaspettato: l'account
`nessus_audit` (RID 1001), creato presumibilmente per scansioni Nessus precedenti, era
ancora attivo nel sistema. In un engagement reale questo rappresenterebbe un vettore
di attacco autonomo da investigare separatamente.

Il problema piu significativo incontrato e stato la latenza di rete tra macchina attaccante
e target in NAT VirtualBox: enum4linux ha impiegato circa 4 minuti per completare il
ciclo RID completo. In un ambiente fisico reale il tempo sarebbe significativamente ridotto.
```

---

### Dimensione 3 - TEORICA

**Cosa e:** la spiegazione del principio tecnico alla base della tecnica e l'interpretazione
contestuale dei risultati. Dimostra comprensione profonda, non solo esecuzione meccanica.

**Come si manifesta:**

- Spiegazione del protocollo o meccanismo sfruttato (a livello tecnico, non divulgativo)
- Motivazione della scelta dell'approccio rispetto alle alternative disponibili
- Interpretazione del risultato: cosa significa quel finding nel contesto dell'assessment,
  non solo come fatto isolato
- Collegamento con la kill chain: dove si e ora, cosa apre questo risultato in avanti
- Contestualizzazione rispetto all'architettura target (Windows vs Linux, rete interna vs DMZ)

**Template:**

```markdown
### Analisi Teorica

Il protocollo SMB (Server Message Block) e progettato per la condivisione di risorse in
reti Windows. La sua autenticazione si basa sul meccanismo NTLM Challenge-Response: il
client riceve un challenge dal server, lo combina con l'hash NTLM della password e invia
la risposta. Se SMB Signing non e obbligatorio, un attaccante in posizione di Man-in-the-Middle
puo intercettare questa risposta e usarla per autenticarsi altrove (SMB Relay Attack,
T1557.001) senza conoscere la password in chiaro.

La scelta di enum4linux rispetto a strumenti piu moderni come enum4linux-ng e stata dettata
dalla disponibilita nel laboratorio e dalla maggiore familiarita con il tool. In un engagement
professionale si preferirebbe enum4linux-ng per la gestione migliore degli errori e la
compatibilita con ambienti SMBv3.

Il finding VULN-004 (accesso C$ con credenziali standard) non e una vulnerabilita del
protocollo SMB in se, ma e il risultato di una cattiva gestione delle identita privilegiate:
un account con password debole e privilegi di amministratore locale annulla qualsiasi
restrizione di rete. Questo e il pattern piu comune nelle violazioni aziendali documentate
nel Verizon DBIR 2024: il vettore e quasi sempre la credenziale compromessa, non lo
zero-day.
```

---

### Come bilanciare le tre dimensioni

Le tre dimensioni non hanno sempre lo stesso peso. Adattare in base al tipo di documento:

| Tipo di README | Tecnica | Descrittiva | Teorica |
| :--- | :---: | :---: | :---: |
| Tecnica specifica (es. nmap, enum4linux) | Alta | Alta | Media |
| Exploitation (es. SQLi, SSTI, Drupalgeddon2) | Alta | Alta | Alta |
| Modulo introduttivo (es. README padre) | Bassa | Bassa | Alta |
| Secure Coding / Remediation | Media | Bassa | Alta |
| Scanner automatico (es. Nessus, Nikto) | Media | Alta | Bassa |

---

## 16. Proiezione verso lo Scenario Reale

Ogni README relativo a finding con severity `Alto` o `Critico` deve includere una sezione
che proietta il laboratorio verso uno scenario reale. Questa sezione risponde alla domanda:
"Se non fosse un laboratorio, cosa succederebbe adesso?"

La sezione deve essere presentata in due prospettive parallele: **attaccante** e **difensore**.

---

### Posizionamento nel documento

La sezione "Scenario Reale" si inserisce **dopo le Conclusioni e prima della tabella MITRE**,
separata da `---`. E un blocco autonomo, non una sottosezione della remediation.

---

### Template obbligatorio

```markdown
---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale, sia
> dal punto di vista dell'attaccante (Red Team) che del difensore (Blue Team).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** [stato raggiunto al termine del laboratorio]

**Passo successivo immediato:** [prima azione concreta che un attaccante farebbe]

**Kill Chain proiettata:**
```
[finding attuale]
        |
        v
[tecnica successiva] -> [obiettivo intermedio]
        |
        v
[tecnica successiva] -> [obiettivo finale: accesso, persistenza, esfiltrazione, ransomware]
```

**Impatto potenziale:** [conseguenza concreta per l'organizzazione target: perdita di dati,
cifratura dei sistemi, richiesta di riscatto, danno reputazionale]

**Vettori di monetizzazione tipici:**
- Ransomware: cifratura dei file + richiesta di riscatto in criptovaluta
- Data exfiltration: vendita di dati sul dark web (PII, IP, credenziali)
- Business Email Compromise: accesso a mailbox per frodi finanziarie
- Access Broker: rivendita dell'accesso iniziale ad altri threat actor

### Prospettiva Difensore (Blue Team)

**Rilevamento:** [come il SOC potrebbe rilevare questa attivita tramite log, SIEM, IDS]

**Indicatori di Compromissione (IOC):**
- [log event specifico, es. Event ID Windows]
- [pattern di traffico anomalo]
- [artefatto su disco o in memoria]

**Contenimento:** [azioni immediate per bloccare la progressione dell'attacco]

**Eradicazione e hardening:** [modifiche strutturali per prevenire recidiva]

**Lezione difensiva:** [principio di sicurezza dimostrato da questo finding]
```

---

### Esempio compilato (da SMB/VULN-004)

```markdown
## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come VULN-004 si inserirebbe in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** accesso alla share C$ di WINDOWS-TEST tramite credenziali nick/1234
con privilegi di amministratore locale.

**Passo successivo immediato:** dump delle credenziali in memoria con Mimikatz per ottenere
hash NTLM di tutti gli utenti che hanno effettuato login recente sulla macchina.

**Kill Chain proiettata:**

```
VULN-004: accesso C$ (nick - admin locale)
        |
        v
Mimikatz sekurlsa::logonpasswords -> hash NTLM Administrator di dominio
        |
        v
Pass-the-Hash / PTK su Domain Controller -> Domain Admin
        |
        v
DCSync (Replication) -> dump tutti gli hash del dominio
        |
        v
Persistenza: Golden Ticket (validita 10 anni) + creazione backdoor account
        |
        v
Ransomware deployment su tutti gli host via GPO / PsExec
```

**Impatto potenziale:** compromissione totale del dominio Active Directory. In un contesto
aziendale reale, questo scenario porta tipicamente a: cifratura di tutti i file server e
sistemi critici, esfiltrazione di dati sensibili (PII dipendenti, dati finanziari, IP),
richiesta di riscatto tra 100.000 e 5.000.000 USD (basato su casi documentati CISA 2024).

**Vettori di monetizzazione tipici:**
- Ransomware-as-a-Service (RaaS): gruppi come LockBit 3.0 o BlackCat/ALPHV
- Double extortion: riscatto per decriptare + riscatto per non pubblicare i dati
- Access Broker: rivendita dell'accesso iniziale su forum underground ($500 - $50.000)

### Prospettiva Difensore (Blue Team)

**Rilevamento:** l'accesso a C$ genera Event ID 4624 (Logon Type 3 - Network) e Event ID
5140 (A network share object was accessed) sui log di Windows Security. Un SIEM con regola
su "accesso C$ da IP non autorizzato" o "accesso share amministrativa in orario anomalo"
avrebbe triggerato un alert entro secondi.

**Indicatori di Compromissione (IOC):**
- Event ID 4624 con LogonType=3 + AccountName=nick + ShareName=C$
- Connessioni SMB in entrata su porta 445 da IP non presenti nella whitelist
- Creazione di file eseguibili in percorsi di sistema tramite share SMB

**Contenimento:** isolamento immediato della macchina dalla rete (quarantena switch port),
reset forzato delle credenziali nick e di tutti gli account amministrativi locali, revoca
di eventuali sessioni attive (Get-SMBSession | Close-SMBSession in PowerShell).

**Eradicazione e hardening:**
- Implementare Tiering Model: account standard != account admin (mai le stesse credenziali)
- Disabilitare le share amministrative nascoste (C$, ADMIN$) se non necessarie tramite GPO
- Abilitare Windows Defender Credential Guard per proteggere gli hash NTLM in memoria
- Implementare LAPS (Local Administrator Password Solution) per password uniche per macchina

**Lezione difensiva:** una password debole su un account con privilegi elevati annulla
qualsiasi difesa perimetrale. Il principio del Least Privilege (ogni account ha solo i
permessi minimi necessari) avrebbe limitato l'impatto anche in caso di compromissione
delle credenziali.
```

---

> Documento aggiornato con le tre dimensioni del report (Sezione 15) e la proiezione
> verso lo scenario reale (Sezione 16). Aggiornare la tabella "Stato di Avanzamento Lavori"
> (sezione 1) a ogni sessione di lavoro.
