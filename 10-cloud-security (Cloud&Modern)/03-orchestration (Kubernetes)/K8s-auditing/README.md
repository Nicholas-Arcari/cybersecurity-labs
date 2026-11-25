> [English](README.en.md) | **Italiano**

# Kubernetes auditing - CIS benchmark e pod security

> - **Fase:** Cloud Security - Kubernetes Hardening (Defense)
> - **Categoria:** Difensivo - audit di conformita e hardening del cluster
> - **Prerequisiti:** Accesso al cluster (nodi/control plane) per l'audit; kube-bench; conoscenza dei Pod Security Standards
> - **Output:** Finding CLOUD-008; report di conformita CIS; hardening del cluster; chiusura delle esposizioni sfruttate in `../K8s-attacks/`

- **Ambiente Operativo:** Cluster Kubernetes di laboratorio dell'autore, kube-bench
- **Tool principali:** kube-bench, Pod Security Standards/Admission, kubectl

---

## Executive summary

L'auditing di Kubernetes e la contromisura difensiva diretta agli attacchi documentati in `../K8s-attacks/` (CLOUD-007). Dato che la sicurezza di un cluster e la somma di molte configurazioni corrette, e che la complessita rende l'errore probabile, serve un modo sistematico per verificare la postura di sicurezza - non a mano, ma contro una baseline riconosciuta. Il **CIS Kubernetes Benchmark** e questa baseline, e **kube-bench** e lo strumento che misura la conformita del cluster ad essa.

Il finding CLOUD-008 documenta il ciclo di audit e hardening: kube-bench esegue centinaia di controlli su control plane, nodi, etcd e policy, confrontandoli con il CIS Benchmark e producendo un report di PASS/FAIL/WARN con le raccomandazioni di correzione. E l'equivalente Kubernetes di Lynis per Linux (`../../../08-defense-hardenings/04-hardening-scripts/linux-hardening/`): rende l'hardening del cluster oggettivo, misurabile e ripetibile.

Il secondo pilastro sono i **Pod Security Standards** (e la Pod Security Admission che li applica): policy che impediscono il deploy di pod pericolosi (privilegiati, con host mount, con capability eccessive) - esattamente i pod che un attaccante userebbe per l'escape (CLOUD-006) o per l'escalation. L'audit trova le debolezze, i Pod Security Standards le prevengono a livello di ammissione.

---

## Struttura della cartella

```
K8s-auditing/
+-- README.md      # questo file: audit CIS (kube-bench) + Pod Security (CLOUD-008)
+-- img/           # report kube-bench e policy
```

---

## Audit CIS con kube-bench

**ID Finding:** `CLOUD-008` | **Severity:** `Alto` (hardening del cluster; chiude le esposizioni del control plane e previene i pod pericolosi sfruttati in CLOUD-006/007)

### Contesto operativo

kube-bench esegue i controlli del CIS Kubernetes Benchmark contro i componenti del cluster: verifica i permessi dei file di configurazione, i flag dell'API server, la sicurezza di etcd, le policy RBAC. Il report indica cosa e conforme e cosa no, con la raccomandazione di correzione per ogni FAIL.

### PoC - esecuzione dell'audit CIS

```Bash
# kube-bench esegue i controlli CIS sul cluster (control plane + nodi)
kube-bench run --targets master,node,etcd,policies
```

```
[INFO] 1 Master Node Security Configuration
[PASS] 1.2.1 Ensure --anonymous-auth is set to false
[FAIL] 1.2.16 Ensure --encryption-provider-config is set     <-- Secret non cifrati (CLOUD-008)
[FAIL] 2.1 Ensure etcd is configured with client cert auth   <-- etcd senza auth (CLOUD-008)
[WARN] 5.2.1 Minimize privileged containers (PodSecurity)

== Summary == 42 checks PASS, 8 FAIL, 11 WARN
```

Ogni FAIL corrisponde a un'esposizione sfruttabile: la 1.2.16 (Secret non cifrati) e la 2.1 (etcd senza auth) sono esattamente i vettori di CLOUD-007. L'audit li rende visibili prima dell'attaccante.

