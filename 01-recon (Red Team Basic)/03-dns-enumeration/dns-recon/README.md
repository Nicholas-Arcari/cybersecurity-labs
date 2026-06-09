> [English](README.en.md) | **Italiano**

# Network Scanning: DNS Enumeration & Zone Transfers

> - **Fase:** Reconnaissance - DNS Enumeration
> - **Visibilita:** Bassa - query DNS standard verso i Name Server pubblici del target, compatibili con traffico legittimo
> - **Prerequisiti:** Dominio target noto, tool dig/host/dnsenum installati
> - **Output:** DNS-001 - Zone Transfer riuscito su zonetransfer.me con esfiltrazione completa della zona DNS (sottodomini critici vpn, dev, office)

---

Obiettivo: Mappare l'infrastruttura del dominio target identificando sottodomini, server di posta e tentare l'esfiltrazione dell'intera zona DNS (Zone Transfer).

Target Didattico: `zonetransfer.me` (Servizio di DigiNinja per test autorizzati)

Strumenti: `dig`, `host`, `dnsenum`

---

## 1 Introduzione Teorica

Il DNS (Domain Name System) opera tipicamente sulla porta 53 (UDP/TCP).

La DNS Enumeration è una tecnica che mira a individuare tutti i record associati a un dominio per espandere la superficie di attacco.

Cos'è un Zone Transfer (AXFR)?

È un meccanismo di replica del database DNS tra server primari e secondari. Se mal configurato (autorizzando richieste da qualsiasi IP), permette a un attaccante di scaricare l'intero elenco dei sottodomini e IP dell'organizzazione.

---

## 2 Esecuzione Tecnica

**ID Finding:** `DNS-001` | **Severity:** `Critico`

#### A. Identificazione dei Name Server (NS)

Prima di attaccare, bisogna sapere "chi" gestisce il DNS del target.

Comando:

```Bash
host -t ns zonetransfer.me
```

![](./img/Screenshot_2026-02-07_19_07_12.jpg)

Analisi: Identificati i server nsztm1.digi.ninja e nsztm2.digi.ninja.

#### B. Esecuzione del Zone Transfer (Attack)

Utilizzando il tool dig, interroghiamo il Name Server identificato chiedendo una copia completa della zona (axfr).

Comando:

```Bash
dig axfr @nsztm1.digi.ninja zonetransfer.me
```

![](./img/Screenshot_2026-02-07_19_14_13.jpg)

- `@nsztm1.digi.ninja`: Il server DNS a cui stiamo chiedendo i dati.
- `axfr`: La richiesta di trasferimento zona.

Analisi dei Dati Estratti: Dal dump sono emersi sottodomini critici solitamente nascosti:

- `vpn.zonetransfer.me` (Accesso remoto)
- `dev.zonetransfer.me` (Ambiente di sviluppo)
- `office.zonetransfer.me` (Rete interna)
- Commenti nei record TXT che rivelano dettagli interni.

#### C. Automazione con DNSenum

Per velocizzare il processo, si utilizza dnsenum che combina query Google, Brute Force e Zone Transfer in un unico comando.

Comando:

```Bash
sudo apt install dnsenum -y
dnsenum zonetransfer.me
```

![](./img/Screenshot_2026-02-07_19_10_13.jpg)
![](./img/Screenshot_2026-02-07_19_10_26.jpg)
![](./img/Screenshot_2026-02-07_19_10_33.jpg)

---

## 3 Conclusioni e Remediation

L'attacco ha avuto successo confermando una Critical Misconfiguration. L'esposizione completa della zona DNS annulla la "Security by Obscurity", fornendo all'attaccante la topologia completa della rete.

Remediation (Blue Team): Configurare il server DNS (es. BIND9 o Windows DNS) per consentire il Zone Transfer solamente agli indirizzi IP dei propri server DNS secondari (Allow-Transfer list), bloccando tutte le altre richieste.

---

## Analisi a Basso Livello: Protocollo AXFR e Struttura dei Record DNS

### Anatomia di una Query AXFR

Il Zone Transfer (AXFR, RFC 5936) opera su TCP porta 53 (a differenza delle query standard che usano UDP). Il protocollo segue una sequenza precisa:

