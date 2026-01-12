to do...

DNS Enumeration

Spesso le aziende dimenticano vecchi sottodomini attivi (es. dev.azienda.com o test.azienda.com).

Zone Transfer: Un vecchio attacco ma va sempre testato. Se il server DNS è mal configurato, ti regala la mappa di tutta la rete.

Sublist3r: Uno script Python classico per aggregare sottodomini da varie fonti.

---

Differenza Chiave: 01 vs 03

È facile confondersi tra la 01-Recon e la 03-Web:

01-Recon (Infrastruttura): Cerco QUALI computer/server esistono. (Risultato: admin.sito.com esiste e ha l'IP 1.2.3.4 con la porta 80 aperta).

03-Web (Applicazione): Cerco COSA c'è dentro il sito. (Risultato: Su admin.sito.com c'è una pagina /login.php vulnerabile a SQL Injection).