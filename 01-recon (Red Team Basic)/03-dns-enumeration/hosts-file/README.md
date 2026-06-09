> [English](README.en.md) | **Italiano**

# DNS Enumeration: Local Hosts File Manipulation

> - **Fase:** Reconnaissance - DNS Enumeration
> - **Visibilita:** Zero - la modifica e locale alla macchina dell'analista, nessun traffico generato verso DNS esterni
> - **Prerequisiti:** IP del server target noto, nome del Virtual Host da testare (da subdomain-finding o altre fonti), accesso root per modificare /etc/hosts
> - **Output:** DNS-002 - Virtual Host non pubblicato nel DNS pubblico ma raggiungibile tramite manipolazione locale

---

Obiettivo: Forzare la risoluzione DNS locale per accedere a Virtual Hosts (VHosts) non indicizzati o ambienti di sviluppo nascosti.

---

## 1 Introduzione Teorica

Il file `/etc/hosts` (o `hosts` su Windows) funge da meccanismo di risoluzione dei nomi locale, con priorità rispetto ai server DNS esterni.

Virtual Hosting:

Molti server web (Apache/Nginx) ospitano più siti web sullo stesso indirizzo IP. Il server decide quale sito mostrare basandosi sull'header `Host:` della richiesta HTTP.
Se un sottodominio (es. `dev.target.com`) non è registrato nel DNS pubblico ma è configurato sul server, l'unico modo per un attaccante di visualizzarlo è mappare manualmente l'IP al nome di dominio nel proprio file `/etc/hosts`.

---

## 2 Esecuzione Tecnica

**ID Finding:** `DNS-002` | **Severity:** `Medio`

#### A. Verifica della Risoluzione (Prima della modifica)

Tentativo di connessione al dominio target prima della manipolazione locale.

Comando:
```Bash
ping -c 4 portale-segreto.corp
```

Risultato: ping: portale-segreto.corp: Name or service not known

Analisi: Il dominio non esiste nei DNS pubblici.

#### B. Hosts File Injection

Modifica del file di configurazione locale per associare forzatamente il dominio all'IP del target.

Comando:

```Bash
sudo nano /etc/hosts
# Aggiunta la riga:
# 10.0.2.3    portale-segreto.corp
```

![](./img/Screenshot_2026-02-07_19_34_45.jpg)

#### C. Verifica e Accesso (Dopo la modifica)

Verifica della raggiungibilità del target tramite il nome a dominio spoofato.

Comando:

```Bash
ping -c 3 portale-segreto.corp
```

![](./img/Screenshot_2026-02-07_19_34_44.jpg)

Analisi: Il sistema risolve correttamente il dominio verso l'IP 10.0.2.3. Ora è possibile lanciare attacchi (Nmap, Nikto, Burp Suite) direttamente contro portale-segreto.corp per testare le risposte specifiche del Virtual Host.

---

## 3 Conclusioni

Questa tecnica è essenziale nelle fasi di Web Application Penetration Testing e CTF, dove spesso i target sono nascosti dietro Virtual Host non pubblicati. La manipolazione del file hosts permette di interagire con la risorsa come se fosse un dominio legittimo.

---

## 4 Sviluppi futuri

Per completare l'analisi del servizio SMB e simulare uno scenario di attacco più avanzato, i prossimi passi previsti sono:

- Authenticated Enumeration (Grey Box Testing):
    
    Eseguire nuovamente `enum4linux` fornendo credenziali valide (simulate o ottenute tramite Brute Force) per mappare completamente utenti, gruppi e Password Policy, confrontando l'output con la scansione anonima.

- Utilizzo di Tool Moderni (NetExec / SMBMap):
    
    Testare strumenti di nuova generazione come NetExec (ex CrackMapExec) o SMBMap, che sono standard industriali per l'enumerazione veloce su grandi reti Active Directory.

- Password Spraying & Brute Force:
    
    Utilizzare strumenti come Hydra o Metasploit contro la porta 445 per tentare di indovinare le credenziali di accesso, basandosi sulla lista utenti (se ottenuta) o su dizionari comuni.

- Vulnerability Scanning Mirato:
    
    Verificare specificamente la presenza di vulnerabilità critiche storiche (es. MS17-010 EternalBlue o SMBGhost) utilizzando script NSE specifici o scanner di vulnerabilità.

La teoria (e una breve guida pratica) è presente in questo path: `cybersecurity-labs/02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.md`

---