```
Client                              Server DNS (NS autoritativo)
  |                                        |
  |--- TCP 3-way handshake (porta 53) --->|
  |                                        |
  |--- DNS Query: QTYPE=AXFR,            |
  |    QCLASS=IN, QNAME=zonetransfer.me ->|
  |                                        |
  |<-- DNS Response: SOA record ----------|  <-- inizio trasferimento
  |<-- DNS Response: tutti i record -------|  <-- A, AAAA, MX, CNAME, SRV, TXT...
  |<-- DNS Response: SOA record ----------|  <-- fine trasferimento (SOA ripetuto)
  |                                        |
  |--- TCP FIN --------------------------->|
```

Il primo e l'ultimo record della risposta AXFR sono sempre il SOA (Start of Authority) della zona: il client utilizza questa convenzione per determinare quando il trasferimento e completo. Ogni record nella risposta contiene il campo TTL (Time To Live), il tipo (A, MX, SRV, TXT, CNAME) e i dati associati.

### Record ad Alto Valore per il Red Team

Non tutti i record DNS hanno lo stesso valore operativo. In un zone transfer riuscito, i record piu critici sono:

| Tipo Record | Esempio dal dump | Valore per l'attaccante |
| :--- | :--- | :--- |
| **SRV** | `_kerberos._tcp.zonetransfer.me` | Rivela la presenza e posizione del Domain Controller (KDC) |
| **MX** | `mail.zonetransfer.me` | Identifica il mail server - target per relay abuse e phishing |
| **A** (interni) | `vpn.zonetransfer.me -> 10.x.x.x` | Mappa la rete interna senza scanning attivo |
| **TXT** | `"v=spf1 include:..."` | Rivela policy SPF/DKIM - utile per spoofing assessment |
| **CNAME** | `dev.zonetransfer.me -> aws.amazonaws.com` | Identifica servizi cloud - potenziale subdomain takeover |
| **HINFO** | `CPU: INTEL-386, OS: LINUX` | Fingerprinting OS senza scanning (raro ma devastante) |

### Protezione: TSIG (Transaction Signature)

La contromisura a livello di protocollo per gli AXFR non autorizzati e TSIG (RFC 2845). TSIG autentica le transazioni DNS tramite un HMAC-MD5 (o HMAC-SHA256) calcolato con una chiave simmetrica condivisa tra primary e secondary DNS:

```
# Configurazione BIND9 con TSIG
key "transfer-key" {
    algorithm hmac-sha256;
    secret "base64-encoded-shared-secret";
};

zone "azienda.it" {
    type master;
    allow-transfer { key "transfer-key"; };    <-- solo chi possiede la chiave
};
```

Con TSIG abilitato, una richiesta AXFR senza la chiave corretta riceve un `REFUSED` (RCODE 5) invece del dump della zona. Questa protezione e indipendente dall'IP sorgente, quindi funziona anche se l'attaccante spoofa l'IP del secondary DNS.

---

## Scenario Reale: Proiezione in un Engagement di Penetration Testing

> Questa sezione descrive come DNS-001 si inserirebbe in un engagement reale su un'infrastruttura aziendale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** dominio target noto (`azienda.it`); identificazione dei Name Server autoritativi tramite query NS; tentativo di zone transfer AXFR.

**Kill Chain proiettata:**

```
DNS-001: dig axfr @ns1.azienda.it azienda.it -> dump completo zona DNS
        |
        v
Analisi record: SRV (_kerberos._tcp) -> Domain Controller identificato
                 A (vpn, dev, staging) -> mappa rete interna
                 MX -> mail server per phishing mirato
                 TXT -> policy SPF debole per email spoofing
        |
        v
Scanning mirato sugli host interni rivelati (zero discovery noise)
        |
        v
Exploit su servizi interni (dev/staging spesso non patchati)
        |
        v
Lateral movement verso Domain Controller (gia identificato da SRV)
        |
        v
Compromissione AD completa
```

**Impatto potenziale:** un zone transfer riuscito elimina completamente la fase di discovery attiva. L'attaccante ottiene la mappa completa dell'infrastruttura senza inviare un singolo pacchetto di scansione - rendendo la ricognizione invisibile a IDS/IPS. In un report SANS del 2023, il 15% dei domini aziendali testati consentiva ancora zone transfer da IP arbitrari. I record SRV per Active Directory (`_ldap._tcp`, `_kerberos._tcp`, `_gc._tcp`) sono particolarmente devastanti: rivelano la posizione esatta dei Domain Controller, Global Catalog e servizi Kerberos.

