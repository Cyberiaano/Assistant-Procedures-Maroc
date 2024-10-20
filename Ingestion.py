import pandas as pd
import cohere
from sqlalchemy import create_engine
from RAG import config_cohere_client
# Configuration de la connexion à la base de données
def config_db_connection():
    engine = create_engine('postgresql://postgres:votre_mot_de_passe@localhost:5432/postgres')
    return engine

# Lecture du fichier Excel
def read_excel_file(filepath):
    df = pd.read_excel(filepath)
    df.columns = df.columns.str.strip()  # Nettoyage des noms de colonnes
    return df

# Nettoyage des données
def clean_data(df):
    df = df[df['الطلب'].notna() & (df['الطلب'] != '')]  # Suppression des lignes NaN ou vides
    return df



# Fonction d'embedding via API Cohere
def get_embeddings(co, model, input_type, texts, batch_index):
    try:
        response = co.embed(texts=texts, model=model, input_type=input_type, embedding_types=['float'])
        if hasattr(response, 'embeddings') and response.embeddings.float_:
            return response.embeddings.float_
        else:
            print("Aucune donnée de vecteur retournée pour le lot", batch_index + 1)
            return None
    except Exception as e:
        print(f"Erreur lors de l'appel API pour le lot {batch_index + 1}: {e}")
        return None

# Traitement par lots et insertion des données dans la base de données
def process_and_store_data(df, engine, co, model, input_type, batch_size=90):
    total_batches = (len(df) // batch_size) + (len(df) % batch_size > 0)
    
    for batch_index in range(total_batches):
        start = batch_index * batch_size
        end = start + batch_size
        batch = df.iloc[start:end].copy()

        batch['vectors'] = get_embeddings(co, model, input_type, batch['الطلب'].tolist(), batch_index)
        batch['id'] = batch.index + 1  # Ajout d'une colonne ID

        # Renommer les colonnes pour correspondre aux noms de la base de données
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

        # Insertion dans la base de données
        batch_to_insert.to_sql('procedures_administratives', engine, if_exists='append', index=False)

# Enregistrement du DataFrame final dans un fichier Excel
def save_to_excel(df, output_filepath):
    df.to_excel(output_filepath, index=False)
    print("Résultats enregistrés dans le fichier Excel:", output_filepath)

# Fonction principale
def main():
    engine = config_db_connection()
    df = read_excel_file('ressources/procedures_administratives.xlsx')
    df = clean_data(df)
    
    # Configurer l'API Cohere
    co, model, input_type = config_cohere_client(api_key="NFumAAw2cT3lOvafIyPYNC4jg4y0JFmZ68KOnsnA", 
                                                 model="embed-multilingual-light-v3.0", 
                                                 input_type="search_query")
    
    process_and_store_data(df, engine, co, model, input_type, batch_size=90)
    save_to_excel(df, 'ressources/resultats_procedures_administratives.xlsx')

# Exécution du programme
if __name__ == "__main__":
    main()
