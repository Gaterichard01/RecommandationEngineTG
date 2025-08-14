# Importations des modules nécessaires
import os
import asyncio
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import hashlib
import time
import httpx # Ajout de la bibliothèque httpx
from dotenv import load_dotenv

# --- Importations spécifiques à Firebase ---
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Charger les variables d'environnement
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    raise RuntimeError("TMDB_API_KEY non trouvée dans les variables d'environnement.")

# --- Configuration de Firebase ---
SERVICE_ACCOUNT_KEY_FILE = "mon-app-de-films-firebase-adminsdk-fbsvc-1c4e560702.json"

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    service_account_path = os.path.join(BASE_DIR, SERVICE_ACCOUNT_KEY_FILE)
    
    if not os.path.exists(service_account_path):
        raise FileNotFoundError(f"Le fichier de clé de service n'a pas été trouvé à l'emplacement : {service_account_path}")
        
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase Admin SDK initialisé avec succès.")
except FileNotFoundError as e:
    raise RuntimeError(f"Erreur: {e}")
except Exception as e:
    raise RuntimeError(f"Erreur d'initialisation de Firebase: {e}. As-tu bien configuré ton fichier de clé de service ?")


# Initialisation de l'API FastAPI
app = FastAPI(
    title="API de Recommandation de Films",
    description="Une API complète pour la gestion des films, des utilisateurs et des favoris avec Firestore."
)

# --- ENDPOINT DE BASE ---
@app.get("/")
def read_root():
    """
    Endpoint de base pour tester que l'API est fonctionnelle.
    """
    return {"message": "Bienvenue sur l'API de Recommandation de Films !"}


# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration de l'API de TMDB
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Modèles Pydantic pour la validation des données
class UserCredentials(BaseModel):
    email: str
    password: str

class UserRegistration(UserCredentials):
    username: str

class FavoriteMovie(BaseModel):
    user_id: str
    movie_id: int

# Fonctions utilitaires
def hash_password(password: str):
    """Hache le mot de passe pour le stockage sécurisé."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password_hash: str, provided_password: str):
    """Vérifie si le mot de passe fourni correspond au hachage stocké."""
    return stored_password_hash == hash_password(provided_password)

def fetch_with_retry(url: str, max_retries: int = 5, delay_seconds: int = 5) -> requests.Response:
    """Logique de retentative pour les requêtes API."""
    for attempt in range(max_retries):
        try:
            print(f"Tentative {attempt + 1} de {max_retries} pour se connecter à {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            print("Requête réussie !")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion lors de la tentative {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"En attente de {delay_seconds} secondes avant de réessayer...")
                time.sleep(delay_seconds)
            else:
                print("Nombre maximum de retentatives atteint. Abandon.")
                raise HTTPException(status_code=500, detail=f"Erreur lors de la communication avec l'API TMDB: {e}")

# Fonctions asynchrones pour les appels à TMDB
async def get_movie_details(movie_id: int):
    """Récupère les détails d'un seul film de manière asynchrone."""
    tmdb_url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=fr-FR"
    try:
        response = await asyncio.to_thread(fetch_with_retry, tmdb_url)
        movie_details = response.json()
        return {
            "id": movie_details.get("id"),
            "title": movie_details.get("title"),
            "poster_path": f"https://image.tmdb.org/t/p/w500{movie_details.get('poster_path')}" if movie_details.get('poster_path') else None,
            "release_date": movie_details.get("release_date")
        }
    except HTTPException:
        return None

async def get_watch_providers(movie_id: int) -> Dict:
    """
    Récupère les fournisseurs de streaming (payants et gratuits)
    pour un film et une région donnés.
    """
    providers_url = f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers?api_key={API_KEY}"
    try:
        response = await asyncio.to_thread(fetch_with_retry, providers_url)
        providers_data = response.json()
        
        if "FR" in providers_data.get("results", {}):
            fr_providers = providers_data["results"]["FR"]
            return {
                "link": fr_providers.get("link"),
                "flatrate": fr_providers.get("flatrate", []),
                "free": fr_providers.get("free", [])
            }
        else:
            return {"link": None, "flatrate": [], "free": []}
            
    except HTTPException:
        return {"link": None, "flatrate": [], "free": []}

