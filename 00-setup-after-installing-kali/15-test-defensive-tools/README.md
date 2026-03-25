# 15 - Testa gli strumenti difensivi

> - **Fase:** System Setup - Validazione Difese (Defense Testing)
> - **Priorita:** Alta - la configurazione non validata e falsa sicurezza
> - **Prerequisiti:** Firewall (passo 04), SSH hardening (passo 06), IDS (passo 14) configurati; una VM target o la macchina locale come bersaglio
> - **Tempo stimato:** 30-60 minuti per un test completo

---

## Approccio

A differenza degli altri passaggi, questo non ha un unico comando: e una fase di validazione empirica. L'obiettivo e generare traffico di test controllato verso il proprio sistema e verificare che le difese rispondano come atteso.

```Bash
# Test 1: verifica che il firewall blocchi le porte chiuse
nmap -sV 127.0.0.1                          # Da locale: porte aperte visibili
nmap -sV [IP_della_macchina] -p 1-65535     # Da un'altra VM: solo le porte permesse da UFW

# Test 2: verifica che SSH risponda sulla nuova porta
ssh -p 2222 utente@[IP]          # Deve funzionare
ssh -p 22 utente@[IP]            # Deve essere rifiutato (porta chiusa)

# Test 3: verifica che l'IDS rilevi il port scan
sudo tail -f /var/log/suricata/fast.log &    # Apri il log in background
nmap -sS [IP_della_macchina]                 # Lancia scan da un'altra VM
# -> Suricata deve generare alert per "ET SCAN"

# Test 4: verifica blocco login root SSH
ssh root@[IP] -p 2222    # Deve essere rifiutato con "Permission denied"
```

---

## Perche farlo?

Configurare un firewall o un IDS non basta: devi avere la conferma empirica che funzionino. Una regola UFW scritta con un refuso, un parametro sshd_config non ricaricato, una regola Suricata non aggiornata: sono tutti scenari in cui credi di essere protetto ma non lo sei.

## Cosa accade dopo?

Hai la conferma oggettiva, basata su evidenze, che le difese configurate rilevano e bloccano gli attacchi simulati. Ogni test superato e un requisito validato; ogni test fallito e un problema da correggere prima di esporre il sistema ad ambienti reali.

## Cosa rischi se non lo fai?

"False sense of security": il sistema sembra configurato correttamente ma una misconfiguration nascosta lo lascia esposto. Scoprirlo durante un engagement reale, quando la macchina attaccante e stata compromessa, e un disastro operativo.

---

## Checklist di validazione

| Test | Comando | Risultato atteso |
| :--- | :--- | :--- |
| Firewall attivo | `sudo ufw status` | `Status: active` |
| Porte chiuse | `nmap [IP]` da altra VM | Solo porte autorizzate visibili |
| SSH porta personalizzata | `ssh -p 2222 utente@[IP]` | Login riuscito |
| SSH root bloccato | `ssh root@[IP] -p 2222` | `Permission denied` |
| IDS alert port scan | `nmap -sS [IP]` + `fast.log` | Alert ET SCAN in Suricata |
| Kernel hardening | `sysctl net.ipv4.tcp_syncookies` | `= 1` |

---

> **Nota:** I test devono essere eseguiti preferibilmente da una VM separata sulla stessa rete (non da localhost) per simulare la prospettiva di un attaccante esterno. Per un test piu realistico, usare la VM Windows usata nel resto del laboratorio come sorgente degli attacchi simulati.
