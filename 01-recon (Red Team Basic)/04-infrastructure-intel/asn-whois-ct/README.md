> [English](README.en.md) | **Italiano**

# Perimeter mapping: ASN, WHOIS e certificate transparency

> - **Fase:** Reconnaissance - Infrastructure Intelligence (mappatura del perimetro)
> - **Visibilita:** Zero - interrogazione di registri pubblici (RIR, WHOIS) e log di Certificate Transparency; nessun pacchetto inviato all'infrastruttura del target
> - **Prerequisiti:** Nome dell'organizzazione o dominio target, accesso a Internet
> - **Output:** Range IP posseduti dal target (blocchi CIDR), Autonomous System Number, sottodomini nascosti da certificati, perimetro di rete completo, finding INTEL-005

---

## Introduzione

Prima di scansionare, un attaccante deve sapere **cosa appartiene** al target. Molte organizzazioni non possiedono un solo IP ma interi blocchi di indirizzi (CIDR) annunciati sotto un proprio Autonomous System (AS). Identificare l'ASN e i range IP associati significa scoprire l'intero perimetro di rete di proprieta - inclusi server, servizi e ambienti che non compaiono in una semplice risoluzione DNS del dominio principale.

Parallelamente, i log di **Certificate Transparency (CT)** offrono una fonte di sottodomini che l'enumerazione DNS tradizionale non trova. Ogni volta che viene emesso un certificato TLS, la Certificate Authority lo registra in log pubblici e append-only (previsti dallo standard RFC 6962). Questi log contengono il Common Name e i Subject Alternative Name del certificato: cioe i nomi di dominio, inclusi sottodomini interni (`vpn.`, `dev.`, `jenkins.`, `admin.`) che l'organizzazione non ha mai pubblicato ma per cui ha richiesto un certificato.

La combinazione di ASN/WHOIS (perimetro IP) e Certificate Transparency (perimetro DNS) produce la mappa completa della superficie di attacco esterna, in modo totalmente passivo. Questa sezione completa la fase di Infrastructure Intelligence iniziata con `shodan-censys/` (INTEL-001..003): mentre Shodan dice "cosa e esposto", ASN/WHOIS e CT dicono "cosa esiste e a chi appartiene".

---

## Struttura della cartella

```
asn-whois-ct/
+-- README.md            <- questo file (INTEL-005: mappatura del perimetro)
+-- img/                 <- screenshot del lab (crt.sh, output amass intel, bgp.he.net)
```

---

## ASN e WHOIS - identificazione dei range IP di proprieta

**ID Finding:** `INTEL-005` | **Severity:** `Variabile (Informativo / Medio)`

### Contesto operativo

L'Autonomous System Number identifica una rete che annuncia i propri prefissi IP tramite BGP. Le grandi organizzazioni hanno un proprio ASN; le piccole usano quello dell'ISP. Partendo dal nome dell'organizzazione o da un singolo IP noto, si risale all'ASN e da questo a tutti i blocchi CIDR annunciati. La severity e `Informativo` per la sola mappatura, ma sale a `Medio` quando la mappatura rivela range o servizi non previsti dal target (shadow IT, ambienti dimenticati).

### Esecuzione

Risoluzione WHOIS di un IP noto per estrarre l'ASN e il blocco di rete:

```Bash
# WHOIS di un IP per ottenere netname, org e range CIDR
whois 8.8.8.8 | grep -Ei "netname|origin|route|orgname|cidr"
```

Output atteso:

```
NetRange:       8.8.8.0 - 8.8.8.255
CIDR:           8.8.8.0/24                     <-- blocco IP di proprieta
OriginAS:       AS15169                        <-- ASN del target
OrgName:        Google LLC                     <-- proprietario
```

Enumerazione di tutti i prefissi annunciati da un ASN (via WHOIS del RIR o tool dedicati):

```Bash
# Tutti i prefissi IPv4 annunciati da un ASN
whois -h whois.radb.net -- '-i origin AS15169' | grep -Eo "([0-9.]+){4}/[0-9]+" | sort -u

# In alternativa, amass intel risale da nome org a range IP e ASN
amass intel -org "Target Corp"
amass intel -asn 15169
```

Output atteso (amass intel):

```
15169, GOOGLE - Google LLC, US
8.8.8.0/24
8.8.4.0/24
34.64.0.0/10                                   <-- range da includere nello scope di scan
...
```

