import groq
import dotenv
import os
import ast
from RAG import semanticSearch
from RAG import get_processing_time_by_id, get_cost_by_id, get_legal_texts_by_id, get_request_by_id,get_delivery_organ_by_id, get_reception_organ_by_id, get_required_documents_by_id

dotenv.load_dotenv()
client = groq.Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

list_of_keywords = ["الوثائق المطلوبة", "المصالح المكلفة بالاستلام", "المصالح المكلفة بالتسليم", "أجل معالجة الطلب وتسليم القرار الإداري", "التكلفة", "النصوص القانونية"]

def find_keywords(question, list_of_keywords=list_of_keywords):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert in natural language processing and information retrieval. Your task is to identify the most relevant keywords from a predefined list based on the user's question."
            },
            {
                "role": "user",
                "content": f"Given the question: '{question}', select only the most relevant keywords from this list: {list_of_keywords}. Return your answer as a Python list containing only the selected keywords, without any additional text or explanation."
            }
        ],
        model="llama-3.1-70b-versatile",
        temperature=0,
    )
    
    response = chat_completion.choices[0].message.content.strip()
    
    try:
        # Attempt to parse the response as a Python list
        keywords = ast.literal_eval(response)
        # Ensure all returned keywords are in the original list
        keywords = [kw for kw in keywords if kw in list_of_keywords]
        return keywords
    except:
        # If parsing fails, fall back to a simple split and filter
        words = response.replace('[', '').replace(']', '').replace('"', '').replace("'", "").split(',')
        return [word.strip() for word in words if word.strip() in list_of_keywords]
    
# Récupération du contexte général de la question
def getContext(question):
    list_keywords = find_keywords(question)
    id = semanticSearch(question)
    
    context_dict = {}

    # Parcours des mots-clés pour extraire les informations
    for keyword in list_keywords:
        if keyword == "الوثائق المطلوبة":
            context_dict["الوثائق المطلوبة"] = get_required_documents_by_id(id)
        elif keyword == "المصالح المكلفة بالاستلام":
            context_dict["المصالح المكلفة بالاستلام"] = get_reception_organ_by_id(id)
        elif keyword == "المصالح المكلفة بالتسليم":
            context_dict["المصالح المكلفة بالتسليم"] = get_delivery_organ_by_id(id)
        elif keyword == "أجل معالجة الطلب وتسليم القرار الإداري":
            context_dict["أجل معالجة الطلب وتسليم القرار الإداري"] = get_processing_time_by_id(id)
        elif keyword == "التكلفة":
            context_dict["التكلفة"] = get_cost_by_id(id)
        elif keyword == "النصوص القانونية":
            context_dict["النصوص القانونية"] = get_legal_texts_by_id(id)
    
    # La demande est incluse indépendamment des mots-clés
    context_dict["الطلب"] = get_request_by_id(id)
    
    # Création du contexte en arabe en construisant dynamiquement la chaîne à partir du dictionnaire
    context = ",\n".join([f'"{key}": "{value}"' for key, value in context_dict.items()])

    # Retour du contexte final
    return context


