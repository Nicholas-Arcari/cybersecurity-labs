import jwt
import datetime
import sys

# IL SEGRETO DEBOLE (In un caso reale, questo sarebbe nascosto nel server)
# Un attaccante non dovrebbe conoscerlo, ma proverà a indovinarlo.
SECRET_KEY = "secret123" 

def create_token(username):
    payload = {
        "user": username,
        "role": "user",  # Di default sei un utente semplice
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    # Genera il token firmato con il segreto
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token_str):
    try:
        # Il server prova a leggere il token usando la sua chiave
        decoded = jwt.decode(token_str, SECRET_KEY, algorithms=["HS256"])
        print(f"\n[+] Accesso Consentito! Ciao {decoded['user']}")
        print(f"[+] Ruolo rilevato: {decoded['role']}")
        
        if decoded['role'] == "admin":
            print("\n*** 🚩 FLAG: HAI VINTO! ACCESSO AMMINISTRATIVO SBLOCCATO ***")
            print("*** Benvenuto nel pannello di controllo segreto ***")
        else:
            print("\n[-] Accesso limitato. Non sei admin.")
            
    except jwt.InvalidSignatureError:
        print("\n[!] ERRORE: Firma non valida! Qualcuno ha manomesso il token?")
    except Exception as e:
        print(f"\n[!] Errore: {e}")

# Menu semplice
if __name__ == "__main__":
    print("--- JWT Lab: Weak Secret Challenge ---")
    print("1. Ottieni un token come 'guest'")
    print("2. Tenta di accedere con un token esistente")
    choice = input("Scegli (1/2): ")

    if choice == "1":
        t = create_token("guest")
        print(f"\nEcco il tuo token (Copialo!):\n{t}")
    elif choice == "2":
        t_input = input("Incolla il token qui: ")
        verify_token(t_input)