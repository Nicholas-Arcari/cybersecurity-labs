# VULNERABLE SNIPPET: Command Injection (RCE)
# PERICOLO: Questo script permette di eseguire comandi sul tuo PC!

import os

def vulnerable_ping():
    print("--- PING TOOL (VULNERABLE) ---")
    print("Inserisci un IP da pingare (es. 8.8.8.8)")
    
    # 1. Prendiamo l'input dell'utente
    target_ip = input("IP > ")

    # 2. IL CODICE SBAGLIATO
    # Concateniamo l'input direttamente nel comando di sistema.
    # Se l'utente scrive: "8.8.8.8; ls -la", il sistema eseguirà ENTRAMBI.
    command = "ping -c 1 " + target_ip
    
    print(f"\n[DEBUG] Sto eseguendo: {command}\n")
    
    # 3. Esecuzione (Boom!)
    os.system(command)

if __name__ == "__main__":
    vulnerable_ping()