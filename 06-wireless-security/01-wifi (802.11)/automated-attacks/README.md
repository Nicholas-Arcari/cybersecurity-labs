> [English](README.en.md) | **Italiano**

# Automated Attacks - Wifite2 & Airgeddon

> - **Fase:** Wireless Security - Attack Automation & Orchestration (802.11)
> - **Visibilita:** Alta - gli attacchi automatici includono deautenticazione, WPS PIN bruteforce e cattura handshake, tutti rilevabili da un WIDS
> - **Prerequisiti:** Monitor mode attiva (vedere `../recon-monitor/`); wordlist configurate; comprensione dei singoli attacchi (`../cracking/`, `../rogue-ap/`) per interpretare i risultati
> - **Output:** WIFI-005; audit wireless completo automatizzato su piu target; handshake/PMKID catturati; PIN WPS recuperati; PSK craccate in un'unica sessione

- **Ambiente Operativo:** Kali Linux (Attaccante), scheda monitor + injection, reti WPA2/WPS di laboratorio
- **Target:** Reti multiple di test, incluso un AP con WPS abilitato
- **Tool principali:** Wifite2, Airgeddon, reaver, bully

---

## Executive Summary

Gli attacchi manuali documentati nelle sezioni precedenti (`recon-monitor`, `cracking`, `rogue-ap`) sono didatticamente essenziali ma non scalano su un audit reale con decine di reti. Wifite2 e Airgeddon automatizzano l'intera catena: scansione, prioritizzazione dei target per potenza di segnale e vulnerabilita, esecuzione sequenziale di tutti gli attacchi applicabili (handshake, PMKID, WPS Pixie-Dust, WPS PIN bruteforce), e cracking finale.

Il valore di questi orchestratori non e fare qualcosa che i tool manuali non fanno, ma farlo in modo sistematico e ripetibile: Wifite2 prova automaticamente l'attacco piu efficiente per ogni target e passa al successivo, producendo un audit completo mentre l'operatore analizza altro. Il finding WIFI-005 documenta in particolare l'attacco WPS Pixie-Dust, che sfrutta una debolezza implementativa per recuperare il PIN WPS (e quindi la PSK) in secondi, indipendentemente dalla robustezza della password.

---

## Struttura della cartella

```
automated-attacks/
+-- README.md      # questo file: Wifite2 orchestration + WPS Pixie-Dust (WIFI-005)
+-- img/           # screenshot sessione Wifite2
```

---

## Wifite2 - Audit Wireless Automatizzato

**ID Finding:** `WIFI-005` | **Severity:** `Alto` (WPS Pixie-Dust: PIN WPS recuperato in secondi, PSK compromessa indipendentemente dalla robustezza)

### Contesto operativo

Wifite2 e un wrapper Python attorno all'intera suite aircrack-ng, hcxdumptool, reaver e bully. Presenta una lista di target ordinata per potenza e permette di selezionare gli obiettivi; per ognuno esegue automaticamente la sequenza di attacchi piu promettente, gestendo deauth, cattura e cracking senza intervento manuale.

### PoC - Sessione Wifite2

```Bash
# Avvio con targeting su WPA/WPS e uso della wordlist di default
sudo wifite --wpa --wps --dict /usr/share/wordlists/rockyou.txt
```

```
   NUM  ESSID              CH  ENCR   POWER  WPS  CLIENT
   ---  --------           --  -----  -----  ---  ------
   1    LAB-CORP            6  WPA2    58db   no    1
   2    LAB-WPS-AP         11  WPA2    52db   yes   0        <-- WPS abilitato (vulnerabile)
   3    LAB-GUEST           1  WPA2    41db   no    0

[+] select target(s) (1-3): 2

[+] LAB-WPS-AP (11): attacco WPS Pixie-Dust
[+] Pixie-Dust: raccolta hash WPS dal primo scambio EAP...
[+] Pixie-Dust: PIN trovato: 12345670                        <-- PIN WPS recuperato (WIFI-005)
[+] WPS PIN 12345670 -> recupero PSK...
[+] PSK: SummerBreeze2025                                    <-- PSK ottenuta senza dizionario
[+] risultati salvati in cracked.txt
```

L'aspetto critico: la PSK `SummerBreeze2025` non e presente in rockyou.txt e resisterebbe a un attacco a dizionario. Ma il WPS Pixie-Dust la bypassa completamente, recuperando prima il PIN WPS (una debolezza implementativa) e poi derivando la PSK dal PIN.

### Remediation

