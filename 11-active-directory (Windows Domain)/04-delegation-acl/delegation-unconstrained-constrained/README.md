> [English](README.en.md) | **Italiano**

# Unconstrained e constrained delegation abuse

> - **Fase:** Privilege Escalation / Lateral Movement (dominio Active Directory)
> - **Visibilita:** Media - richieste Kerberos S4U (constrained) o cattura di TGT in memoria (unconstrained); la coercizione associata genera traffico RPC anomalo
> - **Prerequisiti:** controllo di un account/host configurato con delega (unconstrained o constrained verso un servizio); per l'unconstrained, tipicamente admin locale su un host con quella delega
> - **Tecnica:** `Kerberos delegation abuse` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; identificativi segnaposto.
- Obiettivo: impersonare utenti privilegiati sfruttando deleghe Kerberos mal configurate, fino alla compromissione di un DC.

---

## Executive summary

Kerberos prevede la delega perche un servizio (es. un web server) possa agire per conto dell'utente verso un
altro servizio (es. un database). Esistono due forme classiche, entrambe abusabili:

- **Unconstrained Delegation:** un host con questa delega riceve e memorizza il TGT degli utenti che vi si
  autenticano. Chi compromette quell'host puo estrarre dalla memoria i TGT di chiunque vi si connetta,
  incluso - se si induce (coerce) un DC a connettersi - il TGT dell'account macchina del DC.
- **Constrained Delegation:** un account puo richiedere, via S4U, ticket verso servizi specifici per conto di
  qualunque utente. Chi controlla quell'account puo impersonare utenti privilegiati verso quei servizi.

Entrambe trasformano il controllo di un account/host delegato in impersonazione di identita privilegiate.

## Contesto operativo (perche, prima del come)

Le deleghe sono configurazioni legittime ma pericolose: BloodHound evidenzia gli host con unconstrained
delegation e gli account con constrained delegation come bersagli ad alto valore. La decisione operativa per
l'unconstrained e combinare la compromissione dell'host con la coercizione di un account privilegiato (es.
un DC) a connettersi, per catturarne il TGT. Per la constrained, si sfrutta S4U per impersonare un utente
privilegiato verso il servizio consentito, valutando anche il "protocol transition" se configurato.

## Esecuzione / comandi

### Unconstrained: cattura del TGT + coercizione

```bash
# Monitoraggio/estrazione dei TGT in arrivo sull'host con unconstrained delegation (eseguito da admin su quell'host)
# Si induce poi un DC a connettersi all'host, per catturarne il TGT (coercizione)
Coercer coerce -l <host_unconstrained> -t <IP_domain_controller> -u utente -p 'Password123' -d corp.local
```

Output illustrativo (rappresentativo):

```
[*] Captured TGT for DC01$@CORP.LOCAL   <-- TGT dell'account macchina del DC
```

### Constrained: impersonazione via S4U

```bash
# L'account con constrained delegation richiede un TGS verso il servizio consentito impersonando un admin
getST.py -spn 'cifs/target.corp.local' -impersonate administrator \
  corp.local/'SVC$':'Password123' -dc-ip 10.10.10.10
```

## Analisi dei risultati

Nell'unconstrained, catturare il TGT di un DC equivale a poterne impersonare l'account macchina, da cui
DCSync e dominio completo: severity `Critico`. Nella constrained, l'impatto dipende dal servizio consentito,
ma l'impersonazione di un admin verso un servizio critico e comunque grave. In entrambi i casi il finding
reale va misurato in lab (quale identita si riesce a impersonare, verso quale servizio).

### Analisi teorica

L'unconstrained delegation e una scelta di design pericolosa perche l'host riceve il TGT completo
dell'utente (delega "illimitata"): e la fiducia massima, e chi compromette l'host eredita quella fiducia. La
constrained delegation limita la delega a servizi specifici (S4U2proxy), ma se combinata con "protocol
transition" (S4U2self) consente di ottenere ticket per utenti che non si sono mai autenticati. In entrambi i
casi la violazione (proprieta P3) nasce dal fatto che il controllo dell'account/host delegato concede
l'autorita di impersonazione che la delega rappresenta. La coercizione (T1187) e la leva che, nell'
unconstrained, porta il TGT giusto (quello di un DC) sull'host compromesso. Vedi
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>).

