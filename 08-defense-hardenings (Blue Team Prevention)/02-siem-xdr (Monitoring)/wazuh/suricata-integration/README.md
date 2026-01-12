# Suricata

L'unione tra Wazuh (che guarda cosa succede dentro il sistema) e Suricata (che guarda cosa passa nella rete) è una combinazione potentissima. Trasforma Kali in un sistema di difesa completo (SIEM + IDS).

Note: Attenzione alle risorse: Suricata consuma parecchia memoria e CPU analizzando il traffico. Se la tua macchina è lenta, potrebbe rallentare ulteriormente.

---

## Installa Suricata (se non c'è già)

```Bash
sudo apt update
sudo apt install suricata
```

---

## Configura Suricata per ascoltare l'Hotspot

Bisogna dire a Suricata di ascoltare l'interfaccia giusta (probabilmente `wlan0`), altrimenti ascolterà `eth0` (il cavo) e non vedrà nulla

Controlla il nome della tua interfaccia Wi-Fi:

```Bash
ip a
```

(Cerca quella con l'`IP`, es. `wlan0`)

Modifica la configurazione di Suricata:

```Bash
sudo nano /etc/suricata/suricata.yaml
```

Cerca la sezione `af-packet`: (scendi un po' nel file). Cambia interface: `eth0` con il nome della tua interfaccia (es. `wlan0`)

```YAML
# Esempio:
af-packet:
  - interface: wlan0  # <--- Cambia questo
```

Aggiorna le regole di rilevamento (firme dei virus/attacchi):

```Bash
sudo suricata-update
```

Avvia Suricata:

```Bash
sudo systemctl enable suricata
sudo systemctl start suricata
```

---

## Collega Wazuh a Suricata

Ora dobbiamo dire a Wazuh: "Ehi, leggi tutto quello che scrive Suricata e mostramelo nella dashboard"

Suricata scrive i suoi log in un file chiamato `eve.json`. Wazuh deve solo leggerlo

Apri il file di configurazione del Manager (dato che sei sulla stessa macchina):

```Bash
sudo nano /var/ossec/etc/ossec.conf
```

Scorri fino alla sezione `<ossec_config>`. Incolla questo blocco di codice alla fine (ma prima dell'ultima riga `</ossec_config>`):

```Bash
<localfile>
  <log_format>json</log_format>
  <location>/var/log/suricata/eve.json</location>
</localfile>
```

Salva (CTRL+O, Invio) ed esci (CTRL+X)

Riavvia il Wazuh Manager per applicare la modifica:

```Bash
sudo systemctl restart wazuh-manager
```

---

## Testiamo se funziona

Non ha senso configurare tutto se non proviamo a "far scattare l'allarme". Usiamo un comando sicuro che simula un attacco rilevato da Suricata

Apri un terminale e lancia questo comando (genera un falso alert `"GPL ATTACK_RESPONSE id check returned root"`):

```Bash
curl http://testmyids.com
```

(Dovresti vedere come risposta: `uid=0(root) gid=0(root) groups=0(root)`)

Controlla se Suricata l'ha visto (guarda le ultime righe del log):

```Bash
tail -f /var/log/suricata/fast.log
```

Dovresti vedere una scritta rossa o un log relativo a `GPL ATTACK_RESPONSE`. (Premi CTRL+C per uscire)

---

## Guarda nella Dashboard

Vai sulla tua Wazuh Dashboard (`https://localhost`)

Vai su Wazuh -> Security events

Nella barra di ricerca in alto, scrivi: `rule.groups:suricata`

Dovresti vedere l'alert generato dal tuo curl