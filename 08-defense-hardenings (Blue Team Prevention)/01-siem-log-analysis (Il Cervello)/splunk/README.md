to do...

Splunk è complesso. Non metterci solo l'installer. Dividi il contenuto così:

- SPL-Queries: Splunk usa un linguaggio proprietario (SPL). Creati un file Favorite-Queries.txt con le query per trovare attacchi comuni (es. Brute Force, Port Scanning).
- Data-Ingestion: Appunti su come configurare i "Forwarder" (gli agenti che inviano i log a Splunk).
- Dashboards: Se esporti le configurazioni (XML/JSON) delle tue dashboard difensive, salvale qui.

Nota Strategica: Splunk vs Wireshark vs Wazuh

Wazuh (08): Ti dice: "Ehi, c'è un file sospetto su questo PC!" (Endpoint).

Splunk (08): Ti dice: "Ho visto connessioni strane dal Firewall + Login fallito sul Server + Allarme di Wazuh, tutto insieme nello stesso minuto!" (Correlazione).

Wireshark (09): Lo apri dopo che Splunk ti ha avvisato, per guardare dentro i singoli pacchetti e capire esattamente cosa contenevano.