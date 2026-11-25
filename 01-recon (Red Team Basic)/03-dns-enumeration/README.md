> [English](README.en.md) | **Italiano**

# 03 - DNS enumeration

> - **Fase:** Reconnaissance - DNS Enumeration
> - **Visibilita:** Zero / Bassa - da ricerca passiva su CT logs a query DNS standard
> - **Prerequisiti:** Dominio target identificato, accesso a Internet, tool `dig` / `dnsenum` / `Sublist3r`
> - **Output:** Zone transfer riuscito con esposizione completa della zona DNS (DNS-001), virtual host nascosti accessibili (DNS-002), 500+ sottodomini di un target enterprise (DNS-003)

---

## Introduzione

Il Domain Name System e la rubrica di Internet: mappa nomi a indirizzi IP, identifica i server di posta, gestisce la delega delle zone. Per un Red Team, il DNS e una fonte eccezionale di intelligence: ogni record pubblicato rivela un pezzo dell'infrastruttura del target.

La DNS Enumeration ha due obiettivi principali:

1. **Espandere la superficie di attacco:** trovare sottodomini non linkati dalla homepage principale (ambienti di sviluppo, pannelli admin, VPN, API gateway) che spesso presentano vulnerabilita critiche perche "dimenticati".

2. **Sfruttare misconfigurazioni:** il Zone Transfer (AXFR) e uno degli attacchi piu potenti in questa fase - se il server DNS e mal configurato, consegna all'attaccante l'intera topologia della rete in un singolo comando.

La distinzione fondamentale con il modulo `03-web-attacks/` e la seguente:
- **DNS Enumeration (questo modulo):** si cerca QUALI server/sottodomini esistono (es. `vpn.tesla.com` esiste a `1.2.3.4` con la porta 443 aperta)
- **Web Attack (03):** si analizza COSA gira dentro quei server (es. `vpn.tesla.com` usa Fortinet 7.0.1, vulnerabile a CVE-2023-XXXX)

---

## Struttura della cartella

```
03-dns-enumeration/
+-- README.md                <- questo file (indice + registro finding)
|
+-- dns-recon/
|   +-- README.md            <- DNS-001: zone transfer AXFR, NS/MX query (dig, dnsenum)
|   +-- img/                 <- screenshot del lab
|
+-- hosts-file/
|   +-- README.md            <- DNS-002: virtual host via /etc/hosts manipulation
|   +-- img/                 <- screenshot del lab
|
+-- subdomain-finding/
    +-- README.md            <- DNS-003: passive subdomain enumeration (Sublist3r, Assetfinder)
    +-- img/                 <- screenshot del lab
```

---

## `dns-recon/` - DNS recon e zone transfer

**ID Finding:** `DNS-001` | **Severity:** `Critico`

Il Zone Transfer (richiesta AXFR) e un meccanismo di replica DNS progettato per la sincronizzazione tra server primari e secondari. Se il server non limita l'accesso a IP trusted, chiunque puo richiedere una copia completa del database DNS del dominio.

**Risultato del lab su `zonetransfer.me`:** zone transfer riuscito. Estratti sottodomini critici solitamente nascosti: `vpn.`, `dev.`, `office.` con i relativi IP e record TXT interni.

Questo tipo di misconfiguration azzera completamente la "Security by Obscurity": l'attaccante ottiene la mappa completa della rete in un singolo comando `dig axfr`.

---

## `hosts-file/` - Virtual host discovery tramite /etc/hosts

**ID Finding:** `DNS-002` | **Severity:** `Medio`

I Virtual Host permettono a un singolo server web (Apache/Nginx) di servire piu siti distinti in base all'header `Host:` della richiesta HTTP. Se un sottodominio non e registrato nel DNS pubblico ma e configurato sul server, e accessibile solo modificando localmente il file `/etc/hosts`.

Questa tecnica e fondamentale in ambiente CTF e penetration test interno per accedere a pannelli admin, ambienti di staging o API endpoint non pubblicati ma raggiungibili dall'IP del server.

---

## `subdomain-finding/` - Passive subdomain enumeration

**ID Finding:** `DNS-003` | **Severity:** `Medio`

