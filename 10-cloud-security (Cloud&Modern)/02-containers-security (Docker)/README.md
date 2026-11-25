> [English](README.en.md) | **Italiano**

# 02 - Containers security (Docker)

> - **Fase:** Cloud Security - Container Security
> - **Categoria:** Difensivo + Offensivo - supply chain e isolamento
> - **Prerequisiti:** Docker; immagini da analizzare; per l'offensivo, accesso a un container mal configurato
> - **Output:** Finding CLOUD-005..006; sicurezza delle immagini (build) e del runtime (isolamento)

---

## Introduzione

Il "Modern" nel nome del modulo si riferisce prima di tutto a questo: i container hanno cambiato il modo di distribuire ed eseguire il software. Un container impacchetta un'applicazione con tutte le sue dipendenze in un artefatto portabile, leggero e riproducibile. Ma questa comodita introduce due superfici di sicurezza nuove: cosa c'e dentro l'immagine (la supply chain) e quanto e isolato il container in esecuzione (il runtime).

La differenza fondamentale rispetto alle macchine virtuali definisce tutta la sicurezza dei container: un container non e isolato da un hypervisor ma condivide il kernel dell'host, protetto solo da meccanismi del kernel (namespace, cgroup, capability). L'isolamento non e una barriera fisica ma una configurazione - efficace se corretta, fragile se no.

La sezione copre le due superfici:

1. **Image Scanning (CLOUD-005):** la sicurezza della build. Un'immagine eredita le vulnerabilita di tutti i suoi layer (OS di base, librerie, dipendenze); Trivy le scansiona prima del deploy. E un controllo di supply chain, da integrare in CI/CD (shift-left).

2. **Runtime Security (CLOUD-006):** la sicurezza dell'esecuzione. Le misconfigurazioni (socket Docker montato, `--privileged`, capability eccessive) permettono il container escape - l'evasione verso l'host, che annulla l'isolamento.

I due finding coprono il ciclo di vita: la scansione previene le vulnerabilita note prima del deploy, la runtime security impedisce (e rileva) l'evasione durante l'esecuzione. Insieme rispondono alle due domande della sicurezza dei container: "cosa c'e dentro?" e "quanto e contenuto?".

---

## Struttura della cartella

```
02-containers-security (Docker)/
+-- README.md              # questo file: registro CLOUD-005..006
|
+-- image-scanning/        # CLOUD-005: scansione CVE delle immagini (Trivy) - build
+-- runtime-security/      # CLOUD-006: container escape techniques - runtime
```

---

## Flusso operativo consigliato

```
[BUILD] Immagine costruita
         |
         v
[1] Image Scanning (image-scanning/)
     +-- Trivy -> CVE nei layer -> blocco deploy se critici (CLOUD-005)
              |
              v
[DEPLOY] Container in esecuzione
         |
         v
[2] Runtime Security (runtime-security/)
     +-- config a minimo privilegio (no socket, no privileged, non-root)
     +-- Falco -> detection dell'escape a runtime (CLOUD-006)
              |
              v
[OUTPUT] Container sicuro dalla build al runtime; escape prevenuto e rilevato
```

---

## Tool di riferimento

| tool | fase | tipo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Trivy` | build | difensivo | scansione cve di immagini (standard) |
| `Dive` | build | analisi | ispezione dei layer |
| `Falco` | runtime | difensivo | detection a runtime degli escape |
| `deepce` | runtime | offensivo | enumerazione delle vie di escape |
| `seccomp`/`AppArmor` | runtime | difensivo | restrizione delle syscall/capability |

> **Tool moderno consigliato:** `Trivy` per la build (supply chain), `Falco` per il runtime (detection escape). La combinazione copre entrambe le superfici. Vedere `../Tooling/` per gli scanner cloud piu ampi.

---

## Registro finding - containers security

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `CLOUD-005` | image scanning: vulnerabilita note (cve) nelle immagini prima del deploy | `Medio` | `image-scanning/` |
| `CLOUD-006` | container escape via docker socket: evasione e root sull'host | `Critico` | `runtime-security/` |

---

## Mappatura MITRE ATT&CK - aggregata

| tattica | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| initial access | supply chain compromise | `T1195` | CLOUD-005 |
| privilege escalation | escape to host | `T1611` | CLOUD-006 |
| execution | deploy container | `T1610` | CLOUD-006 |
| discovery | container and resource discovery | `T1613` | CLOUD-006 |

---

> **Nota:** Tutte le attivita documentate sono state condotte su host e container di laboratorio di proprieta dell'autore. Il container escape su infrastrutture di terzi senza autorizzazione costituisce reato. L'image scanning e un controllo difensivo non intrusivo. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
