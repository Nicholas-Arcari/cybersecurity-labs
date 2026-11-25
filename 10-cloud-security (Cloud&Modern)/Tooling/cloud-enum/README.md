> [English](README.en.md) | **Italiano**

# Cloud_enum - recon di asset cloud

> - **Fase:** Cloud Security - Reconnaissance (multi-cloud)
> - **Categoria:** Recon - scoperta di asset esposti
> - **Prerequisiti:** Un nome/keyword del target (azienda, progetto); cloud_enum (Python)
> - **Output:** Elenco di asset cloud pubblici associati al target (bucket, storage, servizi)

- **Tool principale:** cloud_enum (multi-cloud OSINT)

---

## Cos'e e a cosa serve

`cloud_enum` e uno strumento di ricognizione OSINT per il cloud: data una keyword (tipicamente il nome dell'azienda o del progetto), genera permutazioni plausibili e verifica quali asset cloud pubblici esistono e sono accessibili, attraverso i tre provider maggiori. E il punto di partenza di un assessment cloud dall'esterno: mappare cosa il target espone senza autenticazione.

Sfrutta il fatto che gli asset cloud hanno nomi globali e spesso prevedibili (`azienda-backup`, `azienda-assets`, `azienda-prod`). Testando le permutazioni di una keyword, scopre bucket S3, Azure Blob storage, Google Storage, e altri servizi che il target ha esposto - spesso senza saperlo.

---

## Utilizzo

```Bash
# Ricognizione multi-cloud a partire da una keyword
python3 cloud_enum.py -k nomeazienda -k nomeazienda-prod
```

```
[+] AWS S3 Bucket FOUND:   nomeazienda-backup.s3.amazonaws.com   (OPEN)   <-- accessibile
[+] Azure Blob FOUND:      nomeazienda.blob.core.windows.net
[+] GCP Storage FOUND:     nomeazienda-assets  (public)
[!] 3 asset pubblici scoperti per la keyword 'nomeazienda'
```

---

## Quando usarlo nel flusso

- **Primo passo di un assessment cloud esterno:** prima di avere credenziali, mappare la superficie pubblica del target
- **Input per gli attacchi mirati:** i bucket scoperti alimentano gli attacchi S3 (`../../01-providers-infrastructure (IaaS & PaaS)/AWS (Amazon Web Services)/S3-buckets-attacks/`)
- **Verifica difensiva:** un'organizzazione puo eseguirlo su se stessa per scoprire cosa espone inavvertitamente (shadow IT, asset dimenticati)

---

## Tool correlati

| tool | ruolo | relazione |
| :--- | :--- | :--- |
| `cloud_enum` | recon multi-cloud | questo strumento |
| `s3scanner` | s3 enum | focalizzato sui bucket aws |
| `Prowler` / `ScoutSuite` | audit difensivo | trovano gli asset esposti dall'interno dell'account |

> **Tool moderno consigliato:** `cloud_enum` per il recon multi-cloud esterno. Dal lato difensivo, l'audit dall'interno dell'account (`Prowler`/`ScoutSuite`) e piu completo perche vede tutti gli asset, non solo quelli con nome indovinabile.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione |
| :--- | :--- | :--- | :--- |
| reconnaissance | search open websites/domains | `T1593` | scoperta di asset cloud pubblici via permutazione dei nomi |
| discovery | cloud infrastructure discovery | `T1580` | enumerazione degli asset cloud esposti |

---

> **Nota:** cloud_enum va usato per il recon di asset di proprieta dell'autore o con autorizzazione esplicita. L'enumerazione mirata di asset di terzi puo violare i termini dei provider. Documentato a scopo educativo e di security assessment autorizzato.
