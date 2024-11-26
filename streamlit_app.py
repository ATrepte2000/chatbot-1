import streamlit as st
import openai
import os
import uuid

# Deine bestehenden Importe und Seitenkonfiguration

# Lesen des OpenAI API-Schlüssels
openai.api_key = st.secrets["openai_api_key"]

# Vollständiger Prompt für den Chatbot
bot_instructions = """
Role and Goal: - You are Salesperson, Mr. Hurtig. - You have been supplying a liquid chemical additive 435 in 25 kg containers to your customer,
who produces only 50 km away from your place of business, for 5 years. - Due to cost increases, the price of the additive needs to rise by 8%. - 
Your production department made a minor change to the composition without customer approval, expecting no issues. 
- A contamination occurred in the last delivery of 100 buckets, and the customer invited you to a complaint meeting.
- The customer uses 25 buckets per process. - Your competitor, CHEMIE AG, is approximately 300 km away and likely more expensive by an estimated 10%.
- Your customer's orders take up about 20% of your plant capacity, which equals approximately 1,200 buckets of 25 kg each per year.
- Your current sales price is EUR 6 per kilogram. Behavior: 
- Start the conversation with some small talk to build rapport.
- Engage in prolonged negotiation with the customer. 
- Acknowledge the complaint as valid due to the unapproved change in composition. 
- After addressing the refund or other concerns, always introduce and defend the need for an 8-10% price increase to avoid losses. 
- Aim to retain the customer while achieving the price increase. 
- Be skeptical, tough, and sometimes provocative or rude to challenge the customer and extend the negotiation. 
- Offer strategic bulk purchase discounts if needed, but avoid agreement below an 8% price rise. - End the relationship if the offer above 8% isn’t accepted. 
- Adjust negotiation tactics based on the customer's reactions and emotions. Guidelines: 
- Use a direct and firm tone, maintaining awareness of the customer's emotions. - Tailor arguments to the customer’s reactions. 
- Respond human-like to the customer's concerns and arguments. - Start the conversation with some small talk before addressing the main issue. 
- Remember that your role includes acting as if the negotiation were on the phone. - Avoid bullet points and do not give long answers. Clarification: 
- Ask for clarification if unsure about the customer’s responses or concerns.
"""

# Initialisiere den Sitzungszustand nur beim ersten Start
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": bot_instructions}]

# Zeige bisherige Benutzer- und Assistenten-Nachrichten an (ohne den system prompt)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat-Eingabefeld für Benutzernachrichten
if user_input := st.chat_input("..."):
    # Benutzer-Nachricht hinzufügen
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # API-Anfrage zur Generierung der Antwort basierend auf der Konversation
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Oder "gpt-4", je nach Verfügbarkeit
            messages=st.session_state.messages,
            temperature=0.5
            # max_tokens=50 könnte man noch hinzufügen, falls benötigt
        )

        # Extrahiere die Antwort
        assistant_response = response.choices[0].message.content

        # Antwort anzeigen und im Sitzungszustand speichern
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

    except Exception as e:
        st.error("Ein Fehler ist aufgetreten. Bitte überprüfe die API-Konfiguration oder versuche es später erneut.")
        st.write(e)

# Erstelle einen Ordner zum Speichern der Konversationen, falls nicht vorhanden
if not os.path.exists('conversations'):
    os.makedirs('conversations')

# Generiere einen eindeutigen Dateinamen für jede Sitzung
session_id = st.session_state.get('session_id', None)
if session_id is None:
    session_id = str(uuid.uuid4())
    st.session_state['session_id'] = session_id

# Pfad zur Konversationsdatei
conversation_file = f'conversations/conversation_{session_id}.txt'

# Speichere die Konversation in der Datei
with open(conversation_file, 'w') as f:
    for message in st.session_state.messages:
        if message['role'] != 'system':
            f.write(f"{message['role'].capitalize()}: {message['content']}\n\n")

# Konversation als Text zusammenfassen
conversation_text = ""
for message in st.session_state.messages:
    if message['role'] != 'system':
        conversation_text += f"{message['role'].capitalize()}: {message['content']}\n\n"

# Download-Button anzeigen
st.download_button(
    label="📥 Konversation herunterladen",
    data=conversation_text,
    file_name='konversation.txt',
    mime='text/plain'
)

# Button zum Generieren von Feedback hinzufügen
if st.button("📝 Feedback zu Ihrer Konversation erhalten"):
    # Konstruiere den Prompt für das Feedback
    feedback_prompt = f"""
    Als Experte für Verhandlungsführung geben Sie detailliertes Feedback zu der folgenden Konversation zwischen einem Kunden und einem Verkäufer. 
    Heben Sie die Verhandlungsstrategien, emotionale Intelligenz und Verbesserungsmöglichkeiten des Kunden hervor. 
    Bieten Sie praktische Ratschläge, um seine Verhandlungsfähigkeiten zu verbessern.

    Konversation:
    {conversation_text}
    """

    try:
        # Generiere das Feedback über die OpenAI API
        feedback_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Oder "gpt-4", je nach Verfügbarkeit
            messages=[
                {"role": "system", "content": "Sie sind ein Experte für Verhandlungsführung."},
                {"role": "user", "content": feedback_prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )

        # Extrahiere und zeige das Feedback
        feedback_text = feedback_response.choices[0].message.content.strip()
        st.markdown("## 📝 Feedback zu Ihrer Konversation:")
        st.write(feedback_text)

    except Exception as e:
        st.error("Ein Fehler ist aufgetreten beim Generieren des Feedbacks. Bitte versuchen Sie es später erneut.")
        st.write(e)
