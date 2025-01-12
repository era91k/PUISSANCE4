
# **PUISSANCE 4**  
**Projet de Développement AOS** : [Jeu du Puissance 4 en ligne](https://puissance4-2f2e.onrender.com/user.html), développé dans le cadre du cours d'Architecture Orientée Services en Master 2 MIAGE à l'Université d'Évry Paris Saclay.

![puissance4-interface](https://cdn.discordapp.com/attachments/683698523748827145/1327786485180534918/image.png?ex=67845507&is=67830387&hm=8d8b9c450c1b6c3d08f4611afbc591e144b7edfc9466b1f9c42aa8d4d154441b&)

## **👥 Membres de l'Équipe**
- **Rachad Marwane**  
- **Lekouara Abdelrafik**  
- **Antunes Mendes Alexandre**  
- **Felli Mouheb**  
- **Levacher Jimmy**  
- **Gomes Nicolas**  
- **Andriandalaoarivony Era**  

## **🚀 Objectifs du Projet**
### L'objectif principal de ce projet est de créer un jeu de Puissance 4 avec plusieurs fonctionnalités :
- Mode Local : Permet aux joueurs de jouer contre un autre joueur sur le même appareil.
- Mode en Ligne : Permet aux joueurs de créer/rejoindre une partie et de jouer contre d'autres utilisateurs en ligne.
- Mode d'Apprentissage : Permet au joueur de jouer contre une IA avec 3 niveaux de difficultés.
- Reconnaissance Vocale : Permet d’interragir avec le jeu via des commandes vocales.
- Authentification des Utilisateurs : Système de connexion et d’inscription des utilisateurs avec gestion des sessions.
- Architecture Micro-services : Architecture décentralisée basée sur des micro-services pour assurer une évolutivité et une maintenance facilitées.
- Intégration Continue : Mise en place d'un pipeline CI avec des tests unitaires pour garantir la qualité et la fiabilité du code.
- Conteneurisation : Utilisation de conteneurs pour isoler et simplifier le déploiement des services.

## **📝 Installation et Exécution**

### **Pré-requis** :
- Docker et Docker Compose installés sur votre machine.

### **Étapes d'Installation** :

1. **Cloner le dépôt** :

Si vous n’avez pas encore cloné le dépôt, exécutez la commande suivante :
```bash
git clone https://github.com/Marwane-20/PUISSANCE4.git
cd PUISSANCE4
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
- **game-service** : le service qui permet de gérer la logique du jeu (FastAPI)
- **ai-service** : le service qui permet de gérer la logique du jeu (FastAPI)
- **user-service** : le service qui permet de gérer la gestion des utilisateurs du jeu (FastAPI)
- **Base de données** : MongoDB
- **Frontend** : Serveur HTTP Nginx pour héberger le frontend du jeu

4. **Accéder au jeu** :
- **Menu** :
   [http://localhost:8000/menu.html](http://localhost:8000/menu.html)
5. **Accéder à la Documentation de l'API** :
- **Swagger UI** de l'API game-service :  
   [http://localhost:8000/docs](http://localhost:8000/docs)
- **Swagger UI** de l'API ai-service :  
   [http://localhost:8003/docs](http://localhost:8002/docs)
- **Swagger UI** de l'API user-service :  
   [http://localhost:8002/docs](http://localhost:8003/docs)

Ces adresses vous permettront de consulter et tester l'API via une interface graphique.

## **👨🏼‍💻 Technologies Utilisées**
- **Backend** : Python, NodesJS
- **Frontend** : HTML, CSS, JavaScript
- **Base de Données** : MongoDB

## **⚖️ Licence**
Le jeu Puissance 4 est sous licence Open Source MIT et est disponible gratuitement.
