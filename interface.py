import streamlit as st
import generator
# Titre principal de l'interface
st.markdown("<h1 style='text-align: center; color: #4B9CD3;'>استخدم الذكاء الاصطناعي</h1>", unsafe_allow_html=True)

# Section centrale de l'interface
st.write("### :  اهلا بك كيف يمكنني مساعدتك في اجراءاتك الادارية")

# Champ de saisie pour les questions
user_input = st.text_input("اكتب سؤالك هنا", "", placeholder="على سبيل المثال: كم تبلغ تكلفة طلب الترخيص باستغلال مؤسسة مرتبة من الصنف الثالث؟")

# Bouton pour envoyer la question
st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: #4B9CD3;
        color: white;
        border-radius: 10px;
        height: 40px;
        width: 100px;
        font-size: 16px;
    }
    div.stButton > button:hover {
        background-color: #357ABD;
    }
    </style>
    """, unsafe_allow_html=True)

if st.button("Envoyer"):
    # Placeholder pour la réponse de l'IA
    st.write("**Vous** : " + user_input)
    réponse = generator.generate_answer(user_input)
    st.write("**IA** : " + réponse)
