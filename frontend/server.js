// server.js
const express = require('express');
const path = require('path');

const app = express();
const PORT = 3000; // Vous pouvez changer le port si nécessaire

// Servir les fichiers statiques (HTML, CSS, JS)
app.use(express.static(path.join(__dirname)));

// Point d'entrée pour la page d'accueil
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'user.html'));
});

// Démarrer le serveur
app.listen(PORT, () => {
  console.log(`Serveur lancé sur http://localhost:${PORT}`);
});