### PoC - pod security standards (prevenzione dei pod pericolosi)

```YAML
# Pod Security Admission: blocca i pod privilegiati/host-mount a livello di namespace
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted   # <-- policy "restricted"
```

```Bash
# Tentativo di deploy di un pod privilegiato -> rifiutato dall'admission
kubectl apply -f privileged-pod.yaml
```

```
Error: pods "evil" is forbidden: violates PodSecurity "restricted:latest":
  privileged (container must not set securityContext.privileged=true)   <-- escape prevenuto (CLOUD-008)
```

### Operativita difensiva

- **Ciclo audit, hardening, ri-audit:** eseguire kube-bench, correggere i FAIL prioritari (etcd, cifratura Secret, anonymous auth), ri-eseguire per confermare
- **Correzioni prioritarie:** cifratura dei Secret a riposo, TLS mutuo su etcd, disabilitazione accesso anonimo, RBAC a minimo privilegio
- **Pod Security Standards:** applicare la policy `restricted` ai namespace applicativi per bloccare pod privilegiati, host mount e capability eccessive (previene CLOUD-006)
- **Automazione:** integrare kube-bench in CI/CD e nell'audit periodico; abbinare policy engine come OPA/Gatekeeper o Kyverno per policy custom oltre i Pod Security Standards

---

## Esperienza di laboratorio

Il valore di kube-bench e stato tradurre la vastita di Kubernetes in una checklist azionabile. Dopo aver visto in `../K8s-attacks/` quanto sia ampia la superficie del cluster, l'idea di verificarla a mano era scoraggiante; kube-bench l'ha ridotta a un report di PASS/FAIL con le correzioni. Vedere i FAIL corrispondere esattamente ai vettori che avevo sfruttato dal lato offensivo (etcd senza auth, Secret non cifrati) ha reso concreta la simmetria: lo stesso cluster che avevo attaccato, ora lo hardenizzavo chiudendo i FAIL uno per uno.

I Pod Security Standards sono stati la scoperta piu potente sul piano preventivo. Nel modulo dei container avevo usato pod privilegiati per l'escape; qui, con la policy `restricted` applicata al namespace, il deploy di un pod privilegiato veniva semplicemente rifiutato all'ammissione. La differenza tra rilevare un pod pericoloso dopo (detection) e impedirne il deploy prima (admission control) e la differenza tra difesa reattiva e preventiva. Bloccare la classe intera di pod pericolosi a monte e piu robusto che inseguire i singoli.

La riflessione e stata sulla necessita dell'automazione. Un cluster reale cambia continuamente - nuovi deploy, nuove configurazioni - e la postura di sicurezza deriva ad ogni modifica. Un audit una tantum non basta; serve kube-bench in CI/CD e policy di ammissione che impongano i vincoli a ogni deploy. La sicurezza di Kubernetes non e uno stato che si raggiunge ma un vincolo che si mantiene, e mantenerlo richiede automazione.

---

## Analisi teorica: baseline e admission control come difesa scalabile

L'auditing con baseline (CIS) risolve il problema della complessita con lo stesso principio dell'hardening tradizionale (Lynis, CIS Benchmark del modulo 08): trasformare "e sicuro?" - domanda soggettiva e ingestibile su un sistema complesso - in "e conforme a questa baseline riconosciuta?" - domanda oggettiva e verificabile. La baseline incapsula la conoscenza di sicurezza condivisa in una checklist, rendendo l'hardening ripetibile e indipendente dall'esperto. Non serve sapere a memoria ogni configurazione sicura di Kubernetes; serve verificare la conformita al CIS.

L'admission control (Pod Security Standards) introduce un secondo principio: prevenire alla porta invece di rilevare dopo. Un pod pericoloso puo essere rilevato dopo il deploy (detection, reattivo) o rifiutato prima (admission, preventivo). L'admission control e strutturalmente superiore perche agisce sul flusso di creazione: nessun pod che violi la policy entra nel cluster, a prescindere da chi lo deploya. Sposta la sicurezza dal monitorare cosa succede al vincolare cosa puo succedere, ed e questo il modello scalabile per un sistema dove i deploy sono continui e automatizzati.

