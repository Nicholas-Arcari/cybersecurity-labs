> [English](THEORETICAL-FOUNDATIONS.en.md) | **Italiano**

# Fondamenti Teorici - Modulo 10: Cloud Security

> - **Livello:** Analisi accademica (complemento teorico ai README operativi del modulo)
> - **Scopo:** Formalizzare l'identita come perimetro, il metadata SSRF come confused deputy, l'isolamento cloud/container come proprieta configurabile e la co-residenza come canale laterale.
> - **Prerequisiti:** README operativi del modulo 10 (finding CLOUD-); nozioni di controllo degli accessi, teoria dei grafi e isolamento dei sistemi.

---

## Abstract

Il cloud dissolve il perimetro di rete e sposta la sicurezza sull'identita e sulla configurazione. Il documento lo formalizza attorno a quattro nuclei. L'**identita come perimetro** e il collasso del controllo d'accesso basato sulla posizione di rete verso quello basato sulla credenziale, con la privilege escalation IAM come raggiungibilita in un grafo di permessi [Sheyner et al. 2002]. Il **metadata SSRF** e l'abuso delle identita gestite sono istanze cloud del **confused deputy** [Hardy 1988]. L'**isolamento** di VM e container e una proprieta **configurabile**, non una barriera fisica, con la co-residenza e i side-channel [Ristenpart et al. 2009; Zhang et al. 2012] a definirne i limiti. Il tutto e governato dal **Shared Responsibility Model** (NIST SP 800-145) e dalla riduzione della superficie [Manadhata & Wing 2011], unificando il modulo 10 con i principi dell'intero percorso.

---

## 1. Modello dell'Avversario

L'avversario cloud opera in un ambiente dove **ogni servizio e un endpoint API pubblico** e l'unico controllo d'accesso e l'identita. Le sue vie d'ingresso tipiche: una credenziale trapelata (modulo 04/07/09), un SSRF su un'applicazione (modulo 03), un container o un workload compromesso. L'obiettivo e l'escalation da un'identita limitata al controllo dell'account/tenant/progetto, attraverso l'attraversamento di un grafo di permessi (sezione 3.2). Rispetto agli altri moduli, l'avversario non attraversa un perimetro di rete ma un **grafo di autorizzazioni**: la sua potenza dipende dalla configurazione IAM, non dalla topologia. Si adotta anche, per la co-residenza, un modello honest-but-curious sul vicino di tenancy (sezione 3.4).

---

## 2. Proprieta di Sicurezza in Gioco

- **Least privilege sull'identita:** ogni identita (umana, managed identity, service account) deve avere i soli permessi necessari; la sua violazione trasforma un leak in account takeover.
- **Autorizzazione basata sull'intenzione:** un componente privilegiato non deve agire per conto di un principale non autorizzato (confused deputy, sezione 3.3).
- **Isolamento dei tenant e dei workload:** la co-residenza non deve consentire flussi informativi tra tenant/container (sezione 3.4).
- **Immutabilita della configurazione sicura:** i default sicuri devono essere non facilmente derogabili (es. S3 Block Public Access), rendendo l'errore difficile e non solo sconsigliato.

---

## 3. Fondamenti Teorici

### 3.1 Il collasso del perimetro e l'identita come controllo d'accesso

On-premise, il controllo d'accesso e stratificato geograficamente: la posizione di rete (essere "dentro") conferisce fiducia implicita. Il cloud rimuove questa stratificazione: ogni servizio e raggiungibile via API da ovunque, e la fiducia basata sulla posizione perde significato. Il controllo d'accesso si concentra interamente sull'identita: chi presenta una credenziale valida e autorizzato per cio che la credenziale permette. E la realizzazione forzata del principio Zero Trust, gia introdotto come ideale nel modulo 07 (sezione 6): il cloud non offre l'opzione della fiducia posizionale, quindi la impone. Questo unifica teoricamente "l'identita e il nuovo perimetro" (cloud) con la "transitivita della fiducia" (modulo 07, sezione 3.2): in entrambi, la propagazione della compromissione e determinata dalle credenziali, non dalla rete.

### 3.2 Privilege escalation IAM come raggiungibilita in un grafo di permessi

