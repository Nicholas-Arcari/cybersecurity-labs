# Infrastructure Intelligence: Passive Recon with Shodan & Censys

Obiettivo: Mappatura dell'infrastruttura tecnologica esposta su Internet utilizzando motori di ricerca per dispositivi (IoT) e certificati, senza interagire direttamente con i target (Zero-Touch Recon).

Target Case Study: Infrastrutture esposte a Parma (IT) Strumenti: `Shodan` (Web), `Censys` (Web), `Whois`

---

## 1 Introduzione Teorica

A differenza degli scanner attivi (come Nmap) che inviano pacchetti ai bersagli, strumenti come Shodan e Censys effettuano scansioni costanti dell'intero spazio indirizzi IPv4, archiviando le risposte (Banner) dei servizi. Questo permette agli analisti di sicurezza di interrogare un database storico per scoprire asset esposti, versioni software vulnerabili e configurazioni errate in modo totalmente passivo e invisibile agli IDS/IPS del bersaglio.

---

## 2 Esecuzione Tecnica: Shodan (IoT & Services)

Scenario: Ricerca di servizi RDP esposti

La ricerca si è concentrata sull'identificazione di server con Remote Desktop Protocol (RDP) esposti pubblicamente in una specifica area geografica. La porta 3389 è uno dei vettori principali per l'accesso iniziale dei gruppi Ransomware.

Query Shodan:

```Plaintext
port:3389 city:"Parma"
```

![](./img/Screenshot_2026-02-08_11_24_00.jpg)

Risultato Generale:

Analisi Macro: La ricerca ha restituito oltre 60 dispositivi esposti. L'analisi dei banner ha evidenziato gravi problemi di Information Disclosure:

- Nomi Host: Identificati nomi macchina specifici come `SERVER2022` (infrastruttura aziendale) e `PC-MARCO` (dispositivo personale).
- OS Fingerprinting: È possibile distinguere chiaramente tra macchine client (Windows 11) e server (Windows Server 2016/2022).

Analisi Approfondita dei Target (Deep Dive)

L'analisi dei dettagli forniti da Shodan su due host specifici ha rivelato configurazioni estremamente rischiose:

#### Target A (Workstation Esposta)

- IP: `2.118.xx.xx` (Business ISP)
- OS Fingerprinting: Shodan identifica il sistema operativo come Windows 11.

    Significato: Non è un server vero (Windows Server), ma una workstation. Probabilmente un PC usato da un dipendente o un tecnico, lasciato acceso e connesso direttamente a Internet (Business IP Telecom Italia).

- Web Server Anomalo (Porta 3080): C'è un server Apache attivo sulla porta non standard 3080.

    Significato: Spesso indica pannelli di amministrazione o software di test.
    
- Porta 2000 (Bandwidth Test?): La porta 2000 aperta con quel banner binario spesso appartiene a servizi di gestione router (MikroTik) o test di banda.

    Conclusioni: Questa macchina è un "colabrodo". Ha RDP (3389), Web (3080) e servizi di gestione esposti. È il classico PC "dimenticato" sotto la scrivania che permette a un attaccante di entrare nella rete aziendale.

![](./img/Screenshot_2026-02-08_11_27_39.jpg)

#### Target B (Critical Business Server)

Questo è un bersaglio critico. Guardando i domini e le porte, capiamo esattamente cosa fa questa azienda.

- IP: `87.26.xx.xx`
- Identity Disclosure: I domini associati sono `carosello.net` e `carosello.my3cx.it`.

    Significato: Abbiamo il nome dell'attività ("Carosello").

- VoIP System Esposto (Porte 5060, 5090 + dominio 3CX):

    Significato: Il dominio `my3cx.it` e le porte SIP indicano che questo server gestisce i Telefoni Aziendali (Centralino 3CX).

    Rischio: Se un hacker entra qui, può ascoltare le telefonate, deviare le chiamate o fare chiamate a pagamento a spese dell'azienda.

- File Server Esposto (Porta 21): C'è FileZilla Server attivo.

    Significato: Usano questo PC per scambiarsi file. Un attacco Brute Force qui potrebbe portare al furto di documenti aziendali.

- Remote Desktop (Porta 3389):

    Come sempre, la porta di gestione è aperta.

Verdetto: Questo singolo PC gestisce Telefoni, File e Accesso Remoto. Se cade questo PC (es. Ransomware), l'azienda si ferma completamente (niente telefono, niente dati).

![](./img/Screenshot_2026-02-08_11_28_14.jpg)

