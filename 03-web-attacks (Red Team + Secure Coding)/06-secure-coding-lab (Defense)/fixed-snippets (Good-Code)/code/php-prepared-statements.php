<?php
/*
 * SECURE CODING LAB: PHP Prepared Statements (PDO)
 * * Questo script dimostra come prevenire SQL Injection al 100%.
 * Invece di concatenare le stringhe, usiamo i "Placeholders" (:email, :status).
 */

// 1. Configurazione Database (Simulato o Reale)
$host = '127.0.0.1';
$db   = 'dvga_db'; // O un db di test che hai creato
$user = 'root';
$pass = 'toor'; // Password di Kali standard
$charset = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false, // FONDAMENTALE per la sicurezza reale
];

try {
    // Connessione Sicura
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\PDOException $e) {
    // In produzione non mostrare mai l'errore reale all'utente!
    die("Errore di connessione al DB (Simulato).");
}

// --- SCENARIO: LOGIN UTENTE ---

// Input dell'utente (potenzialmente malevolo)
// Immagina che $_POST['email'] sia:  admin' OR '1'='1
$user_email = $_POST['email'] ?? 'test@example.com'; 
$user_status = 'active';

echo "<h3>Input Utente: " . htmlspecialchars($user_email) . "</h3>";

// ---------------------------------------------------------
// MODO SBAGLIATO (VULNERABILE A SQLi)
// ---------------------------------------------------------
// $sql = "SELECT * FROM users WHERE email = '$user_email'";
// $pdo->query($sql); 
// --> Qui l'hacker entra senza password perché ' OR '1'='1 è sempre vero.


// ---------------------------------------------------------
// MODO CORRETTO (PREPARED STATEMENTS)
// ---------------------------------------------------------

// 1. PREPARE: Definiamo lo scheletro con i segnaposto (:email)
// Il database compila questo piano d'azione PRIMA di vedere i dati.
$stmt = $pdo->prepare("SELECT id, username, role FROM users WHERE email = :email AND status = :status");

// 2. BIND & EXECUTE: Inviamo i dati separatamente.
// Anche se $user_email contiene codice SQL, verrà trattato come semplice testo.
$stmt->execute([
    'email' => $user_email,
    'status' => $user_status
]);

// 3. FETCH: Prendiamo i risultati
$user = $stmt->fetch();

echo "<hr>";
if ($user) {
    echo "Login Riuscito! Benvenuto " . htmlspecialchars($user['username']);
} else {
    echo "Login Fallito. Nessun utente trovato con questa email.";
    echo "<br><small>(Nota: Anche con input malevolo, la query non si è rotta!)</small>";
}

?>