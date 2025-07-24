# app/recommender.py

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# --- Chargement et préparation des données ---
try:
    items_df = pd.read_csv('data/items.csv') # Le chemin est relatif à l'endroit où l'API sera lancée
    users_df = pd.read_csv('data/users.csv')
except FileNotFoundError:
    # Gérer le cas où les fichiers ne sont pas trouvés (utile pour le déploiement ou si le chemin change)
    print("Erreur : Les fichiers data/items.csv ou data/users.csv n'ont pas été trouvés.")
    print("Veuillez vous assurer que le dossier 'data' est au même niveau que le dossier 'app'.")
    # Créer des DataFrames vides ou de démonstration pour éviter une erreur fatale
    items_df = pd.DataFrame(columns=['item_id', 'title', 'genre'])
    users_df = pd.DataFrame(columns=['user_id', 'item_id', 'liked'])


# Création de la matrice de user-item
# Utiliser un try-except pour le cas où users_df est vide après un FileNotFoundError
try:
    user_item_matrix = users_df.pivot_table(index='user_id', columns='item_id', values='liked').fillna(0)
except Exception as e:
    print(f"Erreur lors de la création de la matrice user-item : {e}")
    user_item_matrix = pd.DataFrame() # DataFrame vide si erreur

# Calcul de la similarité entre utilisateurs (si la matrice n'est pas vide)
user_similarity_df = pd.DataFrame() # Initialisation par défaut
if not user_item_matrix.empty:
    user_similarity_df = pd.DataFrame(cosine_similarity(user_item_matrix), index=user_item_matrix.index, columns=user_item_matrix.index)

# --- Fonctions de Recommandation ---

def recommend_by_user_similarity(target_user_id, num_recommendations=5):
    """
    Recommande des items à un utilisateur cible en utilisant le filtrage collaboratif.
    """
    if user_item_matrix.empty or target_user_id not in user_item_matrix.index:
        return []

    # Obtenir les utilisateurs similaires, exclure l'utilisateur cible lui-même
    similar_users = user_similarity_df[target_user_id].sort_values(ascending=False)
    similar_users = similar_users.drop(target_user_id, errors='ignore') # Exclure l'utilisateur lui-même

    # Identifier les items déjà aimés par l'utilisateur cible
    user_liked_items = user_item_matrix.loc[target_user_id][user_item_matrix.loc[target_user_id] == 1].index

    recommendations = []
    for similar_user_id, similarity_score in similar_users.items():
        if similarity_score > 0:
            similar_user_liked_items = user_item_matrix.loc[similar_user_id][user_item_matrix.loc[similar_user_id] == 1].index
            new_recommendations = [item for item in similar_user_liked_items if item not in user_liked_items]

            for item_id in new_recommendations:
                item_info = items_df[items_df['item_id'] == item_id]
                if not item_info.empty:
                    item_info = item_info.iloc[0]
                    recommendations.append({
                        'item_id': item_id,
                        'title': item_info['title'],
                        'genre': item_info['genre'],
                        'reason': f"Aimé par un utilisateur similaire (ID: {similar_user_id}, Similarité: {similarity_score:.2f})"
                    })
        if len(recommendations) >= num_recommendations * 2: # Prendre plus pour filtrer les doublons
            break

    unique_recommendations = pd.DataFrame(recommendations).drop_duplicates(subset=['item_id']).head(num_recommendations)
    return unique_recommendations.to_dict(orient='records')

def recommend_by_content(target_user_id, num_recommendations=5):
    """
    Recommande des items à un utilisateur cible en utilisant le filtrage basé sur le contenu (genres).
    """
    if users_df.empty or items_df.empty or target_user_id not in users_df['user_id'].values:
        return []

    user_liked_items_ids = users_df[(users_df['user_id'] == target_user_id) & (users_df['liked'] == 1)]['item_id'].tolist()

    if not user_liked_items_ids:
        return []

    liked_items_info = items_df[items_df['item_id'].isin(user_liked_items_ids)]
    preferred_genres = liked_items_info['genre'].unique()

    unliked_items = items_df[~items_df['item_id'].isin(user_liked_items_ids)]

    recommendations = []
    for genre in preferred_genres:
        genre_items = unliked_items[unliked_items['genre'] == genre]
        for _, row in genre_items.iterrows():
            if len(recommendations) < num_recommendations:
                recommendations.append({
                    'item_id': row['item_id'],
                    'title': row['title'],
                    'genre': row['genre'],
                    'reason': f"Similaire à vos préférences de genre ({genre})"
                })
            else:
                break
        if len(recommendations) >= num_recommendations:
            break

    return recommendations

def get_recommendations(target_user_id: int, num_recommendations_total: int = 5):
    """
    Combine les recommandations du filtrage collaboratif et du filtrage basé sur le contenu.
    C'est la fonction principale qui sera appelée par l'API.
    """
    # S'assurer que les dataframes ne sont pas vides avant de tenter des opérations
    if user_item_matrix.empty or items_df.empty or users_df.empty:
        return [] # Retourne une liste vide si les données ne sont pas chargées

    collaborative_recommendations = recommend_by_user_similarity(target_user_id, num_recommendations=num_recommendations_total * 2)
    content_based_recommendations = recommend_by_content(target_user_id, num_recommendations=num_recommendations_total * 2)

    combined_recs = []
    seen_item_ids = set()

    for rec in collaborative_recommendations:
        if rec['item_id'] not in seen_item_ids:
            combined_recs.append(rec)
            seen_item_ids.add(rec['item_id'])

    for rec in content_based_recommendations:
        if rec['item_id'] not in seen_item_ids:
            combined_recs.append(rec)
            seen_item_ids.add(rec['item_id'])

    user_liked_items_ids = users_df[(users_df['user_id'] == target_user_id) & (users_df['liked'] == 1)]['item_id'].tolist()
    final_recommendations = [rec for rec in combined_recs if rec['item_id'] not in user_liked_items_ids]

    return final_recommendations[:num_recommendations_total]

# Exemple d'appel pour vérifier (non utilisé par l'API, juste pour tester le fichier)
if __name__ == "__main__":
    print("Test des fonctions de recommandation dans recommender.py")
    recs = get_recommendations(1)
    print(f"Recommandations pour l'utilisateur 1: {recs}")
    recs = get_recommendations(10)
    print(f"Recommandations pour l'utilisateur 10: {recs}")
    recs = get_recommendations(999) # Utilisateur inexistant
    print(f"Recommandations pour l'utilisateur 999: {recs}")