Insieme, audit e admission coprono i due tempi della difesa: l'audit verifica lo stato esistente (cosa e configurato male ora), l'admission vincola le modifiche future (cosa non potra essere deployato). In un sistema dinamico come Kubernetes, servono entrambi - correggere il presente e vincolare il futuro - perche la sicurezza non e una fotografia ma un film, e va difesa in ogni fotogramma.

---

## Scenario reale: L'Hardening in azione

> Prospettiva difensiva: come l'audit e l'admission control avrebbero contrastato l'attacco di CLOUD-007.

```
[CLOUD-008] kube-bench + Pod Security Standards applicati
        |
        v
Attaccante scansiona il cluster (kube-hunter) -> accesso anonimo DISABILITATO
        |                                       -> etcd con TLS mutuo, non esposto
        v
FAIL corretti dall'audit: i vettori di CLOUD-007 sono chiusi a monte
        |
        v
Attaccante compromette un pod -> tenta il deploy di un pod privilegiato per l'escape
        |
        v
Pod Security "restricted" RIFIUTA il pod privilegiato -> escape (CLOUD-006) prevenuto
        |
        v
Attacco contenuto: nessuna via al control plane, nessun escape possibile
```

**Valore difensivo:** l'audit chiude le esposizioni del control plane (i vettori di CLOUD-007) e i Pod Security Standards prevengono i pod pericolosi (il vettore di CLOUD-006). La difesa e in profondita: anche se l'attaccante compromette un workload, non trova ne un control plane esposto ne la possibilita di deployare pod per l'escape.

**Lezione difensiva:** la difesa di Kubernetes si costruisce prima dell'attacco, nella conformita alla baseline e nelle policy di ammissione. L'audit trova cio che e gia sbagliato; l'admission control impedisce che si sbagli in futuro. E la stessa filosofia dell'hardening del modulo 08, applicata alla complessita del cluster: rendere l'insicurezza difficile, non solo rilevabile.

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `kube-bench` | cis auditor | difensivo | verifica di conformita al cis kubernetes benchmark |
| `Pod Security Admission` | admission control | difensivo | blocco dei pod pericolosi a livello di namespace |
| `OPA/Gatekeeper` | policy engine | difensivo | policy custom di ammissione (oltre i pod security standards) |
| `Kyverno` | policy engine | difensivo | policy k8s-native, alternativa a opa |
| `kubescape` | security scanner | difensivo | audit basato su framework (nsa/mitre) |

> **Tool moderno consigliato:** `kube-bench` per l'audit CIS, i `Pod Security Standards` nativi come prima linea di admission control, e `Kyverno`/`OPA-Gatekeeper` per le policy custom. `kubescape` per un audit basato sui framework NSA/MITRE. La combinazione audit + admission copre stato presente e modifiche future.

---

## Mappatura MITRE ATT&CK

> Tecniche d'attacco **prevenute** dall'hardening del cluster.

| tattica (prevenuta) | tecnica | id mitre | ruolo del controllo |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | chiusura delle esposizioni del control plane (CLOUD-008) |
| privilege escalation | escape to host | `T1611` | pod security blocca i pod privilegiati (previene CLOUD-006) |
| credential access | unsecured credentials: container api | `T1552.007` | cifratura secret + auth etcd (previene CLOUD-007) |
| execution | deploy container | `T1610` | admission control sui pod deployabili |

| contromisura difensiva (d3fend) | id d3fend | applicazione |
| :--- | :--- | :--- |
| platform hardening | `D3-PH` | conformita al cis kubernetes benchmark |
| mandatory access control | `D3-MAC` | pod security standards / policy di ammissione |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un cluster Kubernetes di laboratorio di proprieta dell'autore. L'auditing e un controllo difensivo non intrusivo. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
