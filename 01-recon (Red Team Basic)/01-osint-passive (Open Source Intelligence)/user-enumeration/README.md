# OSINT Passive: User Enumeration & Identity Correlation

> - **Fase:** Reconnaissance - Passive Information Gathering
> - **Visibilita:** Zero - il tool invia richieste HTTP a piattaforme pubbliche, non al target direttamente
> - **Prerequisiti:** Username target noto, Sherlock installato (pip o apt), Python 3
> - **Output:** OSINT-004 - Mappa della presenza digitale del target su piattaforme social e tecniche, utile per profilazione e Social Engineering

---

Obiettivo: Effettuare la correlazione dell'identità digitale (Identity Correlation) partendo da un singolo username noto per mappare la presenza del target su piattaforme diverse.

Strumenti: `Sherlock`

---

## 1 Introduzione Teorica

La User Enumeration passiva sfrutta la tendenza degli utenti a riutilizzare lo stesso handle (nome utente) su molteplici servizi.
Attraverso strumenti automatizzati, è possibile interrogare centinaia di piattaforme social, forum e servizi tecnici per verificare l'esistenza di un profilo.

Utilità per il Red Team:
- Profilazione Psicologica: Capire interessi e hobby per attacchi di Ingegneria Sociale.
- Estensione della Superficie: Trovare account meno protetti (es. un vecchio forum) che potrebbero contenere leak di password o informazioni personali.

---

## 2 Esecuzione Tecnica

**ID Finding:** `OSINT-004` | **Severity:** `Basso`

### Ricerca con Sherlock
È stato utilizzato lo strumento `Sherlock` per scansionare oltre 300 siti web alla ricerca dell'username target.

```Bash
sudo apt update
sudo apt install sherlock
sherlock <USERNAME>
```

![](./img/Screenshot_2026-02-03_17_12_56.jpg)

---

## 3 Analisi dei Falsi Positivi

Durante l'analisi è fondamentale verificare manualmente i link.

Falsi Positivi: In alcuni casi (es. forum-sconosciuto.com), l'username esiste ma appartiene a un'altra persona (omonimia digitale).

Verifica: È stato controllato manualmente il profilo GitHub e Reddit per confermare che l'immagine del profilo o la bio coincidessero, validando l'attribuzione al target.

---

## 5 Conclusioni

L'impronta digitale del target è [Alta / Media / Bassa]. L'uso consistente dello stesso username permette a un attore malevolo di collegare facilmente la vita professionale (GitHub) con quella personale o ludica, aumentando l'efficacia di potenziali attacchi mirati.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Employee Names | `T1589.003` | Correlazione identita digitale tramite Sherlock per mappare la presenza dell'username target su 300+ piattaforme (OSINT-004) |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | Enumerazione account social del target (GitHub, Reddit, forum) per costruire profilo utile al Social Engineering (OSINT-004) |

---

> **Nota:** Le attivita di user enumeration documentate sono state eseguite a scopo di audit personale o su target che hanno fornito autorizzazione esplicita. La tecnica e stata eseguita all'interno di un laboratorio didattico. I risultati non sono stati usati per finalita malevole.