async def get_movie_recommendations(movie_id: int):
    """Récupère les recommandations pour un film donné de manière asynchrone."""
    recommend_url = f"{TMDB_BASE_URL}/movie/{movie_id}/recommendations?api_key={API_KEY}&language=fr-FR"
    try:
        response = await asyncio.to_thread(fetch_with_retry, recommend_url)
        data = response.json()
        return data.get("results", [])
    except HTTPException:
        return []

# --- Endpoints de l'API ---

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegistration):
    """Enregistre un nouvel utilisateur dans la collection `users` de Firestore."""
    users_ref = db.collection("users")
    query_result = users_ref.where("email", "==", user_data.email).limit(1).get()

    if query_result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est déjà enregistré."
        )

    new_user_data = {
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password)
    }
    user_doc_ref = users_ref.document()
    user_doc_ref.set(new_user_data)
    
    favorites_ref = db.collection("user_favorites").document(user_doc_ref.id)
    favorites_ref.set({"favorites": []})

    return {"user_id": user_doc_ref.id, "username": user_data.username}

@app.post("/login")
async def login(credentials: UserCredentials):
    """Connecte un utilisateur en vérifiant ses identifiants dans Firestore."""
    users_ref = db.collection("users")
    query_result = users_ref.where("email", "==", credentials.email).limit(1).get()

    if not query_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect."
        )

    user_doc = query_result[0]
    user_info = user_doc.to_dict()

    if user_info and verify_password(user_info["password_hash"], credentials.password):
        return {"user_id": user_doc.id, "username": user_info["username"]}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou mot de passe incorrect."
    )

@app.get("/search/{query}")
async def search_movies(query: str):
    """
    Recherche des films via l'API TMDB et y ajoute les plateformes de streaming
    disponibles en France.
    """
    search_url = f"{TMDB_BASE_URL}/search/movie?api_key={API_KEY}&query={query}&language=fr-FR"
    try:
        response = await asyncio.to_thread(fetch_with_retry, search_url)
        data = response.json()
        
        movie_ids = [movie["id"] for movie in data.get("results", [])]
        watch_provider_tasks = [get_watch_providers(movie_id) for movie_id in movie_ids]
        providers_results = await asyncio.gather(*watch_provider_tasks)
        
        results = []
        for i, movie in enumerate(data.get("results", [])):
            movie_details = {
                "id": movie["id"],
                "title": movie["title"],
                "overview": movie.get("overview", ""),
                "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
                "release_date": movie.get("release_date", "N/A"),
                "watch_providers": providers_results[i]
            }
            results.append(movie_details)
        
        return {"results": results}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la communication avec l'API TMDB: {e}")

# --- NOUVEL ENDPOINT AJOUTÉ : C'est celui-là qui manquait ! ---
@app.get("/movie/{movie_id}")
async def get_movie_with_details(movie_id: int):
    """
    Récupère les détails d'un film, y compris les plateformes de streaming,
    et les recommandations.
    """
    async with httpx.AsyncClient() as client:
        # Requête pour les détails du film
        movie_details_url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=fr-FR"
        try:
            movie_response = await client.get(movie_details_url)
            movie_response.raise_for_status()
            movie_details = movie_response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Film non trouvé, bro.")
            raise HTTPException(status_code=e.response.status_code, detail=f"Erreur de l'API TMDb : {e}")

        # Requête pour les plateformes de streaming
        providers_url = f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers?api_key={API_KEY}"
        try:
            providers_response = await client.get(providers_url)
            providers_response.raise_for_status()
            providers_data = providers_response.json()
            providers_france = providers_data.get('results', {}).get('FR')
            movie_details['watch_providers'] = providers_france
        except httpx.HTTPStatusError:
            movie_details['watch_providers'] = None
        
        return movie_details