**Vettori di monetizzazione tipici:**
- Ricognizione silenziosa: vendita della mappa DNS come intelligence su forum underground (Access Broker)
- Subdomain takeover: CNAME che puntano a servizi cloud dismessi possono essere rivendicati dall'attaccante
- Phishing mirato: record MX + policy SPF debole = spoofing email dall'interno del dominio

### Prospettiva Difensore (Blue Team)

**Rilevamento:** una query AXFR genera una connessione TCP sulla porta 53 con trasferimento dati significativo (decine di KB per zone piccole, MB per zone grandi). Questo pattern e anomalo: le query DNS legittime usano UDP e trasferiscono pochi byte.

**Indicatori di Compromissione (IOC):**
- Log DNS (BIND query log / Windows DNS Analytical): query di tipo AXFR da IP non presente nella lista dei secondary DNS autorizzati
- Firewall/IDS: connessione TCP porta 53 con durata anomala (>1 secondo) e volume dati elevato in risposta
- Pattern temporale: query AXFR ripetute verso tutti i NS del dominio in rapida successione (tool automatizzati come dnsenum)
- Risposta AXFR con RCODE 0 (Success) verso IP esterno alla lista `allow-transfer`

**Contenimento:** se un AXFR non autorizzato e rilevato, considerare l'informazione della zona come compromessa. Verificare se i record interni rivelati espongono servizi che dovrebbero essere accessibili solo da rete interna; aggiornare le regole firewall di conseguenza.

**Hardening strutturale:**
- Configurare `allow-transfer` con lista esplicita di IP dei secondary DNS (BIND9: `allow-transfer { 10.0.0.2; };`)
- Implementare TSIG (RFC 2845) per autenticazione crittografica dei trasferimenti - protegge anche da IP spoofing
- Windows DNS: configurare "Zone Transfers" -> "Only to the following servers" nella console DNS Manager
- Abilitare DNS query logging e integrare con SIEM per alert su query AXFR da IP non autorizzati
- Rimuovere record interni (dev, staging, vpn) dalla zona DNS pubblica - utilizzare split-horizon DNS con zona interna separata
- Audit periodico: `dig axfr @ns1.azienda.it azienda.it` dal proprio IP pubblico per verificare che il transfer sia bloccato

---

## Esperienza di Laboratorio

L'esercizio su zonetransfer.me ha reso tangibile la differenza tra teoria e impatto reale. La documentazione DNS descrive AXFR come un "meccanismo di replica tra server" - formulazione che minimizza il rischio. In pratica, il dump ha restituito decine di record che in un contesto aziendale avrebbero mappato l'intera infrastruttura: VPN, ambienti di sviluppo, rete interna, server di posta.

L'aspetto piu istruttivo e stato il confronto tra `dig` e `dnsenum`. Il comando `dig axfr` esegue una singola query AXFR pulita - efficace ma limitata a un solo NS. `dnsenum` automatizza l'intero workflow: identifica tutti i NS, tenta AXFR su ciascuno, e se il transfer fallisce prosegue con brute force dei sottodomini tramite wordlist. In un assessment reale, la ridondanza e fondamentale: il primary DNS puo avere il transfer bloccato mentre il secondary (gestito da un provider diverso con configurazione meno restrittiva) puo consentirlo.

Un dettaglio non ovvio: il zone transfer su zonetransfer.me ha restituito anche record TXT con commenti interni ("Robin Hood's forest", "Office PC") che in un contesto reale corrisponderebbero a note degli amministratori. Questi metadati sono spesso piu informativi dei record A/CNAME stessi - rivelano la funzione operativa degli host senza bisogno di ulteriore enumerazione.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Network Info: DNS | `T1590.002` | Zone Transfer AXFR su zonetransfer.me tramite dig e dnsenum, ottenendo l'elenco completo di sottodomini e IP inclusi vpn, dev e office (DNS-001) |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | Interrogazione dei Name Server pubblici del target per identificare record NS, MX e subzone trasferibili (DNS-001) |

---

> **Nota:** Il Zone Transfer documentato in questa sezione e stato eseguito su `zonetransfer.me`, un servizio pubblico mantenuto da DigiNinja specificamente configurato per permettere zone transfer a scopo didattico e di addestramento alla sicurezza. Nessun sistema di produzione e stato coinvolto.