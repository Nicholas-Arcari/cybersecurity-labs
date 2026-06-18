> **English** | [Italiano](README.md)

to do...

Splunk is complex. Don't just include the installer. Divide the content as follows:

- SPL-Queries: Splunk uses a proprietary language (SPL). Create a Favorite-Queries.txt file with queries to find common attacks (e.g. Brute Force, Port Scanning).
- Data-Ingestion: Notes on how to configure "Forwarders" (agents that send logs to Splunk).
- Dashboards: If you export your defensive dashboard configurations (XML/JSON), save them here.

Strategic Note: Splunk vs Wireshark vs Wazuh

Wazuh (08): Tells you: "Hey, there's a suspicious file on this PC!" (Endpoint).

Splunk (08): Tells you: "I saw strange connections from the Firewall + Failed Login on the Server + Wazuh Alert, all together in the same minute!" (Correlation).

Wireshark (09): You open it after Splunk has alerted you, to look inside individual packets and understand exactly what they contained.