@app.post("/favorites")
async def manage_favorites(favorite_data: FavoriteMovie):
    """
    Ajoute ou retire un film des favoris de l'utilisateur dans Firestore.
    Utilise une transaction pour garantir l'atomicité.
    """
    user_id = favorite_data.user_id
    movie_id = favorite_data.movie_id
    favorites_doc_ref = db.collection("user_favorites").document(user_id)

    @firestore.transactional
    def update_favorites_transaction(transaction, doc_ref):
        favorites_doc = doc_ref.get(transaction=transaction)
        if not favorites_doc.exists:
            transaction.set(doc_ref, {"favorites": [movie_id]})
            return {"status": "ajouté", "movie_id": movie_id, "user_id": user_id}

        current_favorites = favorites_doc.to_dict().get("favorites", [])
        if movie_id in current_favorites:
            current_favorites.remove(movie_id)
            transaction.update(doc_ref, {"favorites": current_favorites})
            return {"status": "retiré", "movie_id": movie_id, "user_id": user_id}
        else:
            current_favorites.append(movie_id)
            transaction.update(doc_ref, {"favorites": current_favorites})
            return {"status": "ajouté", "movie_id": movie_id, "user_id": user_id}

    transaction = db.transaction()
    try:
        result = await asyncio.to_thread(update_favorites_transaction, transaction, favorites_doc_ref)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de transaction Firestore : {e}")


@app.get("/favorites/{user_id}")
async def get_favorites(user_id: str):
    """
    Récupère la liste des films favoris d'un utilisateur depuis Firestore,
    puis récupère les détails de chaque film via l'API TMDB de manière concurrente.
    """
    favorites_doc_ref = db.collection("user_favorites").document(user_id)
    favorites_doc = await asyncio.to_thread(favorites_doc_ref.get)

    if not favorites_doc.exists:
        return {"favorites": []}

    favorite_ids = favorites_doc.to_dict().get("favorites", [])
    
    tasks = [get_movie_details(movie_id) for movie_id in favorite_ids]
    favorite_movies_data = [movie for movie in await asyncio.gather(*tasks) if movie]

    providers_tasks = [get_watch_providers(movie["id"]) for movie in favorite_movies_data]
    providers_results = await asyncio.gather(*providers_tasks)
    
    for i, movie in enumerate(favorite_movies_data):
        movie["watch_providers"] = providers_results[i]

    return {"favorites": favorite_movies_data}


@app.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Récupère le profil d'un utilisateur depuis Firestore en utilisant son ID."""
    user_doc_ref = db.collection("users").document(user_id)
    user_doc = await asyncio.to_thread(user_doc_ref.get)
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    user_data = user_doc.to_dict()
    return {
        "user_id": user_doc.id,
        "username": user_data.get("username"),
        "email": user_data.get("email")
    }

@app.get("/recommend/{user_id}")
async def get_recommendations(user_id: str):
    """
    Recommande des films en fonction des favoris de l'utilisateur stockés dans Firestore
    ou des films populaires si l'utilisateur n'a pas de favoris.
    """
    favorites_doc_ref = db.collection("user_favorites").document(user_id)
    favorites_doc = await asyncio.to_thread(favorites_doc_ref.get)
    favorite_ids = favorites_doc.to_dict().get("favorites", []) if favorites_doc.exists else []
    
    recommended_movies_data = {}

    if not favorite_ids:
        popular_url = f"{TMDB_BASE_URL}/movie/popular?api_key={API_KEY}&language=fr-FR"
        try:
            response = await asyncio.to_thread(fetch_with_retry, popular_url)
            data = response.json()
            for movie in data.get("results", []):
                recommended_movies_data[movie["id"]] = movie
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur de l'API TMDB: {e}")
    else:
        tasks = [get_movie_recommendations(movie_id) for movie_id in favorite_ids]
        recommendation_lists = await asyncio.gather(*tasks)
        
        for rec_list in recommendation_lists:
            for movie in rec_list:
                recommended_movies_data[movie["id"]] = movie
    
    movie_ids = list(recommended_movies_data.keys())
    providers_tasks = [get_watch_providers(movie_id) for movie_id in movie_ids]
    providers_results = await asyncio.gather(*providers_tasks)
    
    results = []
    for i, movie_id in enumerate(movie_ids):
        movie = recommended_movies_data[movie_id]
        results.append({
            "id": movie["id"],
            "title": movie["title"],
            "overview": movie.get("overview", ""),
            "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
            "release_date": movie.get("release_date", "N/A"),
            "watch_providers": providers_results[i]
        })
    
    return {"recommendations": results}

@app.get("/watch_providers/{movie_id}")
async def get_providers_for_movie(movie_id: int):
    """
    Endpoint pour récupérer les fournisseurs de streaming pour un film spécifique
    en France.
    """
    providers = await get_watch_providers(movie_id)
    return {"watch_providers": providers}


# Point d'entrée pour lancer l'application avec uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
