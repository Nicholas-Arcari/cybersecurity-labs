# 13 - Rafforza il kernel (sysctl Hardening)

> - **Fase:** System Setup - Kernel & Network Hardening
> - **Priorita:** Alta - protezione da classi di attacchi di rete comuni
> - **Prerequisiti:** Accesso root o sudo; editor di testo
> - **Tempo stimato:** 10 minuti

---

## Comandi

Modificare `/etc/sysctl.conf`:

```Bash
sudo vim /etc/sysctl.conf
```

Parametri di hardening da aggiungere o modificare:

```Bash
# Protezione da IP spoofing e source routing
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_source_route = 0

# Protezione da SYN flood (TCP syncookies)
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048

# Ignora ICMP ping (riduce visibilita su rete)
net.ipv4.icmp_echo_ignore_all = 1

# Protezione da ICMP redirect (routing manipulation)
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0

# Protezione memoria: disabilita core dump SUID
fs.suid_dumpable = 0

# ASLR (Address Space Layout Randomization) - massimo
kernel.randomize_va_space = 2
```

Applicare le modifiche senza riavvio:

```Bash
sudo sysctl -p    # Carica /etc/sysctl.conf
sudo sysctl -a    # Verifica tutti i parametri correnti
```

---

## Perche farlo?

Le impostazioni di default del kernel Linux favoriscono la compatibilita e l'interoperabilita, non la sicurezza. Molti parametri di rete sono configurati per il caso d'uso generale (server o workstation in LAN sicura), non per un sistema esposto a reti potenzialmente ostili come quelle usate durante i lab.

## Cosa accade dopo?

Il kernel ignorera ping flood e ICMP redirect malevoli, impedira il source routing (usato per spoofing), limitera l'efficacia dei SYN flood e rendera piu difficile lo sfruttamento di vulnerabilita di memoria tramite ASLR massimizzato.

## Cosa rischi se non lo fai?

Il sistema e suscettibile ad attacchi DoS (Denial of Service), IP spoofing e routing manipulation. Su una rete di laboratorio condivisa, queste tecniche potrebbero essere usate da altri partecipanti per interferire con le tue sessioni.

---

> **Nota:** Alcune impostazioni (es. `icmp_echo_ignore_all = 1`) possono interferire con strumenti di diagnostica di rete come `ping`. Adattare secondo le necessita operative: sui sistemi di laboratorio isolati si puo essere piu aggressivi; su macchine di produzione valutare l'impatto prima di applicare. Verificare la compatibilita con eventuali VPN o tunnel di rete prima dell'applicazione.
