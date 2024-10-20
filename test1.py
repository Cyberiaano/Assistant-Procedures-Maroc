import pandas as pd
import cohere
import numpy as np
import ast
import time
from sqlalchemy import create_engine

# Configuration de la connexion à la base de données
engine = create_engine('postgresql://postgres:votre_mot_de_passe@localhost:5432/postgres')

# Lecture du fichier Excel
df = pd.read_excel('ressources/procedures_administratives.xlsx')

# Nettoyage des espaces dans les noms de colonnes
df.columns = df.columns.str.strip()

# Préparation des données pour le stockage dans la base de données
co = cohere.ClientV2(api_key="NFumAAw2cT3lOvafIyPYNC4jg4y0JFmZ68KOnsnA")
model = "embed-multilingual-light-v3.0"
input_type = "search_query"

# Supprimer les lignes avec des valeurs NaN ou vides dans la colonne 'الطلب'
df = df[df['الطلب'].notna() & (df['الطلب'] != '')]

# Traitement par lots
batch_size = 90
total_batches = (len(df) // batch_size) + (len(df) % batch_size > 0)

for batch_index in range(total_batches):
    start = batch_index * batch_size
    end = start + batch_size
    batch = df.iloc[start:end].copy()

    try:
        response = co.embed(texts=batch['الطلب'].tolist(), model=model, input_type=input_type, embedding_types=['float'])

        if hasattr(response, 'embeddings') and response.embeddings.float_:
            batch['vectors'] = response.embeddings.float_
        else:
            print("Aucune donnée de vecteur retournée.")
            batch['vectors'] = None

    except Exception as e:
        print(f"Erreur lors de l'appel API pour le lot {batch_index + 1}: {e}")
        batch['vectors'] = None

    # Création d'une colonne 'id' pour identifier chaque ligne
    batch['id'] = batch.index + 1
    # Renommer les colonnes du DataFrame pour correspondre aux noms dans la base de données
    batch_to_insert = batch.rename(columns={
        'الطلب': 'الطلب',
        'الوثائق المطلوبة': 'الوثائق_المطلوبة',
        'المصالح المكلفة بالاستلام': 'المصالح_المكلفة_بالاستلام',
        'المصالح المكلفة بالتسليم': 'المصالح_المكلفة_بالتسليم',
        'أجل معالجة الطلب وتسليم القرار الإداري': 'أجل_معالجة_الطلب_وتسليم_القرار_الإداري',
        'التكلفة': 'التكلفة',
        'النصوص القانونية': 'النصوص_القانونية',
        'vectors': 'embedding_request'
    })

    # Insérer les données dans la base de données
    batch_to_insert.to_sql('procedures_administratives', engine, if_exists='append', index=False)

    time.sleep(60)

# Enregistrement du résultat dans un fichier Excel
df.to_excel('ressources/resultats_procedures_administratives.xlsx', index=False)

# Affichage du message de confirmation
print("Données insérées avec succès dans la base de données.")


"""
CREATE TABLE procedures_administratives (
    id SERIAL PRIMARY KEY,
    الطلب TEXT,  -- The Request
    الوثائق_المطلوبة TEXT,  -- Required Documents
    المصالح_المكلفة_بالاستلام TEXT,  -- Departments Responsible for Reception
    المصالح_المكلفة_بالتسليم TEXT,  -- Departments Responsible for Delivery
    أجل_معالجة_الطلب_وتسليم_القرار_الإداري TEXT,  -- Processing Time
    التكلفة TEXT,  -- Cost
    النصوص_القانونية TEXT,  -- Legal Texts
    embedding_request VECTOR(384)  -- Embedding for الطلب (The Request)
);

"""