L'enumerazione passiva dei sottodomini sfrutta fonti di terze parti senza generare traffico verso il target: log di Certificate Transparency, archivi storici dei motori di ricerca, database pubblici come VirusTotal.

**Risultato del lab su `tesla.com`:** 500+ sottodomini unici identificati con `Sublist3r` e `Assetfinder`, inclusi target di alto valore come `sso.tesla.com`, `vpn.tesla.com`, `dev-app.tesla.com`.

I sottodomini trovati qui diventano scope diretto per il modulo `03-web-attacks/02-web-recon/`.

> **Tool moderno consigliato:** `amass enum -passive -d <DOMINIO>` - rispetto a Sublist3r (non piu mantenuto attivamente), amass interroga piu fonti (50+), integra i log Certificate Transparency e produce output strutturati in JSON per il post-processing automatizzato.

---

## Flusso operativo consigliato

```
[INPUT] Dominio target (es. tesla.com)
          |
          v
[1] Identificazione Name Server
     +-- host -t ns <DOMINIO>
     +-- dig ns <DOMINIO>
     -> Lista NS records
          |
          v
[2] Zone Transfer (testa sempre - a volte funziona ancora)
     +-- dig axfr @<NAMESERVER> <DOMINIO>
     +-- dnsenum <DOMINIO>
     -> Se riuscito: DNS-001 Critico, mappa completa della rete estratta
          |
     [Se fallisce]
          v
[3] Passive Subdomain Enumeration
     +-- sublist3r -d <DOMINIO> -o output.txt    # aggregazione motori ricerca
     +-- assetfinder --subs-only <DOMINIO>        # Certificate Transparency
     +-- amass enum -passive -d <DOMINIO>         # piu fonti, output strutturato
     -> Lista sottodomini
          |
          v
[4] Virtual Host Discovery (se IP noti)
     +-- Modifica /etc/hosts: <IP> <VHOST>
     +-- ffuf -w wordlist.txt -H "Host: FUZZ.<DOMINIO>" -u http://<IP>/
     -> VHost non pubblicati accessibili
          |
          v
[OUTPUT] Lista sottodomini + IP -> 03-web-attacks/02-web-recon/
```

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `dig` | dns query | cli | query dns avanzate, zone transfer axfr |
| `host` | dns query | cli | query dns rapide, ns/mx/a records |
| `dnsenum` | dns query | cli | automazione zone transfer + brute force sottodomini |
| `Sublist3r` | subdomain harvesting | cli (python) | aggregazione sottodomini da motori di ricerca |
| `Assetfinder` | subdomain harvesting | cli (go) | enumerazione via certificate transparency |
| `amass` | subdomain harvesting | cli (go) | standard owasp, 50+ fonti, json output |
| `ffuf` | vhost fuzzing | cli | brute force virtual host via header http |

> **Tool moderno consigliato:** `amass enum -passive -d <DOMINIO>` (OWASP) in sostituzione di Sublist3r, attivamente mantenuto con supporto a fonti moderne (Shodan, VirusTotal, Censys, BeVigil).

---

## Registro finding

| id | descrizione | severity | file |
| :--- | :--- | :---: | :--- |
| `DNS-001` | zone transfer riuscito su zonetransfer.me - zona dns completa esfiltrata | `Critico` | `dns-recon/README.md` |
| `DNS-002` | virtual host non pubblicato accessibile via /etc/hosts manipulation | `Medio` | `hosts-file/README.md` |
| `DNS-003` | 500+ sottodomini di tesla.com inclusi vpn, sso, dev-app | `Medio` | `subdomain-finding/README.md` |

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim network info: dns | `T1590.002` | zone transfer axfr su zonetransfer.me, estrazione completa dei record dns (DNS-001) |
| reconnaissance | search open technical databases: dns/passive dns | `T1596.001` | enumerazione sottodomini da certificate transparency e motori di ricerca (DNS-001, DNS-003) |

---

> **Nota:** Le attivita di DNS Enumeration sono state eseguite su target specificamente configurati per scopi didattici (`zonetransfer.me` di DigiNinja), su programmi bug bounty pubblici (`tesla.com`) e in laboratorio locale. Il Zone Transfer su `zonetransfer.me` e un comportamento intenzionale del servizio, progettato per l'addestramento alla sicurezza.
