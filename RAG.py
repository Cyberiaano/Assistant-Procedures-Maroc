import os
import numpy as np
from sqlalchemy import create_engine, text
import cohere
import dotenv 
dotenv.load_dotenv()
# Configuration
api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise ValueError("COHERE_API_KEY environment variable is not set. Please set it and try again.")

model = "embed-multilingual-light-v3.0"
input_type = "search_query"

def config_cohere_client(api_key=api_key, model=model, input_type=input_type):
    try:
        co = cohere.ClientV2(api_key=api_key)
        return co, model, input_type
    except cohere.core.api_error.ApiError as e:
        print(f"Error initializing Cohere client: {e}")
        raise

def config_db_connection():
    db_url = os.environ.get("DATABASE_URL", 'postgresql://postgres:votre_mot_de_passe@localhost:5432/postgres')
    return create_engine(db_url)

try:
    engine = config_db_connection()
    co, model, input_type = config_cohere_client()
except Exception as e:
    print(f"Error during configuration: {e}")
    raise

def get_text_embedding(text, co=co, model=model, input_type=input_type):
    response = co.embed(texts=[text], model=model, input_type=input_type, embedding_types=['float'])
    return response.embeddings.float_[0] if hasattr(response, 'embeddings') and response.embeddings.float_ else None

def semanticSearch(text_to_search, co=co, model=model, input_type=input_type, engine=engine):
    embedding = get_text_embedding(text_to_search)
    if embedding is None:
        print("Erreur lors de la récupération de l'embedding.")
        return None

    query = """
        SELECT id
        FROM procedures_administratives
        ORDER BY embedding_request <-> CAST(:embedding AS vector)
        LIMIT 1;
    """

    with engine.connect() as connection:
        result = connection.execute(text(query), {"embedding": embedding})
        similar_id = result.fetchone()

    return similar_id[0] if similar_id else None

def get_info_by_id(id, column_name, engine=engine):
    query = f"""
        SELECT "{column_name}"
        FROM procedures_administratives
        WHERE id = :id;
    """

    with engine.connect() as connection:
        result = connection.execute(text(query), {"id": id})
        info = result.fetchone()

    return info[0] if info else None

# Simplified functions using get_info_by_id
get_processing_time_by_id = lambda id: get_info_by_id(id, "أجل_معالجة_الطلب_وتسليم_القرار_الإداري")
get_request_by_id = lambda id: get_info_by_id(id, "الطلب")
get_reception_organ_by_id = lambda id: get_info_by_id(id, "المصالح_المكلفة_بالاستلام")
get_delivery_organ_by_id = lambda id: get_info_by_id(id, "المصالح_المكلفة_بالتسليم")
get_cost_by_id = lambda id: get_info_by_id(id, "التكلفة")
get_legal_texts_by_id = lambda id: get_info_by_id(id, "النصوص_القانونية")
get_required_documents_by_id = lambda id: get_info_by_id(id, "الوثائق_المطلوبة")

def main():
    try:
        text_to_search = "كم يستغرق معالجة طلب الترخيص باستغلال مؤسسة مرتبة من الصنف الثالث"
        similar_id = semanticSearch(text_to_search)
        
        if similar_id is not None:
            processing_time = get_processing_time_by_id(similar_id)
            print(f"L'ID du vecteur similaire est : {similar_id}")
            print(f"Le temps de traitement est : {processing_time}")
        else:
            print("Aucun vecteur similaire trouvé.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()