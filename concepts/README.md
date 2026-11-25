> [English](README.en.md) | **Italiano**

# Concetti e conoscenza di base

> - **Natura:** pagine di conoscenza di base (background), non tecniche legate a una fase del penetration test.
> - **Taglio:** concettuale ed educativo, con enfasi su classificazione, funzionamento e difesa (detection/mitigazione).
> - **Scopo:** dare il contesto teorico che i moduli operativi (00-11) danno per acquisito.

## Introduzione

I moduli numerati (`00`-`11`) documentano il penetration test per fasi, con tecniche, comandi e finding. Questa
area raccoglie invece i **concetti trasversali** che quei moduli presuppongono: cosa sono le categorie di
malware, come funziona un attacco di negazione del servizio, e simili. Sono pagine da manuale, non da laboratorio:
servono a inquadrare la terminologia e il funzionamento, con attenzione al lato difensivo (come si rileva e si
mitiga), coerentemente con la doppia anima (offensiva + difensiva) del repository.

## Struttura della cartella

| sottocartella | tema | taglio |
| :--- | :--- | :--- |
| `malware-taxonomy/` | tassonomia del malware: virus, worm, trojan, rat, botnet, ransomware, rootkit, wiper, loader, spyware/keylogger | classificazione + mitre + detection |
| `ddos/` | denial of service e ddos: volumetrico, a protocollo, applicativo; amplificazione/riflessione; botnet | funzionamento + mitigazione (concettuale) |

## Nota di perimetro

Queste pagine sono **esplicative**: descrivono categorie e meccanismi e come difendersi. Non contengono
malware funzionante ne strumenti di attacco DoS pronti all'uso; dove utile rimandano ai moduli operativi del
repository (es. [07-post-exploitation](<../07-post-exploitation/README.md>) per il credential dumping,
[08-defense-hardenings](<../08-defense-hardenings (Blue Team Prevention)/README.md>) per detection e difesa).

---

> **Nota:** Contenuto didattico e di conoscenza di base. Nessun payload offensivo: sono pagine concettuali.
