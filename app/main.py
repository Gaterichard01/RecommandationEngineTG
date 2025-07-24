# app/main.py

from fastapi import FastAPI
# Le '.' indique que 'recommender' est dans le même package (dossier 'app')
from .recommender import get_recommendations

app = FastAPI(
    title="API Moteur de RecommandationTG",
    description="API simple de recommandation de films/musiques basée sur le filtrage collaboratif et par contenu.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Moteur de RecommandationTG ! Rendez-vous sur /recommend/{user_id} pour des recommandations."}

@app.get("/recommend/{user_id}")
def recommend(user_id: int):
    """
    Retourne une liste de recommandations de films/musiques pour un utilisateur donné.
    """
    recommendations = get_recommendations(user_id)
    if not recommendations:
        return {"user_id": user_id, "message": "Aucune recommandation trouvée pour cet utilisateur ou utilisateur inconnu.", "recommendations": []}
    return {"user_id": user_id, "recommendations": recommendations}