- **Azione immediata:** disabilitare WPS su tutti gli access point (`WPS: Disabled` nel pannello di amministrazione). WPS e la vulnerabilita: la sua disabilitazione neutralizza sia Pixie-Dust che il PIN bruteforce, senza impatto sulla connettivita (gli utenti usano la PSK)
- **Azione strutturale:** su parchi AP gestiti, applicare via controller una policy globale che forza WPS disabilitato; verificare in fase di procurement che gli AP permettano la disabilitazione completa (alcuni firmware mantengono WPS attivo internamente anche se l'interfaccia lo mostra disabilitato); migrare a WPA3, che non prevede WPS
- **Verifica:** rieseguire Wifite2 dopo la modifica per confermare che la colonna WPS mostri `no` su tutti gli AP

---

## Airgeddon - Framework Multi-Attacco

### Contesto operativo

Dove Wifite2 eccelle nell'automazione da riga di comando, Airgeddon offre un menu interattivo completo che copre anche gli attacchi Evil Twin (vedere `../rogue-ap/`), gli attacchi WEP legacy e la gestione integrata delle interfacce. E utile come "coltellino svizzero" wireless in un unico strumento guidato.

```Bash
sudo airgeddon
# Menu principale: gestione interfacce -> DoS -> Handshake tools ->
#                  Offline WPA/WPA2 decrypt -> Evil Twin -> WPS attacks
```

---

## Esperienza di Laboratorio

L'automazione ha mostrato immediatamente il suo valore: in una singola sessione Wifite2 ha auditato tre reti, catturando un handshake su `LAB-CORP` e recuperando la PSK di `LAB-WPS-AP` via WPS in meno di un minuto. Il contrasto con il flusso manuale (sezione `cracking`) e netto: cio che manualmente richiede il coordinamento di tre terminali (airodump, aireplay, aircrack) qui e una singola scelta di target.

Il risultato piu istruttivo e stato il WPS Pixie-Dust su `LAB-WPS-AP`. La PSK era robusta e sarebbe stata immune a un attacco a dizionario, ma il WPS abilitato ha reso irrilevante la password. Questo ha ribaltato la mia priorita di audit: prima cercare WPS attivo (vittoria rapida e certa), poi tentare handshake/PMKID (dipendente dalla wordlist). L'automazione non solo velocizza, ma insegna l'ordine di priorita corretto degli attacchi.

Un limite pratico osservato: gli orchestratori nascondono i dettagli, e quando un attacco fallisce e piu difficile diagnosticare il perche rispetto all'esecuzione manuale. Wifite2 e ideale per la copertura ampia, ma la comprensione dei tool sottostanti resta indispensabile per il troubleshooting e per gli scenari non standard.

---

## Analisi Teorica: La Debolezza del WPS Pixie-Dust

Il WPS (Wi-Fi Protected Setup) nasce per semplificare la connessione tramite un PIN di 8 cifre. La sua prima debolezza (2011, Viehbock) e strutturale: il PIN viene validato in due meta separate (prime 4 cifre + ultime 3 + 1 di checksum), riducendo lo spazio di ricerca da 10^8 a circa 11.000 combinazioni - bruteforce fattibile in ore (attacco reaver/bully).

Il Pixie-Dust (2014, Bongard) e piu devastante: sfrutta la debole generazione di numeri casuali (i nonce E-S1 ed E-S2) in molti chipset (Ralink, Broadcom, Realtek). Se questi nonce sono prevedibili o nulli, il PIN puo essere ricavato offline dai valori scambiati nel primo messaggio EAP, senza alcun bruteforce online: da ore a secondi.

La conseguenza teorica e importante: WPS introduce un canale di autenticazione parallelo piu debole della PSK. Anche una passphrase WPA2 perfetta e inutile se WPS e abilitato con un chipset vulnerabile, perche l'attaccante non attacca la PSK ma il PIN, da cui l'AP stesso deriva e consegna la PSK. E l'esempio da manuale di come una funzione di comodita (setup semplificato) possa annullare una difesa robusta: la sicurezza di un sistema e quella del suo anello piu debole, non della sua componente piu forte.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Wifite2` | Attack automator | CLI | Audit automatizzato: handshake, PMKID, WPS su target multipli |
| `Airgeddon` | Multi-attack framework | CLI - Menu | Coltellino svizzero wireless: DoS, handshake, Evil Twin, WPS |
| `reaver` | WPS PIN attack | CLI | Bruteforce online del PIN WPS (8 cifre, spazio ridotto) |
| `bully` | WPS PIN attack | CLI | Alternativa a reaver, piu robusta su alcuni chipset |
| `hcxdumptool` | Clientless capture | CLI | Cattura PMKID integrata nei flussi automatici |

> **Tool moderno consigliato:** `Wifite2` resta lo standard per l'automazione nel 2024-2026 grazie all'integrazione di hcxdumptool per il PMKID e al supporto del formato hashcat 22000. Per gli audit enterprise su 802.1X, affiancarlo a `eaphammer` (vedere `../rogue-ap/`).

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force | `T1110` | WPS PIN bruteforce (reaver/bully) e Pixie-Dust per recuperare il PIN e derivare la PSK (WIFI-005) |
| Credential Access | Network Sniffing | `T1040` | Cattura automatizzata di handshake e PMKID su target multipli |
| Collection | Adversary-in-the-Middle | `T1557` | Deautenticazione automatizzata per forzare la cattura degli handshake |
| Initial Access | Valid Accounts | `T1078` | Utilizzo delle PSK recuperate per accedere alle reti target |

---

> **Nota:** Tutte le attivita documentate sono state condotte su reti WiFi di laboratorio di proprieta dell'autore. Gli attacchi automatizzati (deauth, WPS, cattura handshake) sono stati eseguiti esclusivamente contro AP di test in ambiente radio isolato. L'uso di questi strumenti contro reti di terzi senza autorizzazione costituisce reato. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
