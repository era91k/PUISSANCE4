
# **PUISSANCE 4**  
**Projet de Développement AOS**

## **Membres de l'Équipe**
- **Rachad Marwane**  
- **Lekouara Abdelrafik**  
- **Antunes Mendes Alexandre**  
- **Felli Mouheb**  
- **Levacher Jimmy**  
- **Gomes Nicolas**  
- **Andirandalaoarivony Era**  

## **Technologies Utilisées**
- **Backend** : Python, NodesJS
- **Frontend** : HTML, CSS, JavaScript
- **Base de Données** : MySQL

## **Objectifs du Projet**
### L'objectif principal de ce projet est de créer un jeu de Puissance 4 avec plusieurs fonctionnalités :
- Mode Local : Permet aux joueurs de jouer contre un autre joueur sur le même appareil.
- Mode en Ligne : Permet aux joueurs de se connecter et de jouer contre d'autres utilisateurs en ligne.
- Mode d'Apprentissage : Permet au joueur de jouer contre l'ordinateur.
- Reconnaissance Vocale : Permet d’interagir avec le jeu via des commandes vocales.
- Authentification des Utilisateurs : Système de connexion et d’inscription des utilisateurs avec gestion des sessions.
- Architecture Micro-services : Architecture décentralisée basée sur des micro-services pour assurer une évolutivité et une maintenance facilitées.

## **Installation et Exécution**

### **Pré-requis** :
- Docker et Docker Compose installés sur votre machine.

### **Étapes d'Installation** :

1. **Cloner le dépôt** :

   Si vous n’avez pas encore cloné le dépôt, exécutez la commande suivante :
   ```bash
   git clone https://github.com/Marwane-20/PUISSANCE4.git
   cd puissance4
   ```

2. **Construire l'Image Docker** :
   Cela construira les images Docker nécessaires pour exécuter le projet.
   ```bash
   docker-compose build
   ```

3. **Démarrer le Conteneur Docker** :
   Cette commande lancera les conteneurs Docker et démarrera les services associés.
   ```bash
   docker-compose up
   ```

   Cela va démarrer les services suivants :
   - **Backend API** : Python (FastAPI ou Flask)
   - **Base de données** : MySQL
   - **Frontend** : Serveur HTTP pour servir l'application web
   - **Socket.IO** (si applicable) : Pour la gestion des connexions en ligne.

4. **Accéder à la Documentation de l'API** :
   - **Swagger UI** (pour tester l'API) :  
     [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc** (alternative pour la documentation) :  
     [http://localhost:8000/redoc](http://localhost:8000/redoc)

   Ces liens vous permettront de consulter et tester l'API via une interface graphique.

### **Exécuter le Jeu via le CLI** :
Tu peux aussi interagir avec le jeu via un script CLI. Pour cela, exécute simplement le script Python `cli.py` pour lancer une partie :

```bash
python cli.py
```