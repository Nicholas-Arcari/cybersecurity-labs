from flask import Flask, jsonify, request

app = Flask(__name__)

# DATABASE SIMULATO
# In un caso reale, questo sarebbe un DB SQL
accounts = {
    1000: {"owner": "Alice (Tu)", "balance": 50.00, "iban": "IT99A000"},
    1001: {"owner": "Bob (Vittima)", "balance": 150000.00, "iban": "IT88B111"},
    1002: {"owner": "Charlie (CEO)", "balance": 9999999.99, "iban": "IT77C222"},
    1003: {"owner": "Dave (Admin)", "balance": 2500.00, "iban": "IT66D333"}
}

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Leaky Bank API. Use /api/balance/<id> to check balance."})

# ENDPOINT VULNERABILE (IDOR)
@app.route('/api/balance/<int:account_id>', methods=['GET'])
def get_balance(account_id):
    # QUI MANCA IL CONTROLLO DI SICUREZZA!
    # L'API dovrebbe controllare: "L'utente loggato possiede questo account_id?"
    # Invece, si fida ciecamente dell'input.
    
    account = accounts.get(account_id)
    
    if account:
        return jsonify({
            "status": "success",
            "account_id": account_id,
            "data": account
        })
    else:
        return jsonify({"status": "error", "message": "Account not found"}), 404

if __name__ == '__main__':
    # Eseguiamo sulla porta 5000
    print("[*] Leaky Bank API is running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)