> [English](README.en.md) | **Italiano**

# Denial of Service (DoS) e DDoS

> - **Natura:** pagina concettuale (conoscenza di base). Taglio funzionamento + difesa. Nessuno strumento di attacco DoS.
> - **Obiettivo:** spiegare cos'e un attacco di negazione del servizio, le sue categorie, il meccanismo di amplificazione/riflessione e soprattutto come si rileva e si mitiga.
> - **Perimetro:** il DoS e fuori dallo scope di un penetration test (e disruptivo); qui e trattato come conoscenza difensiva e di contesto, non come tecnica da eseguire.

## Introduzione

Un attacco **DoS** (Denial of Service) mira a rendere un servizio indisponibile ai suoi utenti legittimi,
esaurendone una risorsa (banda, CPU, memoria, stato delle connessioni, capacita applicativa). Quando l'attacco
proviene da molte sorgenti coordinate (tipicamente una **botnet**), si parla di **DDoS** (Distributed DoS): la
distribuzione rende difficile bloccare l'origine e moltiplica il volume.

A differenza della maggior parte delle tecniche documentate nel repository, il DoS non punta a ottenere accesso
o dati: punta all'**impatto sulla disponibilita** (la "A" della triade CIA). Per questo in un ingaggio di
penetration test e normalmente **escluso** dallo scope: si documenta la postura difensiva, non si esegue
l'attacco.

## Categorie

| Categoria | Risorsa esaurita | Esempi di meccanismo | Metrica |
| :--- | :--- | :--- | :--- |
| **Volumetrico** | Banda di rete | Flood UDP/ICMP, amplificazione/riflessione | Gbps / Tbps |
| **A protocollo (state exhaustion)** | Stato/tabelle di connessione (firewall, LB, server) | SYN flood, ACK flood, frammentazione | pps (packet/s) |
| **Applicativo (Layer 7)** | Capacita dell'applicazione (CPU, thread, DB) | HTTP flood, richieste costose, Slowloris (connessioni lente tenute aperte) | rps (request/s) |

Gli attacchi applicativi sono i piu insidiosi: bassi volumi (difficili da distinguere dal traffico legittimo)
ma ad alto costo per il server (es. una ricerca pesante ripetuta).

## Amplificazione e riflessione (concetto)

La tecnica che genera i volumi piu alti sfrutta servizi UDP pubblici mal configurati come **amplificatori**:

```
Attaccante (IP vittima falsificato) --richiesta piccola--> Server UDP pubblico (DNS/NTP/memcached)
Server pubblico --risposta grande--> Vittima (perche l'IP sorgente era falsificato)
```

- **Spoofing dell'IP sorgente**: l'attaccante mette l'IP della vittima come mittente; la risposta va alla vittima.
- **Fattore di amplificazione**: il rapporto risposta/richiesta. DNS ~ x50, NTP (monlist) ~ x500, **memcached**
  fino a ~ x50.000. L'attacco GitHub del 2018 (1.35 Tbps) sfrutto proprio memcached esposto.

La radice del problema e duplice: servizi UDP esposti che rispondono a chiunque, e reti che **non filtrano lo
spoofing** in uscita (mancata adozione di BCP38/ingress filtering).

## Relazione con le botnet

Il DDoS volumetrico moderno e alimentato da **botnet**: migliaia di dispositivi compromessi (spesso IoT con
credenziali deboli, vedi [tassonomia malware](<../malware-taxonomy/README.md>)) che inviano traffico al comando
del C2. **Mirai** (2016) ne e l'esempio: compromise di massa di telecamere/router IoT, usati per attacchi oltre
il Tbps (Dyn, OVH, Krebs).

## Rilevamento e mitigazione (Blue Team)

**Rilevamento.**
- Picchi anomali di traffico in ingresso (Gbps/pps) o di richieste L7 (rps) rispetto alla baseline.
- Molte sorgenti che generano richieste simili; distribuzione geografica anomala; user-agent/pattern ripetitivi.
- NetFlow/sFlow per individuare rapidamente il tipo (volumetrico vs protocollo vs L7).

**Mitigazione.**
- **A monte (upstream/provider)**: scrubbing center, servizi anti-DDoS (assorbono il volume prima che raggiunga
  l'origine); blackholing/RTBH come ultima risorsa.
- **Architettura**: **anycast** (distribuisce il carico su piu PoP), CDN (assorbe e cache), sovradimensionamento.
- **A protocollo**: SYN cookies, limiti sullo stato delle connessioni, rate limiting per IP.
- **Applicativo (L7)**: WAF, rate limiting, CAPTCHA/challenge, caching delle risposte costose.
- **Contro l'amplificazione**: non esporre servizi UDP non necessari; disabilitare `monlist` (NTP); adottare
  **BCP38** (ingress filtering) per impedire lo spoofing in uscita dalla propria rete.

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE |
| :--- | :--- | :--- |
| Impact | Network Denial of Service | `T1498` |
| Impact | Network Denial of Service: Direct Network Flood | `T1498.001` |
| Impact | Network Denial of Service: Reflection Amplification | `T1498.002` |
| Impact | Endpoint Denial of Service | `T1499` |
| Impact | Endpoint Denial of Service: Application Exhaustion / Service Exhaustion Flood | `T1499.003` / `T1499.002` |

## Riferimenti

- MITRE ATT&CK, tattica Impact (`T1498`, `T1499`).
- BCP38 / RFC 2827 (Network Ingress Filtering) contro lo spoofing dell'IP sorgente.
- Casi storici: Mirai (2016, botnet IoT); GitHub (2018, amplificazione memcached, 1.35 Tbps).

---

## Correlazioni con i moduli operativi

| Concetto | Modulo correlato | Collegamento |
| :--- | :--- | :--- |
| Botnet come sorgente del DDoS | [tassonomia malware](<../malware-taxonomy/README.md>) | i bot (spesso IoT) sono il motore del volume |
| Rilevamento e mitigazione | [08-defense-hardenings](<../../08-defense-hardenings (Blue Team Prevention)/README.md>) | monitoraggio del traffico, rate limiting, hardening di rete |
| Filtri anti-spoofing (BCP38) | Networking / configurazione dei router di bordo | riducono alla radice la superficie di amplificazione (non specifici di un modulo) |

---

> **Nota:** Contenuto didattico e concettuale, orientato alla difesa. Non contiene strumenti ne procedure per eseguire un attacco DoS/DDoS.
