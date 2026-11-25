> [English](README.en.md) | **Italiano**

# ScoutSuite - audit Multi-Cloud della configurazione

> - **Fase:** Cloud Security - Multi-Cloud Audit (Defense)
> - **Categoria:** Difensivo - vista d'insieme della postura di sicurezza
> - **Prerequisiti:** Credenziali di sola lettura/audit sull'ambiente; ScoutSuite (NCC Group)
> - **Output:** Report HTML navigabile della postura di sicurezza multi-cloud

- **Tool principale:** ScoutSuite (NCC Group, multi-cloud)

---

## Cos'e e a cosa serve

`ScoutSuite` e uno strumento di audit multi-cloud che produce una vista d'insieme navigabile della postura di sicurezza di un ambiente. Raccoglie la configurazione attraverso le API del provider (AWS, Azure, GCP, e altri) e genera un report HTML che evidenzia le misconfigurazioni per servizio, con un colpo d'occhio su cosa e a rischio.

La sua forza e la panoramica. Dove Prowler (`../prowler/`) eccelle nella profondita e nella mappatura di compliance, ScoutSuite eccelle nel dare rapidamente il quadro complessivo: quali servizi hanno problemi, dove si concentrano i rischi, come e configurato l'ambiente nel suo insieme. E spesso il primo strumento da lanciare in un audit cloud per orientarsi, prima di approfondire con Prowler.

---

## Utilizzo

```Bash
# Audit di un ambiente AWS (genera un report HTML navigabile)
scout aws
```

```
[+] Raccolta della configurazione via API...
[+] Analisi di 40+ servizi (IAM, S3, EC2, RDS, ...)
[+] Report generato: scoutsuite-report/aws-<account>.html

Dashboard: 12 findings Danger, 34 Warning
  IAM      -> 4 Danger (policy permissive, root senza MFA)
  S3       -> 3 Danger (bucket pubblici)                    <-- correlato CLOUD-002
  Security Groups -> 5 Danger (porte aperte a 0.0.0.0/0)
```

```Bash
# ScoutSuite supporta piu provider
scout azure
scout gcp
```

---

## Quando usarlo nel flusso

- **Primo audit di orientamento:** per capire rapidamente dove sono i rischi in un ambiente sconosciuto
- **Vista multi-cloud unificata:** utile in organizzazioni che usano piu provider, per una postura complessiva
- **Complementare a Prowler:** ScoutSuite per la panoramica e la navigazione, Prowler per la profondita e la compliance formale
- **Verifica post-hardening:** rieseguirlo dopo le correzioni per confermare la riduzione dei findings

---

## Tool correlati

| tool | ruolo | relazione |
| :--- | :--- | :--- |
| `ScoutSuite` | audit multi-cloud | questo strumento (difensivo) |
| `Prowler` | audit/compliance | complementare: profondita vs panoramica (`../prowler/`) |
| `Pacu` / `AzureHound` | exploitation | le controparti offensive |
| `PMapper` | iam graph | analisi mirata delle vie di privesc iam |

> **Tool moderno consigliato:** usare `ScoutSuite` per la vista d'insieme rapida e `Prowler` per l'audit approfondito e la compliance. In un ambiente multi-cloud, ScoutSuite offre una postura unificata; per provider specifici, gli strumenti nativi (Security Hub AWS, Defender for Cloud Azure) completano il quadro.

---

## Mappatura MITRE ATT&CK

| tattica (prevenuta) | tecnica | id mitre | ruolo del controllo |
| :--- | :--- | :--- | :--- |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | rileva le configurazioni iam a rischio |
| collection | data from cloud storage | `T1530` | rileva i bucket/storage esposti |
| initial access | exploit public-facing application | `T1190` | rileva i security group troppo aperti |

| contromisura difensiva (d3fend) | id d3fend | applicazione |
| :--- | :--- | :--- |
| configuration inventory | `D3-CI` | inventario navigabile della configurazione multi-cloud |
| platform hardening | `D3-PH` | identificazione delle misconfig da correggere |

---

> **Nota:** ScoutSuite e un tool difensivo non intrusivo, da eseguire su ambienti di proprieta o con autorizzazione. Documentato a scopo educativo e di difesa in contesto autorizzato.
