giimport groq
import dotenv
import os
import retriever
dotenv.load_dotenv()
#
client = groq.Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)
# Génération de la réponse à partir du contexte reformulé et de la question
def generate_answer(question,context=""):
    context = retriever.getContext(question)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert in natural language processing and information retrieval. Your task is to generate an human like answer based on the context and the user's question."
            },
            {
                "role": "user",
                "content": f"Given the context: '{context}', and the question: '{question}', generate an answer. Return your answer as a Python string. answer precisely the user's question without any additional text or explanation."
            }
        ],
        model="llama-3.1-70b-versatile",
        temperature=0,
    )
    
    response = chat_completion.choices[0].message.content.strip()
    return response

# Example usage
question = "كم تبلغ تكلفة طلب الترخيص باستغلال مؤسسة مرتبة من الصنف الثالت"
print(retriever.find_keywords(question))
context = retriever.getContext(question)
print(context)
result = generate_answer(question)
print(result)