## Analisi a Basso Livello: Virtual Host Resolution e HTTP Host Header

### Ordine di Risoluzione DNS nel Sistema Operativo

Quando un'applicazione (browser, curl, nmap) richiede la risoluzione di un nome, il sistema operativo segue un ordine di precedenza definito in `/etc/nsswitch.conf`:

```
# /etc/nsswitch.conf (Kali/Debian default)
hosts: files dns myhostname

# Ordine di risoluzione:
# 1. files  -> /etc/hosts (locale, priorita massima)
# 2. dns    -> query al resolver configurato in /etc/resolv.conf
# 3. myhostname -> hostname locale della macchina
```

La modifica del file `/etc/hosts` sfrutta questo ordine: inserendo un mapping `IP nome`, il resolver locale restituisce l'IP senza mai contattare il DNS esterno. Questo rende la tecnica completamente invisibile a qualsiasi monitoraggio di rete - nessuna query DNS viene generata.

### HTTP Host Header e Virtual Host Routing

Il meccanismo che rende questa tecnica operativamente utile e il Virtual Host routing nei web server. Apache e Nginx utilizzano l'header `Host:` della richiesta HTTP per selezionare quale configurazione servire:

```
# Richiesta HTTP generata dopo la modifica di /etc/hosts:
GET / HTTP/1.1
Host: portale-segreto.corp       <-- il web server usa questo valore
Connection: keep-alive            per selezionare il VirtualHost

# Configurazione Apache corrispondente:
<VirtualHost *:80>
    ServerName portale-segreto.corp
    DocumentRoot /var/www/portale-segreto
</VirtualHost>

<VirtualHost *:80>
    ServerName www.azienda.it     <-- VHost diverso, stesso IP
    DocumentRoot /var/www/sito-pubblico
</VirtualHost>
```

Senza la manipolazione dell'Host header (ottenuta tramite /etc/hosts), il browser invierebbe una richiesta con l'IP numerico, e il web server risponderebbe con il VHost di default - tipicamente il sito pubblico, non l'applicazione interna nascosta.

### VHost Discovery Automatizzata

La scoperta sistematica di Virtual Host nascosti si effettua tramite fuzzing dell'Host header con tool dedicati:

```Bash
# Gobuster in modalita vhost
gobuster vhost -u http://10.0.2.3 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# ffuf con filtro sulle risposte diverse dal default
ffuf -u http://10.0.2.3 -H "Host: FUZZ.target.com" \
     -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
     -fs 612    # filtra le risposte con dimensione del VHost default (Nginx 404)
```

Il principio: se la risposta HTTP per `Host: admin.target.com` differisce (dimensione, status code, contenuto) dalla risposta per un VHost inesistente, il VHost e attivo. Questa tecnica e fondamentale in CTF e in assessment dove il target espone applicazioni interne su VHost non pubblicati nel DNS.

---

## Esperienza di Laboratorio

L'esercizio ha reso tangibile un concetto che nella teoria appare banale: la separazione tra risoluzione DNS e routing HTTP. Prima della modifica di `/etc/hosts`, il ping verso `portale-segreto.corp` falliva con "Name or service not known" - il resolver non aveva modo di tradurre il nome in IP. Dopo l'aggiunta della riga nel file hosts, lo stesso comando ha ricevuto risposta immediata. Il punto chiave: il server target non e cambiato in alcun modo - e cambiato solo il modo in cui la macchina dell'analista interpreta il nome.

Questa tecnica e onnipresente in due contesti operativi: CTF (dove le sfide web richiedono quasi sempre di aggiungere entry nel file hosts per accedere ai VHost) e penetration test su applicazioni interne (dove gli ambienti di staging, development e admin sono spesso accessibili solo tramite VHost non pubblicati nel DNS pubblico). In entrambi i casi, la mancata modifica del file hosts porta a testare il VHost sbagliato - un errore che produce risultati apparentemente corretti ma completamente fuorvianti.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Defense Evasion | Modify Authentication Process | `T1556` | Manipolazione del file /etc/hosts per forzare la risoluzione di nomi non registrati nel DNS pubblico verso l'IP del target, bypassando i resolver esterni (DNS-002) |

---

> **Nota:** La tecnica di manipolazione del file /etc/hosts e stata applicata esclusivamente all'interno del laboratorio VirtualBox su un target autorizzato (10.0.2.3). Questa tecnica non altera il DNS pubblico e non ha effetti al di fuori della macchina locale dell'analista.