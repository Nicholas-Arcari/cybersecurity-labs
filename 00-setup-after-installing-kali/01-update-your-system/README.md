# 01 - Aggiorna il sistema

> - **Fase:** System Setup - Aggiornamento pacchetti e kernel
> - **Priorita:** Alta - eseguire come primo passo assoluto dopo l'installazione
> - **Prerequisiti:** Connettivita internet; accesso sudo o root
> - **Tempo stimato:** 5-20 minuti (dipende dalla connessione e dai pacchetti da aggiornare)

---

## Comandi

```Bash
sudo apt update && sudo apt upgrade -y
```

---

## Perche farlo?

Le immagini ISO di installazione sono statiche e spesso vecchie di mesi. I repository contengono le versioni piu recenti del software, incluse le patch di sicurezza rilasciate dopo la pubblicazione dell'ISO.

## Cosa accade dopo?

Il sistema scarica le ultime definizioni dei pacchetti, corregge bug noti e aggiorna il kernel Linux all'ultima versione stabile disponibile nei repository Kali.

## Cosa rischi se non lo fai?

Lavorerai con software obsoleto che potrebbe contenere vulnerabilita di sicurezza gia note agli attaccanti, rendendo il sistema instabile o facilmente penetrabile. Durante un engagement, un sistema attaccante non aggiornato e un rischio operativo.

---

> **Nota:** Eseguire periodicamente (almeno una volta a settimana) o prima di ogni sessione operativa importante. Combinare con il passo 07 (aggiornamenti automatici) per la manutenzione ordinaria.