> [Segnaposto screenshot: catturare la vista di `bgp.he.net` (Hurricane Electric BGP Toolkit) per l'ASN del target, che mostra graficamente tutti i prefissi annunciati e i peer.]

<!-- screenshot placeholder: BGP Toolkit - prefissi ASN (img/asn-bgp-PLACEHOLDER.jpg) -->

### Analisi dei risultati

I blocchi CIDR identificati diventano lo **scope IP** per la fase di network scanning attivo (`02-network-scanning-active/`). Trovare un range non documentato o servizi in un blocco "dimenticato" e un finding di per se: indica shadow IT o asset non gestiti dal team di sicurezza, spesso i piu vulnerabili.

---

## Certificate transparency - sottodomini nascosti dai certificati

### Contesto operativo

I log di Certificate Transparency sono la fonte di enumerazione sottodomini piu efficace e piu passiva disponibile. Non richiedono interazione con i DNS del target: si interroga un indice pubblico (crt.sh, Censys, il tool `ctfr`) dei certificati emessi. Poiche oggi quasi tutti i servizi usano HTTPS, ogni sottodominio ha quasi certamente un certificato, e quindi compare nei log CT - anche i sottodomini interni mai pubblicati.

### Esecuzione

Interrogazione di crt.sh via API JSON (interamente passiva):

```Bash
# Estrazione di tutti i nomi dai certificati emessi per il dominio target
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u

# Tool dedicato che interroga i log CT
ctfr -d target.com
```

Output atteso:

```
target.com
www.target.com
mail.target.com
vpn.target.com                                 <-- vettore accesso remoto
dev.target.com                                 <-- ambiente di sviluppo (meno protetto)
jenkins.target.com                             <-- INTEL-005: CI/CD esposto in CT
staging-admin.target.com                       <-- pannello admin interno
*.internal.target.com                          <-- wildcard interno rivelato dal certificato
```

> [Segnaposto screenshot: catturare la vista web di crt.sh per il dominio target con la lista dei certificati emessi e i relativi SAN.]

### Analisi dei risultati / finding documentato

I sottodomini con nomi come `jenkins`, `dev`, `staging`, `admin`, `vpn`, `gitlab` sono i piu preziosi: rappresentano infrastruttura di supporto (CI/CD, ambienti non-produzione, pannelli di gestione) tipicamente meno protetta della produzione e non progettata per l'esposizione. Un certificato wildcard interno (`*.internal.target.com`) che compare nei log CT rivela addirittura la convenzione di naming della rete interna.

La lista prodotta e input diretto per:
- `03-dns-enumeration/subdomain-finding/` (DNS-003) per la risoluzione e validazione
- `03-web-attacks/02-web-recon/` per il probing dei sottodomini vivi
- `shodan-censys/` per verificare quali di questi sono esposti pubblicamente

---

## Esperienza di laboratorio

L'enumerazione e stata eseguita su domini autorizzati a scopo didattico o inclusi in programmi bug bounty pubblici, senza inviare alcun pacchetto all'infrastruttura del target. Il confronto tra l'enumerazione via Certificate Transparency e la classica enumerazione DNS ha mostrato il valore dei log CT: emergono sottodomini di supporto (ambienti di sviluppo, pannelli, servizi interni) che la sola risoluzione DNS non rivela, perche la loro esistenza e tradita dai certificati emessi. La contropartita, verificata durante il lab, e che i log CT contengono anche certificati vecchi o revocati: una parte dei nomi trovati non e piu risolvibile o non punta piu a un host vivo, per cui e stato necessario un passo di validazione (risoluzione DNS e probing) prima di considerarli parte reale della superficie. La decisione principale e stata proprio nel filtraggio: distinguere i sottodomini attivi da quelli storici e dare priorita agli ambienti non-produzione e agli accessi remoti, che sono gli obiettivi a piu alto valore per le fasi successive.

Punti di attenzione tipici, da verificare durante l'esecuzione:

- I log CT contengono anche certificati scaduti o revocati: un sottodominio presente in CT non e necessariamente attivo. Va validato con risoluzione DNS (semi-passiva) o probing HTTP (attivo) nelle fasi successive.
- I certificati wildcard (`*.target.com`) nascondono i sottodomini specifici: in quel caso CT rivela l'esistenza del wildcard ma non i singoli host, che vanno cercati con altre tecniche.
- crt.sh puo essere lento o rate-limitato su domini con migliaia di certificati: in quel caso preferire l'API di Censys o `subfinder` (che aggrega anche fonti CT).

### Analisi teorica

Certificate Transparency nasce come contromisura difensiva: dopo casi di CA compromesse che emettevano certificati fraudolenti (es. DigiNotar 2011), Google ha imposto che ogni certificato affidabile sia registrato in log pubblici verificabili, cosi che un dominio possa accorgersi di certificati emessi a sua insaputa. Il side effect per la ricognizione e che questi stessi log rivelano l'intera struttura di sottodomini di un'organizzazione. E un esempio perfetto del principio per cui una misura di sicurezza (trasparenza dei certificati) crea una nuova superficie informativa sfruttabile in fase di recon.

Sul piano del routing, l'associazione ASN-prefissi si basa su BGP: gli annunci BGP sono pubblici per necessita (servono a instradare il traffico su Internet), quindi chiunque puo osservare quali prefissi un AS annuncia. Non esiste modo di "nascondere" questa informazione senza rinunciare alla raggiungibilita. Questo rende ASN e CT le due fonti piu affidabili e non evitabili della ricognizione passiva del perimetro.

---

## Flusso operativo consigliato

```
[INPUT] Nome organizzazione o dominio target
          |
          v
[1] Da nome org a IP/ASN
     +-- amass intel -org "Target Corp"    -> ASN candidati
     +-- whois <IP_noto>                    -> netname, OriginAS, CIDR
          |
          v
[2] Da ASN a tutti i prefissi CIDR
     +-- amass intel -asn <ASN>             -> lista blocchi IP
     +-- bgp.he.net (BGP Toolkit web)       -> prefissi + peer
     -> scope IP per network scanning attivo
          |
          v
[3] Sottodomini da Certificate Transparency
     +-- curl crt.sh?q=%25.target.com       -> tutti i nomi nei certificati
     +-- ctfr -d target.com / subfinder     -> aggregazione fonti CT
     -> sottodomini nascosti (vpn, dev, jenkins, admin)
          |
          v
[4] Validazione e prioritizzazione
     +-- filtrare host vivi, prioritizzare ambienti non-prod e accessi remoti
          |
          v
[OUTPUT] Perimetro completo (IP + DNS) -> 02-network-scanning, 03-web-attacks, shodan-censys
```

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `whois` | osint | cli | risoluzione ip/dominio a netname, asn, contatti, cidr |
| `amass intel` | osint/asn | cli | da nome org a asn e range ip, aggregazione ct |
| `crt.sh` | certificate transparency | web / api | enumerazione sottodomini dai log ct |
| `ctfr` | certificate transparency | cli (python) | enumerazione sottodomini via ct logs |
| `subfinder` | subdomain enum | cli | aggregazione multi-fonte (inclusa ct) di sottodomini |
| `bgp.he.net` | asn/bgp | web | bgp toolkit: prefissi, peer, grafo dell'as |
| `dnsx` / `httpx` | validation | cli | validazione host vivi dai sottodomini trovati |

> **Tool moderno consigliato:** `amass` (OWASP) integra in un unico tool l'intelligence ASN (`amass intel`), l'enumerazione da Certificate Transparency e la correlazione passiva DNS, sostituendo la combinazione di whois + crt.sh + tool separati. Per la sola CT, `subfinder -d target.com -all` e piu veloce e aggrega decine di fonti passive.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim network info: ip addresses | `T1590.005` | identificazione dei blocchi cidr di proprieta del target tramite whois e amass intel (INTEL-005) |
| reconnaissance | gather victim network info: network topology | `T1590.004` | ricostruzione del perimetro di rete tramite asn e prefissi bgp annunciati (INTEL-005) |
| reconnaissance | search open technical databases: whois | `T1596.002` | interrogazione dei registri whois dei rir per associare ip, organizzazione e asn (INTEL-005) |
| reconnaissance | search open technical databases: digital certificates | `T1596.003` | enumerazione di sottodomini nascosti tramite i log di certificate transparency (INTEL-005) |
| reconnaissance | gather victim network info: dns | `T1590.002` | scoperta di sottodomini interni (vpn, dev, jenkins) dai subject alternative name dei certificati (INTEL-005) |

---

> **Nota:** Le interrogazioni WHOIS, ASN e Certificate Transparency documentate in questa sezione sono state eseguite su registri e log pubblici, senza alcun contatto con l'infrastruttura dei target. I domini usati sono target autorizzati a scopo didattico o programmi bug bounty pubblici. La sola enumerazione del perimetro non costituisce accesso: nessuna scansione attiva o tentativo di connessione e stato eseguito sui range identificati senza autorizzazione esplicita.
