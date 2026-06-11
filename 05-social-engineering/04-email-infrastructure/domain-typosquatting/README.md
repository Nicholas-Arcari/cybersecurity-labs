> [English](README.en.md) | **Italiano**

# Domain Typosquatting - Generazione Domini Confondibili

> - **Fase:** Social Engineering - Resource Development (Infrastruttura di Attacco)
> - **Visibilita:** Bassa - la generazione e l'analisi dei domini e passiva (query DNS/WHOIS); la registrazione di un dominio e tracciabile tramite WHOIS e Certificate Transparency logs
> - **Prerequisiti:** dnstwist o URLCrazy installato; accesso a Internet per query DNS in tempo reale; per acquisto: registrar di domini con pagamento anonimo (opzionale)
> - **Output:** SE-012 (domini confondibili non registrati identificati per il dominio target - severity Informativo)

- **Ambiente Operativo:** Kali Linux Purple
- **Target:** Dominio aziendale simulato (target-lab.com)
- **Framework:** dnstwist 20240812, URLCrazy
- **Tecniche Documentate:** Homoglyph Generation, Bit-flip Domains, TLD Swap, Omission/Transposition

---

## Executive Summary

Il typosquatting e la tecnica di registrazione di domini visivamente simili al dominio target per ingannare gli utenti. Un dominio come `target-1ab.com` (con cifra "1" al posto della lettera "l") e quasi indistinguibile da `target-lab.com` nella maggior parte dei font. Combinato con un certificato TLS valido (Let's Encrypt e gratuito e automatico), il dominio typosquatting rende le email e le landing page di phishing estremamente credibili.

Il laboratorio ha utilizzato `dnstwist` per generare sistematicamente tutte le variazioni del dominio target e identificare quelle non ancora registrate, disponibili per l'acquisto da parte di un attaccante.

---

## Typosquatting: Domain Permutation Analysis

**ID Finding:** `SE-012` | **Severity:** `Informativo`

### PoC - Fase 1: Generazione Variazioni

```Bash
dnstwist --all --registered target-lab.com
```

```
     _           _            _     _
  __| |_ __  ___| |___      _(_)___| |_
 / _` | '_ \/ __| __\ \ /\ / / / __| __|
| (_| | | | \__ \ |_ \ V  V /| \__ \ |_
 \__,_|_| |_|___/\__| \_/\_/ |_|___/\__|

domain                type           a             mx
target-lab.com        original       93.184.216.34 mx.target-lab.com
targat-lab.com        replacement    -             -                  <-- disponibile
target-1ab.com        homoglyph      -             -                  <-- disponibile (l->1)
targt-lab.com         omission       -             -                  <-- disponibile (e omessa)
targe-tlab.com        insertion      -             -                  <-- disponibile
target-alb.com        transposition  -             -                  <-- disponibile
target-lab.co         tld-swap       203.0.113.5   -                  <-- registrato
targetlab.com         omission       198.51.100.1  mx.parked.com     <-- registrato (parked)
target-lab.net        tld-swap       -             -                  <-- disponibile
target-lab.org        tld-swap       -             -                  <-- disponibile
```

### PoC - Fase 2: Analisi Rischio per Tipo

```Bash
# Conteggio variazioni per tipo
dnstwist --all target-lab.com --format csv | tail -n +2 | cut -d',' -f2 | sort | uniq -c | sort -rn
```

```
  12 replacement        <-- sostituzione singolo carattere
   8 homoglyph          <-- caratteri visivamente simili (l/1, O/0, rn/m)
   6 omission           <-- carattere mancante
   5 insertion          <-- carattere aggiuntivo
   4 transposition      <-- caratteri invertiti
   3 tld-swap           <-- cambio TLD (.com->.net/.org)
   2 addition           <-- carattere in coda
   1 bitsquatting       <-- bit-flip hardware (raro ma documentato)
```

### PoC - Fase 3: Valutazione Impatto Visivo

I domini piu pericolosi sono quelli con la minore distanza visiva dall'originale:

```
RISCHIO ALTO (indistinguibili in molti font):
  target-1ab.com   (l -> 1)    <- omoglifo: quasi impossibile da distinguere
  target-Iab.com   (l -> I)    <- omoglifo maiuscola
  tarqet-lab.com   (g -> q)    <- sostituzione a bassa distanza

RISCHIO MEDIO (richiedono attenzione):
  targat-lab.com   (e -> a)    <- sostituzione vicina sulla tastiera
  target-alb.com   (lab -> alb) <- trasposizione

RISCHIO BASSO (distinguibili con attenzione):
  target-lab.net   (TLD diverso)
  targt-lab.com    (carattere mancante)
```

### Remediation

- **Azione immediata:** registrazione preventiva dei domini a rischio alto (omoglifi con distanza visiva minima)
- **Azione strutturale:** monitoraggio continuo con dnstwist schedulato (cron settimanale); registrazione difensiva dei TLD principali (.com, .net, .org, .it) per le variazioni piu ovvie; configurazione alert su Certificate Transparency logs (crt.sh) per nuovi certificati emessi per domini simili
- **Verifica:** riesecuzione di dnstwist - i domini critici devono risultare sotto il controllo dell'organizzazione

---

## Esperienza di Laboratorio

L'esecuzione di dnstwist sul dominio di test ha generato oltre 40 variazioni in pochi secondi. La sorpresa principale e stata la quantita di domini omoglifi che risultano visivamente identici al dominio originale: la sostituzione `l` (elle minuscola) con `1` (uno) e praticamente invisibile nei font sans-serif utilizzati dalla maggior parte dei client email e browser.

Un aspetto critico: dnstwist con il flag `--all` include anche gli omoglifi Unicode (IDN homograph attack), come la sostituzione della lettera latina "a" con la lettera cirillica "a" (U+0430). Questi domini sono tecnicamente diversi ma visivamente identici. I browser moderni mitigano parzialmente questo attacco mostrando l'URL in formato Punycode (xn--...) quando rilevano script mixing, ma non tutti i client email implementano questa protezione.

---

## Analisi Teorica: Tassonomia degli Attacchi di Dominio

Il typosquatting sfrutta la limitata capacita umana di processare visivamente stringhe alfanumeriche lunghe. La ricerca di Verizon (DBIR 2024) mostra che il tempo medio di analisi di un URL prima del click e inferiore a 2 secondi - insufficiente per identificare una sostituzione di carattere singola.

Le categorie principali di permutazione sono:
- **Omoglifi:** caratteri visivamente identici (`l`/`1`, `O`/`0`, `rn`/`m`). I piu pericolosi.
- **Typo da tastiera:** errori basati sulla prossimita dei tasti (QWERTY/QWERTZ).
- **Bitsquatting:** variazioni causate da bit-flip hardware nella risoluzione DNS. Raro ma documentato in ricerca accademica (Dinaburg, 2011).
- **IDN Homograph:** utilizzo di caratteri Unicode visivamente identici da script diversi. Parzialmente mitigato dai browser ma non dai client email.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | Analisi DNS dei domini typosquatting generati (SE-012) |
| Resource Development | Acquire Infrastructure: Domains | `T1583.001` | Identificazione domini confondibili non registrati per potenziale acquisto |
| Resource Development | Compromise Infrastructure: Domains | `T1584.001` | Valutazione domini typosquatting gia registrati da terzi (parked) |

---

> **Nota:** L'analisi e stata condotta su un dominio di test. Nessun dominio typosquatting e stato registrato. Le tecniche sono documentate a scopo difensivo (monitoring e registrazione preventiva).
