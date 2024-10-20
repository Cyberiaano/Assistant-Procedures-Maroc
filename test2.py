import pandas as pd
import cohere
import numpy as np
import ast
# Lecture du fichier Excel
df = pd.read_excel('ressources/procedures_administratives.xlsx')

# Ne conserver que les 10 premiers enregistrements
df = df.head(10)

# Préparation des données pour le stockage dans la base de données
co = cohere.ClientV2(api_key="NFumAAw2cT3lOvafIyPYNC4jg4y0JFmZ68KOnsnA")
model = "embed-multilingual-light-v3.0"  # Remplacez par un modèle adapté si nécessaire
input_type = "search_query"

# Supprimer les lignes avec des valeurs NaN ou vides dans la colonne 'الطلب'
df = df[df['الطلب'].notna() & (df['الطلب'] != '')]

# Affichage des premières lignes pour vérifier
print("Exemples de données dans la colonne 'الطلب':")
print(df['الطلب'].head())

# Traitement des données sans traitement par lots
try:
    # Envoyer tous les textes à l'API en une seule fois
    response = co.embed(texts=df['الطلب'].tolist(), model=model, input_type=input_type, embedding_types=['float'])

    print(f"Réponse de l'API : {response}")

    # Vérifier que la réponse contient des embeddings et extraire les données
    if hasattr(response, 'embeddings') and response.embeddings.float_:
        df['vectors'] = response.embeddings.float_  # Extraire les embeddings float
    else:
        print("Aucune donnée de vecteur retournée.")
        df['vectors'] = None  # Ou d'autres valeurs par défaut

except Exception as e:
    print(f"Erreur lors de l'appel API : {e}")
    df['vectors'] = None  # Ou d'autres valeurs par défaut

# Création d'une colonne 'id' pour identifier chaque ligne
df['id'] = df.index + 1
df['vectors'] = df['vectors'].apply(lambda x: np.array(ast.literal_eval(x), dtype=float))
# Sélectionner uniquement les colonnes souhaitées
result_df = df[['id', 'الطلب', 'vectors']]

# Enregistrement du résultat dans un fichier Excel
result_df.to_excel('ressources/resultats_procedures_administratives.xlsx', index=False)

# Affichage des premières lignes pour vérifier
print(type(result_df['vectors'][0]))
