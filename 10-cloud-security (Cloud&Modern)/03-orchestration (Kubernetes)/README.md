> [English](README.en.md) | **Italiano**

# 03 - Orchestration (Kubernetes)

> - **Fase:** Cloud Security - Kubernetes (Orchestration)
> - **Categoria:** Offensivo + Difensivo - il sistema operativo del cloud
> - **Prerequisiti:** Cluster K8s di test; kubectl; per l'offensivo, cluster esposto o accesso iniziale; per il difensivo, accesso in audit
> - **Output:** Finding CLOUD-007..008; comprensione della superficie d'attacco del cluster e delle contromisure

---

## Introduzione

Kubernetes e il sistema operativo del cloud moderno: orchestra migliaia di container su cluster di nodi, gestendo deployment, rete, storage e segreti. Questa centralita ne fa un bersaglio ad altissimo valore - compromettere il cluster significa controllare tutti i workload che vi girano - e una superficie d'attacco vasta e complessa, dove la sicurezza e la somma di molte configurazioni corrette e basta un componente esposto per compromettere l'insieme.

La sezione affronta Kubernetes dalle due prospettive complementari:

1. **K8s Attacks (CLOUD-007):** l'offensiva. Sfruttamento di cluster esposti e mal configurati - API server con accesso anonimo, etcd non autenticato (che contiene i Secret in chiaro), kubelet aperto, service account sovraprivilegiati. kube-hunter per la ricognizione.

2. **K8s Auditing (CLOUD-008):** la difesa. Audit di conformita al CIS Benchmark con kube-bench e prevenzione dei pod pericolosi con i Pod Security Standards. Chiude le esposizioni che l'offensiva sfrutta.

Il tema trasversale e la gestione della complessita. Kubernetes ha troppi componenti e configurazioni perche la sicurezza possa essere verificata a mano; serve l'audit sistematico contro una baseline (kube-bench/CIS) e l'admission control che vincola i deploy futuri (Pod Security Standards). La simmetria offensivo/difensivo e forte: kube-hunter trova cio che kube-bench aiuta a correggere.

---

## Struttura della cartella

```
03-orchestration (Kubernetes)/
+-- README.md          # questo file: registro CLOUD-007..008
|
+-- K8s-attacks/       # CLOUD-007: cluster esposti/mal configurati (kube-hunter, etcd)
+-- K8s-auditing/      # CLOUD-008: audit CIS (kube-bench) + Pod Security Standards
```

---

## Flusso operativo consigliato

```
[OFFENSIVO] K8s-attacks/
     +-- kube-hunter -> API/etcd/kubelet esposti -> furto Secret / controllo cluster (CLOUD-007)
              |
              v
[DIFENSIVO] K8s-auditing/
     +-- kube-bench (CIS) -> chiude le esposizioni del control plane (CLOUD-008)
     +-- Pod Security Standards -> previene i pod pericolosi (escape)
              |
              v
[OUTPUT] Cluster hardenizzato: control plane protetto, escape e escalation prevenuti
```

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `kubectl` | k8s cli | ufficiale | interazione con il cluster |
| `kube-hunter` | scanner | offensivo | scoperta di componenti esposti |
| `Peirates` | exploitation | offensivo | post-exploitation su k8s |
| `kube-bench` | cis auditor | difensivo | audit di conformita cis |
| `Pod Security` / `Kyverno` | admission | difensivo | blocco dei pod pericolosi |
| `Falco` | runtime security | difensivo | detection a runtime |

> **Tool moderno consigliato:** `kube-hunter`/`Peirates` (offensivo) e `kube-bench` + Pod Security Standards + `Falco` (difensivo). Vedere `../Tooling/` per gli scanner cloud trasversali.

---

## Registro finding - orchestration (Kubernetes)

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `CLOUD-007` | k8s cluster esposto/mal configurato: furto secret e controllo del control plane | `Critico` | `K8s-attacks/` |
| `CLOUD-008` | k8s auditing: cis benchmark (kube-bench) + pod security standards (hardening) | `Alto` | `K8s-auditing/` |

---

## Mappatura MITRE ATT&CK - aggregata

> Riferimento: MITRE ATT&CK for Containers.

| tattica | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | CLOUD-007, CLOUD-008 |
| credential access | unsecured credentials: container api | `T1552.007` | CLOUD-007, CLOUD-008 |
| privilege escalation | escape to host | `T1611` | CLOUD-008 (prevenzione) |
| execution | deploy container | `T1610` | CLOUD-007, CLOUD-008 |
| discovery | container and resource discovery | `T1613` | CLOUD-007 |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un cluster Kubernetes di laboratorio di proprieta dell'autore. L'accesso non autorizzato a cluster di terzi costituisce reato. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