## Remediation (blue team)

**Rilevamento.** Host con unconstrained delegation che ricevono connessioni da DC in orari/contesti
inattesi; traffico di coercizione RPC; richieste S4U anomale da account con constrained delegation.

**Hardening.** Eliminare l'unconstrained delegation (sostituirla con constrained o RBCD piu limitati);
marcare gli account sensibili come "Account is sensitive and cannot be delegated" e inserirli nel gruppo
Protected Users; mitigare la coercizione; monitorare le configurazioni di delega (BloodHound lato blue team).

---

## Scenario reale: proiezione Post-Exploitation

> Nell'unconstrained con coercizione di un DC, l'esito e il dominio completo (severity Critico).

### Prospettiva attaccante (red team)

**Punto di partenza:** admin locale su un host con unconstrained delegation (o controllo di un account con
constrained delegation).

**Passo successivo immediato (unconstrained):** monitorare i TGT in arrivo e coercere un DC a connettersi.

**Kill Chain proiettata:**

```
Host con unconstrained delegation compromesso
        |
        v
Coercizione del DC a connettersi (MS-RPRN/MS-EFSRPC)
        |
        v
Cattura del TGT dell'account macchina del DC
        |
        v
Impersonazione del DC -> DCSync -> dominio completo
        |
        v
Golden Ticket / persistenza
```

**Impatto potenziale:** compromissione del dominio partendo da un singolo host mal configurato con
unconstrained delegation.

**Vettori di monetizzazione tipici:** ransomware/esfiltrazione a valle del dominio.

### Prospettiva difensore (blue team)

**Rilevamento:** connessioni di un DC verso host con unconstrained delegation; coercizione RPC; S4U anomali.

**Indicatori di Compromissione (IOC):** TGT di account macchina DC presenti su host non-DC; traffico
MS-RPRN/MS-EFSRPC verso i DC; impersonazioni S4U verso servizi sensibili.

**Contenimento:** isolamento dell'host con delega; reset dell'account macchina del DC coinvolto; indagine.

**Eradicazione e hardening:** eliminazione dell'unconstrained delegation; Protected Users e flag "non
delegabile" sugli account sensibili; mitigazione coercizione.

**Lezione difensiva:** l'unconstrained delegation concede a un host la fiducia piena degli utenti che vi si
connettono. E una configurazione da eliminare, non solo da monitorare.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Rubeus` | .net kerberos tool | cli - attivo | monitoraggio/cattura tgt (unconstrained) e s4u (constrained) da windows |
| `getST.py` (impacket) | kerberos tool | cli - attivo | impersonazione via s4u nella constrained delegation |
| `Coercer` / `PetitPotam` | coercion | cli - attivo | coercizione del do/dc a connettersi all'host unconstrained |
| `BloodHound` | graph enum | gui | individuazione di host/account con delega |

## Note di metodologia

In lab reale documentare: quali host/account hanno delega, l'esito della cattura TGT (unconstrained) o
dell'impersonazione S4U (constrained), e l'efficacia delle contromisure (Protected Users, rimozione
unconstrained).

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| credential access | steal or forge kerberos tickets | `T1558` | cattura o richiesta di ticket per impersonare account privilegiati. |
| credential access | forced authentication | `T1187` | coercizione di un dc a connettersi all'host con unconstrained delegation. |
| lateral movement | use alternate authentication material: pass the ticket | `T1550.003` | uso dei ticket catturati/forgiati per autenticarsi. |

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [bloodhound](<../../01-enumeration/bloodhound/README.md>) | delegation abuse | individua host/account con delega sfruttabile |
| delegation abuse | [dcsync](<../../05-credential-dumping/dcsync/README.md>) | la cattura del tgt del dc porta alla replica abusata |
| [rbcd](<../rbcd/README.md>) | delegation abuse | rbcd e la terza forma (resource-based) della stessa famiglia |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
