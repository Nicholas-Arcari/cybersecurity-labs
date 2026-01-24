# Rafforza il kernel (Hardening)

Comando: Edit `/etc/sysctl.conf`:

```Bash
net.ipv4.icmp_echo_ignore_all = 1
net.ipv4.tcp_syncokies = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.all.accept_source_route = 0
```

- Perché farlo?

Le impostazioni di default di Linux favoriscono la compatibilità, non la sicurezza

- Cosa accade dopo?

Il kernel ignora ping flood, impedisce il routing di pacchetti sospetti e protegge la memoria

- Cosa rischi se non lo fai?

Il sistema è suscettibile ad attacchi DoS (Denial of Service) o spoofing che potrebbero far cadere la connessione di rete