RecommandationEngineTG - Système de Recommandation de Films/Musiques (Simulé)
Ce projet est une démonstration simple d'un algorithme de recommandation basé sur les préférences des utilisateurs. Il met en œuvre des concepts fondamentaux du Machine Learning pour simuler un système de recommandation que l'on pourrait trouver sur des plateformes comme Netflix ou Spotify.

Objectif Principal
Construire un algorithme de recommandation basique en utilisant Python et des bibliothèques de ML, et le servir via une API web FastAPI.

Fonctionnalités
Base de Données Simulée : Utilisation de fichiers CSV pour les films/musiques et les préférences des utilisateurs.

Algorithme de Recommandation :

Filtrage Collaboratif basé sur la similarité des utilisateurs.

Filtrage basé sur le Contenu en fonction des genres.

Combinaison des deux approches pour des recommandations plus robustes.

API REST : Un endpoint /recommend/{user_id} retourne des recommandations pour un utilisateur donné.

Technologies Utilisées
Python 3.x

pandas : Manipulation de données.

numpy : Opérations numériques.

scikit-learn : Calcul de similarité (cosine_similarity).

FastAPI : Framework pour l'API.

uvicorn : Serveur ASGI.

Installation et Lancement
Préparer les fichiers :

Créez un dossier RecommandationEngineTG/.

Créez les sous-dossiers data/ et app/.

Créez et placez tous les fichiers de ce projet dans les dossiers appropriés.

Installer les dépendances :

pip install -r requirements.txt

Lancer l'API :

uvicorn app.main:app --reload

L'API sera disponible à l'adresse http://127.0.0.1:8000.

Utiliser l'interface Web :

Ouvrez le fichier index.html dans votre navigateur.
