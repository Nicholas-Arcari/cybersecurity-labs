<?php
// XSS DEFENSE LAB
// Obiettivo: Impedire l'esecuzione di JavaScript arbitrario.

// Simuliamo un input utente (es. un commento o un nome)
// Se non c'è input nell'URL, usiamo un default innocuo.
// ATTACCO: Prova a passare ?name=<script>alert('Hacked')</script>
$input_utente = $_GET['name'] ?? 'Ospite';

?>

<!DOCTYPE html>
<html>
<head>
    <title>XSS Defense Lab</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .box { border: 1px solid #ccc; padding: 15px; margin-bottom: 20px; }
        .bad { background-color: #ffcccc; }
        .good { background-color: #ccffcc; }
    </style>
</head>
<body>

<h1>Test di Sicurezza XSS</h1>
<p>Prova ad attaccare questa pagina aggiungendo nell'URL: <br>
<code>?name=&lt;script&gt;alert('Hacked')&lt;/script&gt;</code></p>
<p>Oppure un payload più moderno: <br>
<code>?name=&lt;img src=x onerror=alert('XSS')&gt;</code></p>

<div class="box bad">
    <h3>Output Non Protetto (Vulnerabile)</h3>
    <p>Ciao, 
    <?php 
        // ERRORE: L'input viene stampato direttamente.
        // Il browser interpreterà i tag <script> come codice da eseguire.
        echo $input_utente; 
    ?>
    </p>
</div>

<div class="box good">
    <h3>Output Sicuro (Sanitized/Encoded)</h3>
    <p>Ciao, 
    <?php 
        // SOLUZIONE: htmlspecialchars()
        // Trasforma i caratteri speciali in entità HTML innocue.
        // < diventa &lt;
        // > diventa &gt;
        // " diventa &quot;
        // Il browser vede il testo "<script>" ma NON lo esegue.
        echo htmlspecialchars($input_utente, ENT_QUOTES, 'UTF-8'); 
    ?>
    </p>
</div>

</body>
</html>