La configurazione IAM definisce un **grafo di permessi**: i nodi sono identita e risorse, gli archi sono i permessi che consentono a un'identita di agire su una risorsa o di assumere/modificare un'altra identita. La privilege escalation IAM e la ricerca di un cammino da un'identita limitata a privilegi amministrativi, esattamente il problema di raggiungibilita nei grafi di attacco [Sheyner et al. 2002] (modulo 07, sezione 3.1). Un permesso apparentemente innocuo (`iam:CreatePolicyVersion`, `iam:PassRole`) e un arco che collassa la distanza verso l'admin. La difesa e la rimozione di archi (least privilege, permission boundaries, SCP) per disconnettere le identita limitate dai nodi privilegiati. Questo fornisce la base teorica al fatto che strumenti come PMapper (analisi a grafo dei permessi) e Pacu (`iam__privesc_scan`) risolvano, offensivamente e difensivamente, lo stesso problema di reachability.

### 3.3 Metadata SSRF e managed identity come confused deputy cloud

Il furto di token via metadata service e l'abuso di managed identity/service account sono istanze cloud del **confused deputy** [Hardy 1988] gia formalizzato nel modulo 03 (sezione 3.2). Nel metadata SSRF, l'applicazione web e il deputy: possiede la posizione privilegiata (raggiungibilita del metadata endpoint, che consegna credenziali a chi lo interroga dall'interno) e viene indotta dall'attaccante a usarla per suo conto. Nell'abuso di managed identity, la risorsa compromessa e il deputy: possiede l'identita gestita e la eredita a chi la controlla. La radice comune e la **fiducia basata sulla posizione** (il metadata si fida di chiunque lo raggiunga dall'interno), la stessa assunzione che la sezione 3.1 identifica come dissolta nel modello corretto: l'SSRF sfrutta il residuo di fiducia posizionale che il cloud non ha ancora eliminato. La contromisura (restringere le richieste in uscita, Workload Identity, IMDSv2 con vincoli) e l'applicazione della verifica dell'intenzione e del least privilege.

### 3.4 Isolamento come configurazione: container e co-residenza

L'isolamento nel cloud non e una barriera fisica ma una proprieta **configurabile**, con due manifestazioni. Per i **container**, l'isolamento deriva da meccanismi del kernel condiviso (namespace, cgroup, capability), non da un hypervisor: e efficace se configurato correttamente, aggirabile se no (Docker socket montato, `--privileged`). NIST SP 800-190 codifica questo modello di rischio. La proprieta corretta e "il container e isolato solo quanto lo configuro", e l'escape e lo sfruttamento di un isolamento incompleto, non la rottura di una barriera (modulo 10, runtime security). Per le **VM**, [Ristenpart et al. 2009] dimostrano che la co-residenza di tenant diversi sullo stesso hardware fisico apre canali laterali: un attaccante puo collocare deliberatamente una propria VM sullo stesso host della vittima e, tramite side-channel della cache condivisa, estrarre informazione - fino a chiavi crittografiche [Zhang et al. 2012]. Questo mostra che l'isolamento logico dei tenant non implica l'isolamento fisico delle risorse, e che la condivisione dell'hardware e una superficie d'attacco autonoma.

---

## 4. Analisi Quantitativa

### 4.1 La probabilita di co-residenza

[Ristenpart et al. 2009] quantificano la fattibilita della co-residenza: mostrano che, con strategie di lancio mirate, un attaccante puo ottenere la co-residenza con una vittima target su un cloud pubblico con probabilita non trascurabile e a basso costo, e che la co-residenza e verificabile tramite side-channel. La conseguenza teorica e che l'assunzione "il multi-tenancy e trasparente e isolato" e quantitativamente falsificata: la condivisione fisica ha un costo di sicurezza misurabile. E la ragione per cui carichi ad altissima sensibilita ricorrono a tenancy dedicata (dedicated instances), che elimina la co-residenza al costo dell'efficienza del multi-tenancy.

### 4.2 Il costo asimmetrico del default insicuro

Il caso dei bucket S3 pubblici illustra quantitativamente il principio "rendere l'errore difficile". Un default sicuro (bucket privato) protegge finche `n` operatori non sbagliano; la probabilita che almeno uno renda pubblico un bucket cresce come `1 - (1-p)^n` (la stessa formula dell'anello debole, modulo 05, sezione 4.2), tendente a 1 su scala. "Block Public Access" a livello di account rimuove la classe intera dell'errore: non riduce `p`, azzera lo spazio in cui l'errore ha effetto. E la traduzione cloud del principio, gia visto nei prepared statements (modulo 03), per cui eliminare strutturalmente una classe batte inseguire le istanze.

---

## 5. Rassegna della Letteratura

La co-residenza e i side-channel cross-VM sono dimostrati da [Ristenpart et al. 2009] e [Zhang et al. 2012], riferimenti fondativi della sicurezza dell'isolamento cloud. Il confused deputy e di [Hardy 1988]. La privilege escalation come raggiungibilita si fonda sui grafi di attacco di [Sheyner et al. 2002]. Il least privilege e i principi di progettazione sono di [Saltzer & Schroeder 1975]; la riduzione della superficie di [Manadhata & Wing 2011]. Le definizioni e i modelli di rischio normativi sono in NIST SP 800-145 (definizione di cloud), NIST SP 800-190 (container) e NIST SP 800-63B (identita). La gestione dei segreti si richiama ai principi entropici e di costo dei moduli 04 e 07.

---

## 6. Limiti e Problemi Aperti

1. **Complessita IAM come superficie irriducibile.** Lo spazio delle configurazioni IAM (centinaia di servizi, migliaia di azioni, policy che si compongono) e cosi vasto che l'analisi manuale esaustiva delle vie di privesc e intrattabile; gli strumenti a grafo (PMapper) sono necessari ma soffrono dell'esplosione combinatoria dei grafi di attacco [Sheyner et al. 2002].

2. **Isolamento senza condivisione fisica.** Eliminare completamente i side-channel di co-residenza [Ristenpart et al. 2009; Zhang et al. 2012] richiede di rinunciare al multi-tenancy (tenancy dedicata), sacrificando l'efficienza economica che e la ragione d'essere del cloud. Il compromesso isolamento/efficienza resta aperto.

3. **Fiducia posizionale residua.** Il metadata SSRF (sezione 3.3) mostra che il cloud non ha ancora eliminato ogni residuo di fiducia basata sulla posizione. La realizzazione completa di Zero Trust a livello di workload (ogni richiesta autenticata e autorizzata, nessuna fiducia implicita interna) e parziale nelle infrastrutture reali.

---

## 7. Sintesi e Collegamento alla Pratica

I finding `CLOUD-` del modulo istanziano questo quadro: la privilege escalation IAM (CLOUD-001) e la raggiungibilita nel grafo di permessi della sezione 3.2; il metadata SSRF e l'abuso di managed identity/service account (CLOUD-003/004) sono i confused deputy della sezione 3.3; il container escape (CLOUD-006) e l'isolamento-come-configurazione della sezione 3.4; i bucket S3 esposti (CLOUD-002) illustrano il costo del default insicuro della sezione 4.2; l'auditing e l'hardening (CLOUD-008/010) sono la rimozione di archi e la riduzione della superficie. Le contromisure documentate - least privilege, permission boundaries, Block Public Access, Workload Identity, Pod Security, shift-left - sono le realizzazioni operative dei principi qui formalizzati. Il documento chiude il percorso mostrando che il cloud non introduce principi nuovi ma porta all'estremo quelli gia incontrati: il confused deputy (modulo 03), la transitivita della fiducia (modulo 07), la riduzione della superficie (moduli 01, 08), l'eliminazione strutturale delle classi di errore (modulo 03). L'identita come perimetro e la sintesi finale: dove la posizione non conferisce piu fiducia, la sicurezza e la correttezza della configurazione degli accessi.

---

## Riferimenti

Sottoinsieme della bibliografia master (`../REFERENCES.md`) rilevante per questo modulo:

- [Ristenpart et al. 2009] - co-residenza e side-channel nel cloud pubblico.
- [Zhang et al. 2012] - side-channel cross-VM ed estrazione di chiavi.
- [Hardy 1988] - confused deputy (base di SSRF/metadata).
- [Sheyner et al. 2002] - grafi di attacco (privesc IAM come raggiungibilita).
- [Saltzer & Schroeder 1975] - least privilege e principi di progettazione.
- [Manadhata & Wing 2011] - riduzione della superficie d'attacco.
- NIST SP 800-145 (cloud), 800-190 (container), 800-63B (identita).

---

> **Nota:** Documento a scopo educativo, complementare ai README operativi. Le citazioni rimandano a fonti reali elencate in `../REFERENCES.md`.
