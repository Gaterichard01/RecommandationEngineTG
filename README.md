L'écosystème de Recommandation de Films

c'est un projet complet d'application de recommandation de films, composé d'une API backend et d'une interface web frontend. Il permet aux utilisateurs de gérer leurs favoris et de recevoir des recommandations personnalisées basées sur leurs préférences.

 ## Vue d'ensemble des fonctionnalités

  * **Authentification sécurisée** : Inscription et connexion des utilisateurs avec gestion des mots de passe hachés.
  * **Recherche de films** : Un moteur de recherche puissant qui utilise l'API TMDB pour trouver des films pertinents.
  * **Gestion des favoris** : Les utilisateurs peuvent ajouter ou retirer des films de leur liste de favoris, stockée sur Firestore.
  * **Recommandations intelligentes** : Des suggestions de films sont générées en se basant sur la liste de favoris de l'utilisateur. Si la liste est vide, les films populaires sont affichés par défaut.
  * **Détails enrichis** : Les cartes de films et la modale de détails affichent le résumé, la date de sortie, la note, et surtout, les plateformes de streaming disponibles en France.
  * **Interface utilisateur moderne** : Une interface utilisateur élégante, réactive et en une seule page (SPA) qui propose un mode sombre et un mode clair.

## Stack Technique

Ce projet est conçu en deux parties distinctes :

### 1\. Backend (API)

  * **Langage** : Python 3.10+
  * **Framework** : **FastAPI** pour construire l'API.
  * **Base de données** : **Google Cloud Firestore** pour stocker les informations des utilisateurs et leurs listes de favoris.
  * **Source de données** : **The Movie Database (TMDB)** pour les informations sur les films.
  * **Dépendances** : uvicorn, python-dotenv, firebase-admin, pydantic, requests, httpx.

### 2\. Frontend (Interface Web)

  * **Langages** : HTML5, CSS3, JavaScript (Vanilla JS)
  * **Framework CSS** : **Tailwind CSS** pour un design rapide et un style personnalisable.
  * **Librairie d'icônes** : **Font Awesome** pour les icônes de cœurs, d'étoiles, etc.
  * **Type d'application** : Single Page Application (SPA).


##  Installation et Lancement

Pour lancer l'ensemble de l'écosystème FilmPulse, suivez ces étapes :

### Étape 1 : Configuration de l'API Backend

1.  **Clonez le dépôt** :

  
    git clone <URL_DU_DÉPÔT>
    cd <NOM_DU_DOSSIER>
   

2.  **Créez un environnement virtuel et installez les dépendances** :

   
    python -m venv venv
    source venv/bin/activate  # Pour macOS/Linux
    venv\Scripts\activate     # Pour Windows
    pip install -r requirements.txt


     Si vous n'avez pas de fichier requirements.txt, vous pouvez l'installer avec pip install fastapi uvicorn python-dotenv firebase-admin pydantic requests httpx.

3.  **Configurez les clés d'API** :

      * Créez un fichier .env à la racine de votre projet avec votre clé TMDB :
      
        TMDB_API_KEY=votre_cle_api_tmdb
      
      * Téléchargez votre clé de compte de service Firebase (au format JSON) et placez-la à la racine du dossier de l'API. Assurez-vous que son nom corresponde à celui configuré dans le code.

4.  **Lancez le serveur API** :


    uvicorn main:app --reload


    Le backend sera accessible sur `http://127.0.0.1:8000`.

### Étape 2 : Lancement de l'Interface Frontend

1.  **Ouvrez le fichier HTML** :
      * Ouvrez le fichier index.html (ou tout autre nom que vous avez donné) dans votre navigateur web. Vous n'avez pas besoin d'un serveur local pour cela, car tout est géré par JavaScript.
      * **Important** : Si vous n'utilisez pas http://127.0.0.1:8000 pour l'API, vous devrez modifier la variable BASE_API_URL dans le code JavaScript du fichier HTML pour qu'elle pointe vers l'URL correcte.

Une documentation interactive de l'API est automatiquement générée et accessible à l'adresse suivante lorsque le backend est en cours d'exécution :
http://127.0.0.1:8000/docs

Les contributions, rapports de bugs et suggestions d'amélioration sont les bienvenus. N'hésitez pas à ouvrir une `issue` ou à soumettre une `pull request`.

## 📜 Licence

Ce projet est distribué sous la licence MIT.
