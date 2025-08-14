RecommandationEngineTG
Système de Recommandation de Films/Musiques (Simulé)
1. Introduction
Ce projet, RecommandationEngineTG, est une démonstration simple d'un algorithme de recommandation basé sur les préférences des utilisateurs. Il simule un système de recommandation que l'on pourrait trouver sur des plateformes comme Netflix ou Spotify, en mettant en œuvre des concepts fondamentaux du Machine Learning.

L'objectif principal est de montrer la capacité à construire un algorithme de recommandation fonctionnel et à l'exposer via une API REST.

2. Objectif Principal
Démontrer la compréhension et la capacité à construire un algorithme de recommandation basique en utilisant Python et des bibliothèques de ML, et à le servir via une API web.

3. Fonctionnalités Clés (MVP)
Base de Données Simulée : Un petit jeu de données (CSV) de films/musiques (titre, genre) et d'utilisateurs avec des "likes" pour certains items.

Algorithme de Recommandation Simple :

Filtrage Collaboratif Basé sur les Utilisateurs : Recommande des items que des utilisateurs "similaires" ont aimés.

Filtrage Basé sur le Contenu : Recommande des items du même genre que ceux aimés par l'utilisateur cible.

Combinaison des deux approches pour des recommandations plus robustes.

API REST : Un endpoint simple (/recommend/{user_id}) qui prend un ID utilisateur et retourne une liste de recommandations.

4. Structure du Projet
RecommandationEngineTG/
│
├── data/
│   ├── users.csv             # Données simulées des likes utilisateurs
│   └── items.csv             # Données simulées des films/musiques (titre, genre)
│
├── notebooks/
│   └── recommendation_algorithms.ipynb # Notebook Jupyter expliquant et testant les algorithmes
│
├── app/
│   ├── main.py               # Fichier principal de l'API FastAPI
│   └── recommender.py        # Fonctions Python implémentant les algorithmes de recommandation
│
├── venv/                     # Environnement virtuel Python (non inclus dans Git)
├── requirements.txt          # Liste des dépendances Python
└── README.md                 # Ce fichier de documentation

5. Technologies Utilisées
Langage : Python 3.x

Bibliothèques Python :

pandas : Manipulation et analyse de données.

numpy : Opérations numériques.

scikit-learn : Calcul de similarité (e.g., cosine_similarity).

FastAPI : Framework pour construire l'API web.

uvicorn : Serveur ASGI pour exécuter l'application FastAPI.

Outils de Développement :

Jupyter Notebook / Google Colab : Pour l'expérimentation et la documentation des algorithmes.

VS Code : Éditeur de code pour le développement de l'API.

Version Control : Git & GitHub (pour le partage du code).

6. Installation et Lancement
Suivez ces étapes pour configurer et lancer le projet localement.

6.1. Cloner le Dépôt (si vous clonez depuis GitHub)
git clone https://github.com/VotreNomUtilisateur/RecommandationEngineTG.git
cd RecommandationEngineTG

6.2. Créer et Activer l'Environnement Virtuel
Il est fortement recommandé d'utiliser un environnement virtuel pour gérer les dépendances.

python -m venv venv

Pour Windows (PowerShell) :

. .\venv\Scripts\activate

Pour macOS/Linux :

source venv/bin/activate

Vous devriez voir (venv) apparaître au début de votre ligne de commande, indiquant que l'environnement est activé.

6.3. Installer les Dépendances
Avec l'environnement virtuel activé, installez toutes les bibliothèques requises :

pip install fastapi uvicorn pandas scikit-learn numpy jupyter

Ou, si vous avez déjà généré requirements.txt :

pip install -r requirements.txt

6.4. Préparer les Données
Assurez-vous que les fichiers items.csv et users.csv sont bien placés dans le dossier data/ à la racine du projet.

6.5. Lancer l'API FastAPI
Depuis la racine du projet (RecommandationEngineTG/) et avec votre environnement virtuel activé, lancez le serveur Uvicorn :

uvicorn app.main:app --reload

L'API sera accessible à l'adresse http://127.0.0.1:8000. Le paramètre --reload permet à l'API de se recharger automatiquement à chaque modification de code.

7. Utilisation de l'API
Une fois l'API lancée, vous pouvez y accéder via votre navigateur ou des outils comme curl ou Postman.

Endpoint Principal :

GET / : Retourne un message de bienvenue.

Exemple : http://127.0.0.1:8000/

Endpoint de Recommandation :

GET /recommend/{user_id} : Retourne des recommandations pour un utilisateur spécifique. Remplacez {user_id} par l'ID de l'utilisateur (e.g., 1, 7, 10).

Exemple : http://127.0.0.1:8000/recommend/1

Exemple de Réponse JSON :
{
  "user_id": 1,
  "recommendations": [
    {
      "item_id": 103,
      "title": "The Dark Knight",
      "genre": "Action",
      "reason": "Aimé par un utilisateur similaire (ID: 2, Similarité: 0.82)"
    },
    {
      "item_id": 111,
      "title": "Gladiator",
      "genre": "Action",
      "reason": "Aimé par un utilisateur similaire (ID: 2, Similarité: 0.82)"
    },
    {
      "item_id": 106,
      "title": "Pulp Fiction",
      "genre": "Crime",
      "reason": "Similaire à vos préférences de genre (Science-Fiction)"
    },
    {
      "item_id": 110,
      "title": "Whiplash",
      "genre": "Drame",
      "reason": "Similaire à vos préférences de genre (Science-Fiction)"
    },
    {
      "item_id": 115,
      "title": "Parasite",
      "genre": "Thriller",
      "reason": "Similaire à vos préférences de genre (Science-Fiction)"
    }
  ]
}

8. Explication des Algorithmes (Jupyter Notebook)
Pour comprendre en détail l'implémentation des algorithmes de filtrage collaboratif et basé sur le contenu, ouvrez le Jupyter Notebook :

Assurez-vous que jupyter est installé (pip install jupyter).

Depuis la racine du projet (RecommandationEngineTG/) et avec l'environnement virtuel activé, lancez Jupyter :

jupyter notebook

Dans l'interface web de Jupyter, naviguez vers notebooks/recommendation_algorithms.ipynb et ouvrez-le. Vous pourrez exécuter les cellules et voir les étapes de calcul.

9. Perspectives d'Évolution (V2, V3)
Modèles plus complexes : Intégration de techniques avancées comme la factorisation matricielle (SVD, NMF) ou des réseaux de neurones.

Interface Utilisateur : Développer une interface web/mobile simple (avec React, VueJS, ou HTML/CSS/JS pur) pour interagir visuellement avec l'API.

Données enrichies : Prise en compte de notes explicites (sur 5 étoiles), historique de visionnage/écoute plus détaillé, ou données textuelles (descriptions, critiques).

Déploiement : Déployer l'API sur un service cloud comme Render, Heroku, ou Google Cloud Run.

Gestion des nouveaux utilisateurs : Stratégies pour recommander des items aux nouveaux utilisateurs (problème du "cold start").