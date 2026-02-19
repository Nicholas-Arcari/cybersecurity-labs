<?php
// VULNERABLE SNIPPET: SQL Injection (Classic)
// PERICOLO: Non usare mai questo codice in produzione!

// Simuliamo un input (es. da URL: ?id=1)
$user_id = $_GET['id'] ?? '1';

// --- IL CODICE SBAGLIATO ---
// L'errore è usare il punto (.) per unire la variabile alla query.
// Il database non saprà distinguere tra il comando e il dato.
$query = "SELECT * FROM users WHERE id = " . $user_id;

?>

<!DOCTYPE html>
<html>
<body style="font-family: monospace;">
    <h1>Vulnerable SQL Snippet</h1>
    <p>Prova ad aggiungere all'URL: <code>?id=1 OR 1=1</code></p>
    
    <div style="background: #ffcccc; padding: 20px; border: 1px solid red;">
        <h3>La Query che il DB eseguirà:</h3>
        <p><strong><?php echo $query; ?></strong></p>
    </div>

    <p>Se vedi <code>OR 1=1</code> dentro la query, l'attacco ha funzionato!</p>
</body>
</html>