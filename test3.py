import groq
import dotenv
import os
import retriever
dotenv.load_dotenv()

client = groq.Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

# Reformuler le contexte pour augmenter la pertinence des réponses à partir de la question
def reformulate_context(question,context=""):
    context = retriever.getContext(question)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert in natural language processing and information retrieval. Your task is to reformulate the context provided based on the user's question to pass it to answer generator."
            },
            {
                "role": "user",
                "content": f"Given the context: '{context}', and the question: '{question}', reformulate the context to make it more relevant to the question. Return your answer as a Python string without any additional text or explanation."
            }
        ],
        model="llama-3.1-70b-versatile",
        temperature=1,
    )
    
    response = chat_completion.choices[0].message.content.strip()
    return response
