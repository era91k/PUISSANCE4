🤖 Bot Puissance 4
==================

Un bot intelligent pour jouer au Puissance 4, conçu en utilisant PyTorch et exposé via une API Flask. Ce bot peut être entraîné pour améliorer ses performances et offre une architecture flexible pour jouer localement, tester ou s'entraîner.

🚀 Fonctionnalités principales
------------------------------

*   **API REST** pour interagir avec le bot.
    
*   Mode **entraînement** pour améliorer les performances.
    
*   **Architecture modulaire** avec des composants séparés pour une meilleure gestion.
    
*   Jouez localement contre le bot ou utilisez l'API pour intégrer le bot dans vos applications.
    

📂 Structure du projet
----------------------
```
├── api/
│ ├── app.py # API Flask pour interagir avec le bot
├── controller/
│ ├── bot_controller.py # Gestionnaire des appels au bot
├── model/
│ ├── bot.py # Définition du bot et des méthodes d'entraînement
├── test/
│ ├── local_game.py # Partie locale pour jouer contre le bot
│ ├── train_bot.py # Script pour entraîner le bot
| ├── game.py      # Jeu pui4
├── bot_model.pth # Modèle pré-entraîné du bot
└── README.md # Documentation du projet
```
## 🛠️ Prérequis

Assurez-vous d'avoir les éléments suivants installés :

- **Python 3.8+**
- **pip** (Gestionnaire de paquets)
- Les bibliothèques Python suivantes :
  - `torch`
  - `requests`
  - `Flask`
  - `numpy`

### Installation des dépendances

```bash
pip install torch requests Flask numpy
```

🧩 Comment utiliser le projet ?
-------------------------------

### 1️⃣ **Lancer l'API**

Lancez le serveur Flask pour interagir avec le bot via une API.

<code>api/app.py</code>   

Par défaut, le serveur est disponible à l'adresse : http://127.0.0.1:5000.

#### Endpoints disponibles

*   **Exemple de requête :**
```
        {"board": \[
            \[0, 0, 0, 0, 0, 0, 0\],

            \[0, 0, 0, 0, 0, 0, 0\],

            \[0, 0, 0, 0, 0, 0, 0\],

            \[0, 0, 0, 0, 0, 0, 0\],

            \[0, 0, 0, 0, 0, 0, 0\],

            \[0, 0, 0, 0, 0, 0, 0\]
        \]}
```
*   **Exemple de réponse :**
```
        {
            "move": 3
        }
```

### 2️⃣ **Jouer localement contre le bot**

Utilisez le fichier local\_game.py pour jouer une partie contre le bot.

> test/local_game.py 

Suivez les instructions affichées pour jouer au Puissance 4 dans le terminal.

### 3️⃣ **Entraîner le bot**

Lancez le fichier train\_bot.py pour entraîner le bot en jouant des parties simulées contre lui-même.

> test/train_bot.py 

Le modèle entraîné sera automatiquement sauvegardé dans ```./bot_model.pth```. Chaque entraînement améliore les capacités du bot en fonction des parties précédentes.

🏗️ Architecture du projet
--------------------------

### 1\. **BotAI** (Réseau Neuronal)

Le réseau neuronal BotAI utilise PyTorch pour prendre des décisions.Il est constitué de couches entièrement connectées avec activation ReLU et une sortie Softmax pour choisir la meilleure colonne.

### 2\. **API Flask**

L'API expose un point d'entrée pour interagir avec le bot.Elle utilise le contrôleur BotController pour déléguer les tâches au bot.

### 3\. **Modes d'utilisation**

*   **Mode évaluation :** Utilisé pour jouer contre le bot via l'API ou localement.
    
*   **Mode entraînement :** Le bot apprend en jouant des parties contre lui-même.
    

💡 Conseils d'amélioration
--------------------------

*   Ajustez les hyperparamètres (par ex. learning\_rate, nombre de parties simulées) pour améliorer l'entraînement.
    
*   Implémentez un algorithme plus complexe pour entraîner le bot avec des stratégies spécifiques.
    
*   Intégrez des tests unitaires pour valider les comportements du bot.