---

## 3 Integrazione OSINT: Identificazione dell'ISP (Whois)

Per completare la profilazione del target critico (`87.26.xx.xx`), è stata eseguita una query Whois per identificare il provider di servizi internet (ISP) e i contatti di abuso.

Comando:

```Bash
whois 87.26.xx.xx
```

![](./img/Screenshot_2026-02-08_11_33_05.jpg)

Analisi:

- `netname: TELECOM-ADSL-IPTV`:

    Ti dice che tipo di connessione è. Non è un data center (come Amazon AWS o Google Cloud), ma una normale linea ADSL/Fibra Business. Questo conferma che il server è fisicamente dentro l'ufficio o il negozio dell'azienda, non nel cloud.

- `descr: Telecom Italia S.p.A.`:

    Il proprietario dell'infrastruttura fisica (i cavi) è Telecom Italia. L'IP è noleggiato da loro.

- `abuse-mailbox: abuse@retail.telecomitalia.it`:

    Questa è la riga più importante per un Ethical Hacker. Se devi segnalare un attacco, un virus o una vulnerabilità grave (Responsible Disclosure), questa è l'email ufficiale a cui scrivere.

- `address: Via Oriolo Romano 240, 00189 Roma`:

    Attenzione: Questo NON è l'indirizzo del bersaglio (Carosello a Parma). Questo è l'indirizzo della sede legale di Telecom Italia a Roma. Il `whois` raramente ti dà l'indirizzo di casa del cliente per motivi di privacy.

Nota sulla Geolocalizzazione: Sebbene Shodan localizzi l'IP a Parma, l'analisi OSINT incrociata sui domini (`carosello.net`) e sulla Partita IVA ha rivelato che l'azienda opera principalmente in Liguria. Questa discrepanza è attribuibile all'instradamento dell'ISP e conferma l'importanza della verifica manuale dei dati automatici.


## 4 Esecuzione Tecnica: Censys (Validation & New Findings)

Scenario: Validazione incrociata (Cross-Reference) del target critico individuato su Shodan. L'obiettivo è analizzare i certificati TLS e scoprire servizi che potrebbero essere sfuggiti alla prima analisi.

Query Censys:

```text
ip: 87.26.xx.xx
```

Analisi dei Risultati (Nuove Scoperte): L'analisi su Censys ha arricchito il quadro di intelligence con dettagli critici sull'uso della macchina:

- Uso Promiscuo (Business + Personal): È stato identificato un servizio Plex Media Server sulla porta 32400. La presenza di un software di intrattenimento personale su un server che gestisce dati aziendali (FTP) e telefonia (VoIP) indica una gravissima violazione delle policy di sicurezza e un rischio elevato di compromissione accidentale.
- Conferma Identità (RDP Certificate): L'analisi del certificato SSL sulla porta 3389 conferma inequivocabilmente il nome host PC-Marco (CN=PC-Marco), corroborando i dati NetBIOS trovati da Shodan.
- Security Posture: Tutti i certificati rilevati (FTP, RDP) sono "Self-Signed" (non validati da una CA), esponendo le connessioni a possibili attacchi Man-in-the-Middle.

![](./img/Screenshot_2026-02-08_12_38_17.jpg)

![](./img/Screenshot_2026-02-08_12_39_08.jpg)

---

## 5 Ethical Handling (Gestione Etica)

In uno scenario reale, dopo aver identificato una criticità così elevata (Esposizione VoIP e Dati), la procedura corretta di Responsible Disclosure prevede:

- Attribuzione: Identificazione del proprietario tramite `lookup DNS` e `Whois`.
- Segnalazione: Invio di una comunicazione formale all'indirizzo `abuse@` dell'ISP o al contatto tecnico dell'azienda, fornendo i dettagli dell'esposizione senza mai tentare l'accesso (Exploitation).
- Remediation (Consigliata):

    - Chiudere immediatamente le porte 3389 (RDP), 21 (FTP) e 5060 (SIP) sul firewall perimetrale.
    - Implementare l'accesso esclusivamente tramite VPN.

---

## 6 Conclusioni

L'Infrastructure Intelligence ha permesso di mappare una superficie di attacco critica senza inviare un singolo pacchetto verso il bersaglio. Abbiamo identificato un'azienda reale che espone il cuore della propria operatività (Telefoni e File) su una linea consumer, rendendola vulnerabile ad attacchi Ransomware o di spionaggio industriale con uno sforzo minimo da parte di un attaccante.